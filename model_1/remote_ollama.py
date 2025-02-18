from groq import Groq
import logging

def chat_bot(user_chat, instructions, model_type, api_key_user, chat_history):
    print(chat_history)
    # Define the API key
    api_key = api_key_user
    client = Groq(api_key=api_key)
# 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
# calimove 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
# noa man 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
    # Define system instructions
    instructions_list_2 = [
        "Make the response short and summarized.",
        "If the user asks anything outside of this information, you should politely say: 'Sorry, I can't answer that.'",
        "Your responses should be concise, friendly, and respectful. If you don't know the answer based on the provided information, always guide the conversation back to the known facts.",
        "Remember, only respond with the information you have, and never make up details.",
        "When in doubt, politely decline by saying 'Sorry, I can't answer that.'"
    ]

    # Limit the instructions length to avoid unnecessary processing
    instructions_list_1 = instructions[:145] if len(instructions) > 145 else instructions

    # System instructions
    system_instructions = """
        You are a Llama bot designed to engage in a conversation based on a user's provided information.
        You should respond to questions about the following:
    """ 
    # using previous chats
    system_instructions = f"Previous conversation:\n{chat_history}\n"
    system_instructions += '\n' + '\n'.join(instructions_list_1)
    system_instructions += '\n' + '\n'.join(instructions_list_2)

    try:
        # Make the API call to get the response from the chat model
        completion = client.chat.completions.create(
            model=model_type,
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


