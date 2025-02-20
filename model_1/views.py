from django.shortcuts import render, redirect
from . import remote_ollama
from . import filter
from collections import deque
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from .models import Bussiness, Client, Chats  # Import the Bussiness model
from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from .url_safety import encrypt_data, decrypt_data
from cryptography.fernet import InvalidToken

# List of models
model_list = ['qwen-2.5-32b', 'qwen-2.5-coder-32b', 'deepseek-r1-distill-qwen-32b', 'deepseek-r1-distill-llama-70b', 'gemma2-9b-it', 'llama-3.1-8b-instant', 'llama-3.2-11b-vision-preview', 'llama-3.2-1b-preview', 'llama-3.2-3b-preview', 'llama-3.2-90b-vision-preview', 'llama-3.3-70b-specdec', 'llama-3.3-70b-versatile', 'llama-guard-3-8b', 'llama3-70b-8192', 'llama3-8b-8192', 'mixtral-8x7b-32768']

# Initialize instructions and conversation history
conversation_history = deque(maxlen=10)

def get_saved_business_apis():
    # Fetch all Bussiness models and extract the API keys
    businesses = Bussiness.objects.all()
    return [business.api_key for business in businesses]

def save_new_api_key(business_name, api_key, file, selected_model):
    new_business = Bussiness(
        bussiness_name=business_name,
        api_key=api_key,
        file=file,
        llm_model=selected_model
    )
    new_business.save()

def file_upload(request):
    # Retrieve session data if available
    api_keys = get_saved_business_apis()  # Fetch API keys from the Bussiness model
    instructions = request.session.get('instructions', [])
    in_use_model = request.session.get('in_use_model', 'llama-3.1-8b-instant')
    current_api = request.session.get('current_api', '')

    media_path = settings.MEDIA_ROOT  # Path to the media folder

    # Get a list of existing .txt files in the media folder
    existing_files = [file for file in os.listdir(media_path) if file.endswith('.txt')]

    if request.method == 'POST':
        # Handle file upload
        business_name = request.POST.get('bussiness_name')
        uploaded_file = request.FILES.get('uploaded_file')
        selected_file = request.POST.get('existing_file')
        selected_model = request.POST.get('selected_model')  # Get the selected model
        api_key = request.POST.get('api_key')  # Get the new API key
        existing_api_key = request.POST.get('existing_api_key')  # Get the selected API key

        if uploaded_file:
            file = uploaded_file
        elif selected_file:
            file = selected_file

        # Handle API key selection logic
        if existing_api_key:
            api_key = existing_api_key  # Use the selected API key
        elif not api_key:
            # If no API key is provided, return an error
            print("No API key provided.")
            return redirect('file_upload')  # Redirect back with an error message
        elif api_key:
            # If it's a new API key, save it and ensure only one API key exists
            save_new_api_key(business_name, api_key, file, selected_model)

        # Check if any of the values have changed and reset session data accordingly
        if selected_model != in_use_model or api_key != current_api:
            # Reset session data if new model or API key is provided
            request.session['instructions'] = []
            request.session['in_use_model'] = selected_model
            request.session['current_api'] = api_key

        # Handle the file selection or upload
        if uploaded_file:
            # If a new file is uploaded
            file_path = os.path.join(media_path, uploaded_file.name)
            if os.path.exists(file_path):
                print(f"File {uploaded_file.name} already exists.")
            else:
                fs = FileSystemStorage()
                filename = fs.save(uploaded_file.name, uploaded_file)
                file_path = os.path.join(media_path, filename)

            # Fine-tune with the newly uploaded file
            instructions = filter.fine_tune(file_path)

        elif selected_file:
            # If an existing file is selected
            file_path = os.path.join(media_path, selected_file)
            instructions = filter.fine_tune(file_path)

        # Update the session with new instructions and model
        request.session['instructions'] = instructions
        request.session['in_use_model'] = selected_model
        request.session['current_api'] = api_key

        # Redirect to home after processing (this will load the new session)
        print('before redirect')
        return redirect('index')

    # Render the page with existing files and models if it's not a POST request
    return render(request, 'model_1/upload_file.html', {
        'existing_files': existing_files,
        'model_list': model_list,
        'api_keys': api_keys,  # Pass the API keys fetched from the Bussiness model
        'current_api': current_api
    })


