import transformers
import torch
from modelscope import snapshot_download
from scl_team_coder.util.prompt_res_util import *
from scl_team_coder.util.agent_tools import *
from datetime import datetime

model_id = snapshot_download("LLM-Research/Meta-Llama-3.1-8B-Instruct")

# todo:生成过程逻辑错误

def run_llama3(dateset="competition"):
    # 设置提示文件和数据集文件的路径
    prompt_path = f"{glovar.EXPERIMENT_DIR}/baselines/llama3/prompt"
    dataset_path = f"{glovar.EXPERIMENT_DIR}/datasets/"
    output_path = f"{glovar.EXPERIMENT_DIR}/output/{dateset}/llama3/"
    
    # 读取系统提示文件
    with open(prompt_path,"r") as fp:
        sys_prompt = fp.read()    
    # 获取当前时间
    current_time = datetime.now()
    
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
    
    pipeline = transformers.pipeline(
        "text-generation",
        model=model_id,
        model_kwargs={"torch_dtype": torch.bfloat16},
        device_map="auto",
    )
    # 遍历数据集中的每个数据点
    for data in test_data:
        # 为每个数据点创建一个包含系统提示和用户内容的消息
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": str(data)}
        ]
        outputs = pipeline(
            messages,
            max_new_tokens=2048,
            eos_token_id=2, 
            pad_token_id=2
        )
        response = outputs[0]["generated_text"][-1]['content']
        response = parse_response(response)
        data['code'] = response
        print(response)
        result.append(data)
