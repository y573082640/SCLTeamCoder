import os
import re
import json

def extract_blocks_from_file(file_path, output_dir, counter):
    with open(file_path, 'r') as file:
        content = file.read()

    pattern = re.compile(r'(FUNCTION_BLOCK\s+"?(\w+)"?.*?END_FUNCTION_BLOCK|FUNCTION\s+"?(\w+)"?.*?END_FUNCTION)', re.DOTALL)
    matches = pattern.findall(content)

    for match in matches:
        block_content, fb_name, func_name = match
        block_name = fb_name or func_name
        block_file_name = f'{block_name}.scl'
        with open(os.path.join(output_dir, block_file_name), 'w') as output_file:
            output_file.write(block_content)

def extract_blocks_from_directory(directory_path):
    output_dir = 'new'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    counter = 0
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.scl'):
                file_path = os.path.join(root, file)
                counter = extract_blocks_from_file(file_path, output_dir, counter)

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
    functions_dict = {}
    all_used_functions = []
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.scl'):
                block_file_path = os.path.join(root, file)
                with open(block_file_path, 'r') as block_file:
                    block_content = block_file.read()
                    functions = extract_functions_from_block(block_content)
                    functions_dict[file] = functions
                    all_used_functions += functions
    functions_dict['all_used_functions'] = list(set(all_used_functions))
    return functions_dict

if __name__ == '__main__':
    input_directory_path = './'  # 修改为包含.scl文件的目录路径
    extract_blocks_from_directory(input_directory_path)
    
    output_directory_path = 'exp'
    functions_dict = extract_functions_from_blocks(output_directory_path)

    with open('functions_usage.json', 'w') as json_file:
        json.dump(functions_dict, json_file, indent=4)

    print('Functions extracted and saved to functions_usage.json')
