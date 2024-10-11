from zhipuai import ZhipuAI
from scl_team_coder import glovar
from scl_team_coder.util.prompt_res_util import *
from scl_team_coder.util.agent_tools import *
from datetime import datetime

api_key = glovar.API_KEY_AIRX
client = ZhipuAI(api_key=api_key)
model="glm-4-arix"
dataset_path = "../../datesets/"
output_path = "../../output/glm/"
if not os.path.exists(output_path):
    os.makedirs(output_path)
    
def run(dateset="competition"):
    test_data = read_jsonl(dataset_path + f"{dateset}.json")
    with open("prompt","r") as fp:
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
        data['scl_code'] = parse_response(response)
        result.append(data)
        
    current_time = datetime.now()
    date_folder = current_time.strftime("%Y-%m-%d")
    time_folder = current_time.strftime("%H-%M-%S")
    with open(output_path + f"{date_folder}_{time_folder}.json") as fp:
        json.dump(result,fp,ensure_ascii=False)
    
run()