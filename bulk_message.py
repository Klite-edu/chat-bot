user_input = '250 Box'
num_part = ''
text_part = ''
for i in user_input:
    if i.isnumeric():
        num_part += i
    elif i == ' ':
        pass
    else:
        text_part += i
        
num_part = int(num_part)
num_part -= 100
final_text = str(num_part) +' ' + text_part
print(final_text)