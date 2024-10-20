from zhipuai import ZhipuAI
from scl_team_coder import glovar
from scl_team_coder.util.prompt_res_util import *
from scl_team_coder.util.agent_tools import *
from datetime import datetime
from tqdm import tqdm  # 导入tqdm库
def run_glm(dataset="competition_en",prompt_file="prompt"):
    """
    使用智谱 AI 的 GLM 模型处理数据集并生成代码。

    参数:
        dataset (str): 要处理的数据集名称，默认为 "competition_en"。

    返回:
        None

    该函数执行以下操作：
    1. 设置 API 密钥。
    2. 创建智谱 AI 客户端。
    3. 指定要使用的模型。
    4. 构建提示文件和数据集文件的路径。
    5. 创建输出目录（如果不存在）。
    6. 读取数据集文件。
    7. 遍历数据集中的每个数据点。
    8. 为每个数据点创建一个包含系统提示和用户内容的消息。
    9. 将消息发送到 GLM 模型并获取响应。
    10. 从响应中提取代码。
    11. 将提取的代码添加到数据点中。
    12. 将处理后的数据点添加到结果列表中。
    13. 将结果列表保存到输出文件中。

    输出文件的名称基于当前日期和时间。
    """
    # 设置 API 密钥
    api_key = glovar.API_KEY_AIRX
    
    # 创建智谱 AI 客户端
    client = ZhipuAI(api_key=api_key)
    
    # 指定要使用的模型
    model = "glm-4-plus"
    
    # 构建提示文件和数据集文件的路径
    prompt_path = f"{glovar.EXPERIMENT_DIR}/baselines/glm/{prompt_file}"
    dataset_path = f"{glovar.EXPERIMENT_DIR}/datasets/"
    output_path = f"{glovar.EXPERIMENT_DIR}/output/{dataset}/glm/"
    
    # 打印数据集路径和输出路径
    print(dataset_path, output_path)
    
    # 如果输出路径不存在，则创建它
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # 读取数据集文件
    test_data = read_jsonl(dataset_path + f"{dataset}.jsonl")
    
    # 读取系统提示文件
    with open(prompt_path, "r") as fp:
        sys_prompt = fp.read()
    
   # 获取当前时间
    current_time = datetime.now()
    
    # 格式化日期和时间
    date_folder = current_time.strftime("%Y-%m-%d")
    time_folder = current_time.strftime("%H-%M-%S")
    
    # 构建输出文件路径
    output_to = f"{output_path}{date_folder}_{time_folder}.json"
    
    # 遍历数据集中的每个数据点
    for data in tqdm(test_data, desc=f"{model} Processing {dataset}"):
        # 为每个数据点创建一个包含系统提示和用户内容的消息
        response = client.chat.completions.create(
            model=model,  # 填写需要调用的模型名称
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": str(data)}
            ],
            max_tokens=4096,
        )
        
        # 从响应中提取文本内容
        response = response.choices[0].message.content
        
        # 从响应中提取代码
        data['code'] = parse_response(response)
        
        # 将处理后的数据点添加到结果文件中
        write_jsonl(data, output_to)