def home(request, encrypted_bussiness_name, encrypted_client_number):
    # Check if the client is logged in (i.e., check for session data)
    if not request.session.get('client_number') or not request.session.get('bussiness_name'):
        # If not logged in, redirect to login page with an error message
        messages.error(request, 'You need to log in first to access this page.')
        return redirect('client_login')

    # Decryption
    try:
        bussiness_name = decrypt_data(encrypted_bussiness_name)
        client_number = decrypt_data(encrypted_client_number)
    except InvalidToken:
        messages.error(request, 'The provided encrypted data is invalid or expired.')
        return redirect('client_login')

    # Retrieve the Bussiness object based on bussiness_name
    try:
        bussiness = Bussiness.objects.get(bussiness_name=bussiness_name)
    except Bussiness.DoesNotExist:
        messages.error(request, 'Business not found.')
        return redirect('client_login')

    # Retrieve the Client object for the provided client_number
    try:
        client = Client.objects.get(client_number=client_number, bussiness_name=bussiness)
    except Client.DoesNotExist:
        messages.error(request, 'Client not found.')
        return redirect('client_login')

    # Proceed with rendering the home page if logged in
    api_key = request.session.get('api_key', bussiness.api_key)
    file = request.session.get('file', bussiness.file)
    model = request.session.get('model', bussiness.llm_model)

    # Retrieve previous chat history from the database
    previous_chats = Chats.objects.filter(
        client_number=client_number,
        bussiness_name=bussiness
    ).order_by('time_of_chat')  # Order by time to display the chat in sequence
    
    conversation_history = [
        {'sender': 'User' if chat.is_client else 'Bot', 'text': chat.chat, 
         'identifier': client_number if chat.is_client else bussiness_name}
        for chat in previous_chats
    ]
    
    # Handle chat submission
    if request.method == 'POST':
        user_chat = request.POST.get('user_chat')  # Get the user's chat input

        if user_chat:  # If user chat exists
            # Send user message to bot and get response
            media_path = settings.MEDIA_ROOT
            file_path = os.path.join(media_path, file)
            instructions = filter.fine_tune(file_path)
            chat_history_for_model = [f"User: {chat.chat}" for chat in previous_chats if chat.is_client]
            chat_history_for_model_2 = []
            for i in chat_history_for_model:
                if i not in chat_history_for_model_2:
                    chat_history_for_model_2.append(i)

            chat_history_for_model = "\n".join([i for i in chat_history_for_model_2])
            bot_chat = remote_ollama.chat_bot(user_chat, instructions, model, api_key, chat_history_for_model)
            # Append user and bot messages to conversation history
            conversation_history.append({'sender': 'User', 'text': user_chat, 'identifier': client_number})
            conversation_history.append({'sender': 'Bot', 'text': bot_chat, 'identifier': bussiness_name})

            # Save user chat to the database
            Chats.objects.create(
                chat=user_chat,
                client_number=client_number,
                bussiness_name=bussiness,
                is_client=True,
                time_of_chat=timezone.now()  # Save the time of the chat
            )
            print(f'model = {model}')
            # Save bot chat to the database
            Chats.objects.create(
                chat=bot_chat,
                client_number=client_number,
                bussiness_name=bussiness,
                is_client=False,
                time_of_chat=timezone.now()  # Save the time of the chat
            )

            # Save conversation history to the session
            request.session['conversation_history'] = conversation_history
     # Encryption
    encrypt_bussiness_name = encrypt_data(bussiness_name)
    encrypt_client_number = encrypt_data(client_number)
    # Render home template with all necessary data
    return render(request, 'model_1/home.html', {
        'conversation': conversation_history,
        'client_number': encrypt_client_number,
        'bussiness_name': encrypt_bussiness_name,
        'api_key': api_key,
        'file': file,
        'model': model,
        # 'encrypted_bussiness_name':encrypt_bussiness_name,
        # 'encrypted_client_number':encrypt_client_number
    })



def exit_session(request):
    # Clear the session to end the current session
    request.session.flush()

    # Redirect the user back to the file upload page
    return redirect('index')

def index(request):
    return render(request, 'model_1/index.html')

def client_page(request):
    return render(request, 'model_1/client_page.html')

def get_saved_business_names():
    # Fetch all Bussiness models and extract the API keys
    businesses = Bussiness.objects.all()
    businesses_list = [business.bussiness_name for business in businesses]
    print(businesses_list)
    return businesses_list

