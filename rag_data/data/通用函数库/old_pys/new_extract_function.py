import os
import re
import json
def extract_instruction_name():
    instruction_names = []  # 初始化一个列表来存储所有的指令名
    dic = "../指令库/all_InstructionJSONFormat_165.jsonl"
    with open(dic, 'r', encoding='utf-8') as file:
    # 解析文件中的 JSON 数据
        for line in file:  # 逐行读取
            instruction = json.loads(line)  # 解析每一行的JSON数据
            instruction_name = instruction.get('指令名')  # 使用get以避免KeyError
            if instruction_name is not None:  # 确保指令名存在
                instruction_names.append(instruction_name)
    return instruction_names
def foreachLGF(keywords, file_keywords):
    folder_path = './new'
    files = os.listdir(folder_path)
    # 遍历文件列表
    all_functions = []
    for filename in files:
        # 获取文件的完整路径
        file_path = os.path.join(folder_path, filename)
        # 确保是文件而不是目录
        if os.path.isfile(file_path):
            # 打开文件并读取内容
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # 这里你可以添加代码来处理或提取文件内容
                # print(f"文件名: {filename}")
                found_keywords = [keyword for keyword in keywords if keyword in content]
                for keyword in found_keywords:
                    if keyword not in file_keywords[filename[:-4]]:
                        file_keywords[filename[:-4]].append(keyword)
                for keyword in file_keywords[filename[:-4]]:
                    if keyword not in all_functions:
                        all_functions.append(keyword)
    file_keywords["all_used_functions"] = all_functions
    # print("\n -------------- \n")
    # print(file_keywords)
    json_string = json.dumps(file_keywords, indent=4)
    print(json_string)
    with open ("new_functions_usage.json", "w", encoding = 'utf-8') as file:
        file.write(json_string)

def extract_functions_from_block(block_content):
    # 定义一个正则表达式来匹配函数调用，确保函数名后面紧跟着括号
    pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\('    
    # 初始化一个列表来存储所有提取到的函Z数名
    functions = []

    # 定义一个递归函数来处理嵌套结构
    def recursive_extract(text):
        matches = re.finditer(pattern, text)
        for match in matches:
            # 提取函数名并添加到列表中
            functions.append(match.group(1))
            # 找到匹配的括号内部内容进行递归处理
            start = match.end()  # 括号内部的起始位置
            depth = 1
            for i in range(start, len(text)):
                if text[i] == '(':
                    depth += 1
                elif text[i] == ')':
                    depth -= 1
                    if depth == 0:
                        inner_text = text[start:i]
                        recursive_extract(inner_text)
                        break

    # 开始递归提取
    recursive_extract(block_content)

    # 去重和LGF（特判一个奇怪的东西）
    ret = set(functions)
    ret.discard('LGF') 
    return list(ret)

def extract_functions_from_blocks(output_dir):
    folder_path = './new'
    files = os.listdir(folder_path)
    # 遍历文件列表
    file_keywords = {}
    all_functions = []
    for filename in files:
        # 获取文件的完整路径
        file_path = os.path.join(folder_path, filename)
        # 确保是文件而不是目录
        if os.path.isfile(file_path) and filename.endswith('.scl'):
            # 打开文件并读取内容
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                functions = extract_functions_from_block(content)
                file_keywords[filename[:-4]] = functions
    return file_keywords

if __name__ == '__main__':
    output = './new_functions_usage.json'
    output_directory_path = '../scl_case_code_modified'
    file_keywords = extract_functions_from_blocks(output_directory_path)
    keywords = extract_instruction_name()
    foreachLGF(keywords, file_keywords)