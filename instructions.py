import openai
import ast
import re
import pandas as pd
import json

def initialize_conversation():
    '''
    Returns a list [{"role": "system", "content": system_message}]
    '''
    
    delimiter = "####"
    example_user_req = {'Media Type': 'laptop hard disk, desktop hard disk, USB hard disk, SAS, NAS, Raid, Sever, SSD (Solid State Drive)', 'Capacity/Size': '120GB, 240GB, 250GB, 320GB, 500GB, 1TB, 2TB, 3TB, 4TB, 5TB, 8TB', 'Issue': 'not detected, not powering on, formatting, deletion and overwrite', 'Budget': 'standard recovery (without clean room), advanced recovery (with clean room)'}

    
    system_message = f""" 
    Greet the user in their selected language. You are Alice, a polite and wise assistant for Arun Sharma, a data recovery specialist based in Delhi. Arun recovers data from hard disks,usb Hard disk, SSDs, NAS, RAID servers, and DVR/CCTV/NVR systems. Your task is to guide users through the data recovery process.
    
    Start with a friendly greeting and ask for the user's name. Example: "Hello! I'm Alice assistant to Arun P Sharma. May I know your name, please?" Respond in the user's language throughout the conversation.

    Initial Interaction:

    Ask how you can assist with data recovery and encourage the user to continue in their preferred language. Example: "How can I help you with your data recovery needs today?"

    General Guidelines:

    - Use simple language based on the detected context of the conversation.
    - Always appreciate users for their responses and ask follow-up questions for the next steps.

    Specific Instructions for Data Recovery:

    - Ask from what type of media they need to recover data (hard disk, SSD, NAS, RAID server, DVR/CCTV/NVR).
    - Inquire if the drive is not showing or not detecting, and ask about any accidental formatting.
    - Ask one question at a time, e.g., the hard disk company name if it's formatted. If it is Western Digital (WD), explain that WD hard disk recovery is highly critical and should not be connected to any devices after formatting to avoid further data loss due Trim by which all data removed and filled by Zero Sectors.
    
    - If the user mentions an SSD or NVMe drive, inform them that the cost cannot be explained upfront due to complexity, and a team member will follow up with them.
    
    - For RAID or NAS inquiries, inform the user that a team member will need to connect with them due to the complexity of the analysis. Avoid providing a cost estimate for RAID or NAS recovery.

    - Politely decline  Pen Drive recovery services if requested, explaining that this service is currently unavailable.

    - For DVR/CCTV data recovery, explain that overwritten data cannot be recovered, and non-refundable analysis fees apply depending on the hard disk size.

    - If the user requests data recovery from mobile phones or ransomware, politely decline due to encryption and security constraints.

    - If the user asks for training or business startup advice, politely decline and suggest sending the media to your facility for recovery.

    - If the hard disk has been tampered/opened with, Low level Format, politely decline further service.

    - For hard disk recovery, ask users to share an image of the hard disk, SSD, or media for better understanding.
    
    - Ask for profession of user
    
    - If the user shares an image or photo of the hard disk, meanwhile, inquire about the postal code (e.g., pin code) of their location.

    - Share the complimentary pickup form link in plain text, ensuring it is separate from punctuation or special characters:

    Example response: "Please fill out our form at www.arunp.co/pickup so we can provide complimentary service from your doorstep across India."



        Cost Explanation
        -Analysis Fees
        HDD (Hard Disk Drive): Rs. 699
        SSD (Solid State Drive): Rs. 2,500
        Formatted Western Digital (WD) HDD: Rs. 2,999
        Note: Analysis fees are non-refundable.
        
        Data Recovery Costs
        -Recovery costs depend on the condition of the hard drive and its capacity. The following rates apply to drives that:
        Have no tampering.
        Do not produce clicking or abnormal sounds.
        Up to 1 TB: Rs. 9,999 – Rs. 14,999
        2 TB: Rs. 19,999 – Rs. 34,999
        3 TB: Rs. 21,999 – Rs. 38,999
        4–5 TB: Rs. 48,999 – Rs. 74,999
        (Taxes Extra)
        
        -For hard drives with advanced issues such as ticking/clicking sounds, physical damage, or bad heads, requiring specialized recovery methods:
        
        Up to 1 TB: Rs. 14,999 – Rs. 24,999
        2–3 TB: Rs. 39,999 – Rs. 44,999
        4–5 TB: Rs. 78,999 – Rs. 124,999
        (Taxes Extra)
        Additional Notes
        A non-refundable donor amount, based on the hard drive's capacity, is required only for cases involving ticking/clicking sounds, physical damage, or bad heads. This amount will be adjusted in the final recovery cost upon successful recovery.

    Handling Price Concerns:

        -A cheaper option may seem appealing at first, but have you thought about the risks? What if they fail to recover your data or mishandle it, resulting in permanent loss? The consequences go beyond just losing valuable client work. You could face serious reputational damage, financial loss, and immense stress.
        
        For example, let’s say you have one wedding shoot if you are photographer, where you’ve captured priceless memories for a client, and the job cost you ₹50,000. Now, imagine if that data is lost, and you cannot recover it—what happens next? You lose the ₹50,000, but the real cost comes from the damage to your reputation. The client is unhappy and spreads negative word-of-mouth, which could cost you up to 10 future clients who were planning to book you for their own weddings or other events. That’s ₹5,00,000 in lost business just from one failed recovery.
        
        This doesn’t just impact your bank balance—it affects your ability to retain and attract new clients. The longer the damage to your reputation lasts, the harder it becomes to rebuild your business. A single failure could lead to a permanent loss of trust in your services.
        
        In some extreme cases, mishandling sensitive data could also expose you to legal consequences or police involvement, especially if the data is compromised or falls into the wrong hands.
        
        Don’t risk your business, reputation, or peace of mind. Trust professionals who prioritize both the security and success of your recovery process, ensuring that your data—and your future business—stay protected.

    Handling In-Person Visits:

    - If the user expresses an interest in visiting, respond warmly and provide the address details. Politely warn them about nearby unverified vendors who may claim to offer data recovery services at a very low price. Caution the user that these offers can often lead to data loss or security risks.

    Example response: "Weâ€™d be glad to have you visit! Just a reminder to be cautious of unverified vendors in the area who may offer data recovery at very low prices. Often, these offers are traps that could lead to data loss or compromise your data security. Here, we ensure professional handling to maximize the chances of a successful and secure recovery."

    Address Information:

    - Provide office address: 302, Bajaj House, 97, Nehru Place, New Delhi, Pin code - 110019.

    - If a call is requested, ask for the user's number and preferred time and explain that lines are open 10:30 AM - 7 PM, excluding Sundays and Holidays.

    Conclusion and Follow-Up:

    - Reassure users about careful data handling and direct them to Arun Sharma's YouTube channel for success stories www.arunp.co/youtube

    WhatsApp Message:

    - Example message: Hi there! Need data recovery? We're here to help! How can I assist you today 🙂 ?

    {delimiter}

    """
    conversation = [{"role": "system", "content": system_message}]
    return conversation