def client_sign_up(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        business_name = request.POST.get('bussiness_name')  # Ensure correct field name here
        # Validation: Ensure phone number and business name are not empty and valid
        errors = []
        if not phone_number:
            errors.append('Phone number is required.')
        elif len(phone_number) < 10:  # Simple length check for valid phone number
            errors.append('Phone number must be at least 10 digits long.')
        
        if not business_name:
            errors.append('Business name is required.')

        if errors:
            business_names = get_saved_business_names()
            return render(request, 'model_1/client_sign_up.html', {'errors': errors, 'businesses': business_names})

        print(f'client = {phone_number} business = {business_name}')
        try:
            bussiness_instance = Bussiness.objects.get(bussiness_name=business_name)
        except Bussiness.DoesNotExist:
            # Handle the case where the Bussiness does not exist (optional)
            return render(request, "client_signup.html", {"errors": ["Business not found"]})
        # Save the client data
        new_client = Client(
                client_number=phone_number,
                bussiness_name=bussiness_instance
            )
        new_client.save()        
        # Redirect to the client page or a confirmation message
        return redirect('client_page')  # Ensure you have 'client_page' defined in your URLs

    # Get all business names for the form dropdown
    business_names = get_saved_business_names()
    print(f'bussiness list = {business_names}')
    return render(request, 'model_1/client_sign_up.html', {'businesses': business_names})

def get_client_data(client_number):
    client_data = {}
    try:
        client = Client.objects.get(client_number=client_number)  # Fetch the client based on client_number
        business = client.bussiness_name  # This is now a ForeignKey reference to the Bussiness model

        client_data['client_number'] = client.client_number
        client_data['bussiness_name'] = business.bussiness_name  # Access the bussiness_name attribute of the Bussiness model

        # Add business-related data
        client_data['api_key'] = business.api_key
        client_data['file'] = business.file
        client_data['model'] = business.llm_model

    except Client.DoesNotExist:
        client_data = None  # If no client is found, return None
    return client_data


def client_login(request):
    if request.method == 'POST':
        client_number = request.POST.get('phone_number')
        client_data = get_client_data(client_number)  # Fetch the client data
        
        if client_data:  # If client data is found
            # Store the details in the session
            request.session['client_number'] = client_data['client_number']
            request.session['bussiness_name'] = client_data['bussiness_name']
            request.session['api_key'] = client_data['api_key']
            request.session['file'] = client_data['file']
            request.session['model'] = client_data['model']
        
            

            # Redirect to home page with the necessary arguments
            bussiness_name = request.session.get('bussiness_name')
            client_number = request.session.get('client_number')

            # Encryption
            encrypt_bussiness_name = encrypt_data(bussiness_name)
            encrypt_client_number = encrypt_data(client_number)
            # Ensure both bussiness_name and client_number are available before redirecting
            if bussiness_name and client_number:
                return redirect('home', encrypted_bussiness_name=encrypt_bussiness_name, encrypted_client_number=encrypt_client_number)
            # Handle invalid client number (optional)
            return render(request, 'model_1/client_login.html', {'error': 'Client not found'})

    return render(request, 'model_1/client_login.html')

def Business_page(request):
    return render(request, 'model_1/Business_page.html')



def get_saved_business_names():
    businesses = Bussiness.objects.all()
    business_names = []
    for i in businesses:
        business_names.append(i.bussiness_name)
    return business_names
def Business_login(request):
    if request.method == 'POST':
        business_name = request.POST.get('business')
        return redirect('Business_dashboard', business_name=business_name)
    # Getting All business names
    businesses = get_saved_business_names()
    return render(request, 'model_1/Business_login.html', {'bussinesses' : businesses})


def get_business_details(business_name):
    clients = Client.objects.all()
    # Getting Client Names
    client_names = []
    api_key = ''
    for i in clients:
        if i.bussiness_name.bussiness_name == business_name:
            client_names.append(i.client_number)
            api_key = i.bussiness_name.api_key
            file = i.bussiness_name.file
            model = i.bussiness_name.llm_model
    return client_names, api_key, file, model
def Business_dashboard(request, business_name):
    client_names, api_key, file, model = get_business_details(business_name)
    return render(request, 'model_1/Business_dashboard.html', {'business_name':business_name,'clients' : client_names, 'api_key':api_key, 'file':file, 'llm_model':model})