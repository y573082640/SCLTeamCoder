import os
from anthropic import Anthropic
from scl_team_coder import glovar
from scl_team_coder.util.prompt_res_util import *
from scl_team_coder.util.agent_tools import *
from datetime import datetime

def run_claude(dateset="competition"):
    """
    使用 Anthropic 的 Claude 模型处理数据集并生成代码。

    参数:
        dateset (str): 要处理的数据集名称，默认为 "competition"。

    返回:
        None

    该函数执行以下操作：
    1. 设置 API 密钥和基础 URL。
    2. 指定要使用的模型。
    3. 构建提示文件和数据集文件的路径。
    4. 创建输出目录（如果不存在）。
    5. 读取数据集文件。
    6. 遍历数据集中的每个数据点。
    7. 为每个数据点创建一个包含系统提示和用户内容的消息。
    8. 将消息发送到 Claude 模型并获取响应。
    9. 从响应中提取代码。
    10. 将提取的代码添加到数据点中。
    11. 将处理后的数据点添加到结果列表中。
    12. 将结果列表保存到输出文件中。

    输出文件的名称基于当前日期和时间。
    """
    # 设置 API 密钥和基础 URL
    api_key = glovar.GPT_API_KEY
    client = Anthropic(api_key=api_key, base_url=f"https://www.gptapi.us")
    
    # 指定要使用的模型
    model = "claude-3-5-sonnet"
    
    # 构建提示文件和数据集文件的路径
    prompt_path = f"{glovar.EXPERIMENT_DIR}/baselines/claude/prompt"
    dataset_path = f"{glovar.EXPERIMENT_DIR}/datasets/"
    output_path = f"{glovar.EXPERIMENT_DIR}/output/{dateset}/claude/"
    
    # 打印数据集路径和输出路径
    print(dataset_path, output_path)
    
    # 如果输出路径不存在，则创建它
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # 读取数据集文件
    test_data = read_jsonl(dataset_path + f"{dateset}.jsonl")
    
    # 读取系统提示文件
    with open(prompt_path, "r") as fp:
        sys_prompt = fp.read()
    
    # 初始化结果列表
    result = []
    
    # 遍历数据集中的每个数据点
    for data in test_data:
        # 为每个数据点创建一个包含系统提示和用户内容的消息
        response = client.messages.create(
            model=model,  # 填写需要调用的模型名称
            max_tokens=2048,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": str(data)}
            ],
        )
        
        # 从响应中提取文本内容
        response = response.content[0].text
        
        # 打印响应内容
        print(response)
        
        # 从响应中提取代码
        data['scl_code'] = parse_response(response)
        
        # 将处理后的数据点添加到结果列表中
        result.append(data)
    
    # 获取当前时间
    current_time = datetime.now()
    
    # 格式化日期和时间
    date_folder = current_time.strftime("%Y-%m-%d")
    time_folder = current_time.strftime("%H-%M-%S")
    
    # 构建输出文件路径
    with open(output_path + f"{date_folder}_{time_folder}.json", "w") as fp:
        # 将结果列表保存到输出文件中
        json.dump(result, fp, ensure_ascii=False)
