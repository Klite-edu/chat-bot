from groq import Groq
import logging

def chat_bot(user_chat):
    # Define the API key
    api_key = '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'
    client = Groq(api_key=api_key)
# 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
# calimove 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
# noa man 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
    # Define system instructions
    

    # Limit the instructions length to avoid unnecessary processing

    # System instructions
    system_instructions = """
        You are a Llama bot designed to engage in a conversation based on a user's provided information.
        You should respond to questions about the following:
    """ 
   

    try:
        # Make the API call to get the response from the chat model
        completion = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[{"role": "system", "content": system_instructions}, {"role": "user", "content": user_chat}],
            temperature=1,
            max_completion_tokens=512,  # Reduced token length for faster response
            top_p=1,
            stream=False, 
        )

        # Return the response content
        return completion.choices[0].message.content
    
    except Exception as e:
        # Log the error for debugging purposes
        logging.error(f"Error during API request: {str(e)}")
        # Return a user-friendly error message
        return "Sorry, there was an issue with the service. Please try again later."
