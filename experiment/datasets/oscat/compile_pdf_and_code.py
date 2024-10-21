import os
import json

# 定义文件路径
input_json_dir = 'oscat_with_llm_description'          # 原始 JSON 文件目录
description_dir = 'oscat_raws/processed' # 存储 description 的文件目录
output_json_dir = 'oscat_with_mixed_describtion'          # 输出修改后的 JSON 文件目录

# 确保输出目录存在
os.makedirs(output_json_dir, exist_ok=True)

def update_json_descriptions():
    cnt = 0
    # 遍历 lgf_zh/ 目录下的所有 .json 文件
    for json_filename in os.listdir(input_json_dir):
        if json_filename.endswith(".json"):
            json_path = os.path.join(input_json_dir, json_filename)
            cnt += 1
            # 构造对应的 description 文件路径
            description_filename = os.path.splitext(json_filename)[0]  # 获取文件名（去掉.json后缀）
            description_path = os.path.join(description_dir, description_filename)
            description_path += ".txt"
            # 读取 description 文件内容
            try:
                with open(description_path, 'r', encoding='utf-8') as desc_file:
                    description_content = desc_file.read().strip()  # 读取 description 文件内容
            except FileNotFoundError:
                print(f"描述文件 {description_path} 未找到，跳过该 JSON 文件。")
            
            # 读取 JSON 文件
            with open(json_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)  # 解析 JSON 文件
            
            # 更新 JSON 文件中的 description 字段
            data['description'] = description_content
            
            # 移除中文部分
            if "description_zh" in data:
                del data['description_zh']
                
            # 构造输出路径
            output_json_path = os.path.join(output_json_dir, json_filename)
            
            # 将更新后的 JSON 写回到 lgf_en/ 目录
            with open(output_json_path, 'w', encoding='utf-8') as output_file:
                json.dump(data, output_file, ensure_ascii=False, indent=4)  # 写入 JSON 文件，保持格式化
            
            # print(f"{json_filename} 已更新并保存到 {output_json_path}")
    
    print(cnt)
# 调用函数进行操作
update_json_descriptions()
