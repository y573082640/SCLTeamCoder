import os
import re

def remove_change_log(input_dir, output_dir):
    for filename in os.listdir(input_dir):
        if filename.endswith(".scl"):
            file_path = os.path.join(input_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Regex to match and remove Change log table
            pattern = re.compile(r'(//[\s\S]*?)(//\s*Change log table:[\s\S]*?)(//\s*=============================================================================)')
            new_content = pattern.sub(r'\1\3', content)

            with open(output_dir, 'w', encoding='utf-8') as file:
                file.write(new_content)

if __name__ == '__main__':
    inputs = './extracted_blocks'  # Replace with your directory path
    outputs = './new'
    remove_change_log(input_dir=inputs, output_dir=outputs)
    print('success.')