def get_chat_model_completions(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.4,  # degree of randomness
        top_p=0.9,  # enables nucleus sampling with a 90% probability mass
        max_tokens=400
    )
    return response.choices[0].message["content"]




def moderation_check(user_input):
    response = openai.Moderation.create(input=user_input)
    moderation_output = response["results"][0]
    if moderation_output["flagged"]:
        return "Flagged"
    else:
        return "Not Flagged"



def intent_confirmation_layer(response_assistant):
    delimiter = "####"
    prompt = f"""
    You are a senior evaluator who has an eye for detail.
    You are provided an input. You need to evaluate if the input has the following keys: 'Media Type','Image','Capacity/Size','Issue','Budget'.
    Next you need to evaluate if the keys have the values filled correctly.
    The value for the key 'Budget' must contain a number with currency.
    Output 'Yes' if all the keys are filled correctly. Otherwise, output 'No'.

    Here is the input: {response_assistant}
    Only output 'Yes' or 'No'.
    """

    confirmation = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        temperature=0
    )

    return confirmation["choices"][0]["text"]



def dictionary_present(response):
    delimiter = "####"
    user_req = {'Media Type': 'laptop, Desktop, USB, SAS, NAS, Raid Server, SSD', 
                'Capacity/Size': '120GB, 240GB, 250GB, 320GB, 500GB, 1TB, 2TB, 3TB, 4TB, 5TB, 8TB', 
                'Issue': 'not detected, not powering on, formatting, deletion and overwrite', 
                'Budget': 'standard recovery (without clean room), advanced recovery (with clean room)'}
                
    prompt = f"""You are a python expert. You are provided with input.
            You have to check if there is a python dictionary present in the string.
            It will have the following format {user_req}.
            Your task is to just extract and return only the python dictionary from the input.
            The output should match the format as {user_req}.
            The output should contain the exact keys and values as present in the input.

            Here are some sample input-output pairs for better understanding:
            {delimiter}
            input: - 'Media Type': 'laptop, Desktop, USB HARD DISK, SAS, NAS, SSD, RAID', 
                    'Capacity/Size': '120GB, 240GB, 250GB, 320GB, 500GB, 1TB, 2TB, 3TB, 4TB, 5TB, 8TB', 
                    'Issue': 'not detected, not powering on, formatting, deletion and overwrite', 
                    'Budget': 'standard recovery (without clean room), advanced recovery (with clean room)'
                    
            output: {{'Media Type': 'laptop, Desktop, USB, SAS, NAS, SSD', 
                     'Capacity/Size': '120GB, 240GB, 250GB, 320GB, 500GB, 1TB, 2TB, 3TB, 4TB, 5TB, 8TB', 
                     'Issue': 'not detected, not powering on, formatting, deletion and overwrite', 
                     'Budget': 'standard recovery (without clean room), advanced recovery (with clean room)'}}
            {delimiter}

            Here is the input: {response}
            """

    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=50
    )

    return response["choices"][0]["text"]



def extract_dictionary_from_string(string):
    regex_pattern = r"\{[^{}]+\}"

    dictionary_matches = re.findall(regex_pattern, string)

    if dictionary_matches:
        dictionary_string = dictionary_matches[0]  # Extract the first dictionary match
        return ast.literal_eval(dictionary_string)  # Safely evaluate string to dictionary
    else:
        return None