from django.conf import settings
import os

def fine_tune(file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()        
        # Removing unwanted signs
        text = text.replace('[', '')
        text = text.replace(']', '')
        for i in range(0, 10, 1):
            text = text.replace(str(i), '')

        instructions = []
        new_line = ''
        for i in text:
            if not(i == '.'):
                new_line += i
            else:
                instructions.append(new_line)
                new_line = ''
        return instructions
        
        
    else:
        print(f"File '{file_name}' not found.")
