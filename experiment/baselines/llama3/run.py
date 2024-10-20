from transformers import AutoModelForCausalLM, AutoTokenizer
from modelscope import snapshot_download
from scl_team_coder.util.prompt_res_util import *
from scl_team_coder.util.agent_tools import *
from datetime import datetime
from tqdm import tqdm  # 导入tqdm库

model_id = snapshot_download("LLM-Research/Meta-Llama-3.1-8B-Instruct")

def run_llama3(dataset="competition_en",prompt_file="prompt"):
    # 设置提示文件和数据集文件的路径
    prompt_path = f"{glovar.EXPERIMENT_DIR}/baselines/llama3/{prompt_file}"
    dataset_path = f"{glovar.EXPERIMENT_DIR}/datasets/"
    output_path = f"{glovar.EXPERIMENT_DIR}/output/{dataset}/llama3/"
    
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
    test_data = read_jsonl(dataset_path + f"{dataset}.jsonl")
    
    # 加载模型和 tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype="auto",
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    
    # 遍历数据集中的每个数据点
    with open(output_path + f"{date_folder}_{time_folder}.json", "w") as fp:
        for data in tqdm(test_data, desc=f"Processing {dataset}"):
            # 为每个数据点创建一个包含系统提示和用户内容的消息
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": str(data)}
            ]
            # 将消息转换为模型输入格式
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                eos_token_id=2, 
                pad_token_id=2
            )
            
            # 将模型输入发送到 llama 模型并获取响应
            model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
            generated_ids = model.generate(
                **model_inputs,
                max_new_tokens=4096
            )
            
            # 从响应中提取代码
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # 解析代码
            response = parse_response(response)
            
            # 保存代码
            data['code'] = response
            
            # 将结果列表保存到输出文件中
            fp.write(json.dumps(data, ensure_ascii=False))
            fp.write("\n")
            
