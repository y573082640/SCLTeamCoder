import os
from anthropic import Anthropic
from scl_team_coder import glovar
from scl_team_coder.util.prompt_res_util import *
from scl_team_coder.util.agent_tools import *
from datetime import datetime

def run_claude(dateset="competition"):
    api_key = 'sk-heJMQX0Z4FEBm1ve7a5320F48f034fE688D104E53c2fBe45'
    client = Anthropic(api_key=api_key,base_url=f"https://www.gptapi.us")
    model="claude-3-5-sonnet"
    prompt_path = f"{glovar.EXPERIMENT_DIR}/baselines/claude/prompt"
    dataset_path = f"{glovar.EXPERIMENT_DIR}/datasets/"
    output_path = f"{glovar.EXPERIMENT_DIR}/output/claude/"
    print(dataset_path,output_path)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    test_data = read_jsonl(dataset_path + f"{dateset}.jsonl")
    with open(prompt_path,"r") as fp:
        sys_prompt = fp.read()
    result = []
    for data in test_data:
        response = client.messages.create(
            model = model,  # 填写需要调用的模型名称
            max_tokens=1024,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": str(data)}
            ],
        )
        response = response.content[0].text
        print(response)
        data['scl_code'] = parse_response(response)
        result.append(data)
    current_time = datetime.now()
    date_folder = current_time.strftime("%Y-%m-%d")
    time_folder = current_time.strftime("%H-%M-%S")
    with open(output_path + f"{date_folder}_{time_folder}.json","w") as fp:
        json.dump(result,fp,ensure_ascii=False)