import ollama

client = ollama.Client()

model = 'calisthenics_bot:latest'

def chat(user_input):
    prompt = user_input    
    response = client.generate(model=model, prompt=prompt)
    return response.response