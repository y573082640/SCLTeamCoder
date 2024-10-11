from transformers import AutoModelForCausalLM, AutoTokenizer
from scl_team_coder.util.prompt_res_util import *
from scl_team_coder.util.agent_tools import *
from datetime import datetime

dataset_path = "../../datesets/"
output_path = "../../output/gpt/"
current_time = datetime.now()
date_folder = current_time.strftime("%Y-%m-%d")
time_folder = current_time.strftime("%H-%M-%S")
if not os.path.exists(output_path):
    os.makedirs(output_path)
    
def run(dateset="competition"):
    test_data = read_jsonl(dataset_path + f"{dateset}.json")
    with open("prompt","r") as fp:
        sys_prompt = fp.read()
    result = []
    model_name = "Qwen/Qwen2.5-Coder-7B-Instruct"
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    for data in test_data:
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": str(data)}
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=2048
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        data['scl_code'] = parse_response(response)
        result.append(response)
        
    with open(output_path + f"{date_folder}_{time_folder}.json") as fp:
        json.dump(result,fp,ensure_ascii=False)
        
        
run()
