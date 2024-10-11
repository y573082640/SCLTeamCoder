import os
import json

def read_json_files_to_jsonl(directory):
    jsonl_data = []
    
    # Loop through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".json"):  # Check if the file is a JSON file
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding="utf-8 sig") as file:
                data = json.load(file)
                jsonl_data.append(data)  # Append the data to the list
    
    # Write the data to a JSONL file
    with open('competition.jsonl', 'w') as jsonl_file:
        for item in jsonl_data:
            jsonl_file.write(json.dumps(item,ensure_ascii=False) + "\n")
    
    return "competition.jsonl"

# Call the function and provide the current directory
output_file = read_json_files_to_jsonl('./competition')