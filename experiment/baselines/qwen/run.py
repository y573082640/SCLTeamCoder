from transformers import AutoModelForCausalLM, AutoTokenizer
from scl_team_coder.util.prompt_res_util import *
from scl_team_coder.util.agent_tools import *
from datetime import datetime

def run_qwen(dateset="competition"):
    """
    使用 Qwen 模型处理数据集并生成代码。

    参数:
        dateset (str): 要处理的数据集名称，默认为 "competition"。

    返回:
        None

    该函数执行以下操作：
    1. 设置提示文件和数据集文件的路径。
    2. 指定要使用的模型名称。
    3. 构建输出目录（如果不存在）。
    4. 读取数据集文件。
    5. 遍历数据集中的每个数据点。
    6. 为每个数据点创建一个包含系统提示和用户内容的消息。
    7. 将消息转换为模型输入格式。
    8. 将模型输入发送到 Qwen 模型并获取响应。
    9. 从响应中提取代码。
    10. 将提取的代码添加到数据点中。
    11. 将处理后的数据点添加到结果列表中。
    12. 将结果列表保存到输出文件中。

    输出文件的名称基于当前日期和时间。
    """
    # 设置提示文件和数据集文件的路径
    prompt_path = f"{glovar.EXPERIMENT_DIR}/baselines/qwen/prompt"
    dataset_path = f"{glovar.EXPERIMENT_DIR}/datasets/"
    output_path = f"{glovar.EXPERIMENT_DIR}/output/{dateset}/qwen/"
    
    # 获取当前时间
    current_time = datetime.now()
    
    # 读取系统提示文件
    with open(prompt_path,"r") as fp:
        sys_prompt = fp.read()
    
    # 构建日期和时间文件夹
    date_folder = current_time.strftime("%Y-%m-%d")
    time_folder = current_time.strftime("%H-%M-%S")
    
    # 如果输出路径不存在，则创建它
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # 读取数据集文件
    test_data = read_jsonl(dataset_path + f"{dateset}.jsonl")
    
    # 初始化结果列表
    result = []
    
    # 指定要使用的模型名称
    model_name = "Qwen/Qwen2.5-Coder-7B-Instruct"
    
    # 加载模型和 tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # 遍历数据集中的每个数据点
    for data in test_data:
        # 为每个数据点创建一个包含系统提示和用户内容的消息
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": str(data)}
        ]
        
        # 将消息转换为模型输入格式
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # 将模型输入发送到 Qwen 模型并获取响应
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=2048
        )
        
        # 从响应中提取代码
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        # 打印响应内容
        print(response)
        
        # 将提取的代码添加到数据点中
        data['code'] = parse_response(response)
        
        # 将处理后的数据点添加到结果列表中
        result.append(data)
    
    # 将结果列表保存到输出文件中
    with open(output_path + f"{date_folder}_{time_folder}.json") as fp:
        json.dump(result,fp,ensure_ascii=False)
