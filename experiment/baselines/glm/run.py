from zhipuai import ZhipuAI
from scl_team_coder import glovar
from scl_team_coder.util.prompt_res_util import *
from scl_team_coder.util.agent_tools import *
from datetime import datetime

def run_glm(dateset="competition"):
    api_key = glovar.API_KEY_AIRX
    client = ZhipuAI(api_key=api_key)
    model="glm-4-airx"
    prompt_path = f"{glovar.EXPERIMENT_DIR}/baselines/glm/prompt"
    dataset_path = f"{glovar.EXPERIMENT_DIR}/datasets/"
    output_path = f"{glovar.EXPERIMENT_DIR}/output/glm/"
    print(dataset_path,output_path)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    test_data = read_jsonl(dataset_path + f"{dateset}.jsonl")
    with open(prompt_path,"r") as fp:
        sys_prompt = fp.read()
    result = []
    for data in test_data:
        response = client.chat.completions.create(
            model = model,  # 填写需要调用的模型名称
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": str(data)}
            ],
        )
        response = response.choices[0].message.content
        print(response)
        data['scl_code'] = parse_response(response)
        result.append(data)
    current_time = datetime.now()
    date_folder = current_time.strftime("%Y-%m-%d")
    time_folder = current_time.strftime("%H-%M-%S")
    with open(output_path + f"{date_folder}_{time_folder}.json","w") as fp:
        json.dump(result,fp,ensure_ascii=False)