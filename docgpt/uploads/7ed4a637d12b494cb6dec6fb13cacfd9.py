import easyocr
import re

image_path = input("Enter the path to the input image: ")

reader = easyocr.Reader(['en', 'la']) # this needs to run only once to load the model into memory
data = reader.readtext(image_path)

formatted_output = '\n'.join([f"{entry[1]}" for entry in data])

print(formatted_output)
print("Wantedddddddddd")

formatted_text = re.sub(r'\n(?=[A-Z])', ' ', formatted_output)

print(formatted_text)

# Replace newline characters with spaces, except before a capital letter
formatted_text = re.sub(r'\n(?=[A-Z])', ' ', formatted_output)

# Replace newline characters between consecutive numbers with a space
formatted_text = re.sub(r'(\d)\n(\d)', r'\1 \2', formatted_text)

# print("Value found is ")

# print(formatted_text, type(formatted_text))

numbers = re.findall(r'\b\d(?: *\d){13,19}\b', formatted_text)

if numbers:
    print("Extracted Card Number is:")
    print(numbers[0].replace(' ', ''))
else:
    print("Sorry Coudlnt extract any")


