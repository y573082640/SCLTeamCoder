import os
import glob
from openai import OpenAI
from scl_team_coder import glovar
from scl_team_coder.util.prompt_res_util import *
from scl_team_coder.util.agent_tools import *
from datetime import datetime
api_key = 'sk-heJMQX0Z4FEBm1ve7a5320F48f034fE688D104E53c2fBe45'
client = OpenAI(api_key=api_key,base_url=f"https://www.gptapi.us/v1")
model="gpt-4o"
# todo:生成过程逻辑错误
def load_prompt(repo="prompts"):
    prompt_path = f"{glovar.EXPERIMENT_DIR}/baselines/llm4plc/{repo}"
    prompt_dict = {}
    
    # 遍历prompt_path目录下的所有子目录
    for subdir in glob.glob(os.path.join(prompt_path, "*")):
        if os.path.isdir(subdir):  # 判断是否为子目录
            subdir_name = os.path.basename(subdir)  # 获取子目录名
            prompt_dict[subdir_name] = {}  # 初始化子目录字典
            
            # 遍历子目录中的文件
            for filepath in glob.glob(os.path.join(subdir, "*")):
                if os.path.isfile(filepath):
                    filename = os.path.basename(filepath)
                    # 读取文件内容并保存到嵌套字典中
                    with open(filepath, 'r', encoding='utf-8') as file:
                        prompt_dict[subdir_name][filename] = file.read()

    return prompt_dict
    
def call_gpt4(sys_prompt,content,max_tokens=2048,temperature=0.5):
    response = client.chat.completions.create(
        model = model,  # 填写需要调用的模型名称
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": str(content)}
        ],
    )
    response = response.choices[0].message.content
    return response
    
def syntax_check(st_code):
    ...
    
def call_smv(smv_code):
    ...
    
def pipeline(nl_task_requirements):
    sys_prompts = load_prompt()
    print(sys_prompts)
    return 
    # 一次性生成规划，没有人工参与
    plan = call_gpt4(sys_prompts["generate_plan"],nl_task_requirements)
    
    # 生成scl代码的loop
    loop_count = 0
    st_passed = False
    st_code = call_gpt4(sys_prompts["generate_st_code"],nl_task_requirements)
    st_passed,st_syntax_check_feedback = syntax_check(st_code)
    while st_passed is not True and loop_count<3:
        st_code = call_gpt4(sys_prompts["generate_st_code"],nl_task_requirements)
        st_passed,st_syntax_check_feedback = syntax_check(st_code)
        loop_count += 1
        
    # 生成smv代码loop
    loop_count = 0
    smv_passed = False
    smv_code = call_gpt4(sys_prompts["generate_smv_code"],plan)
    smv_passed,smv_syntax_check_feedback = call_smv(smv_code)
    while smv_passed is not True and loop_count<3:
        smv_code = call_gpt4(sys_prompts["generate_smv_code"],nl_task_requirements)
        smv_code,smv_syntax_check_feedback = call_smv(smv_code)
        loop_count += 1
    
    # 获取smv对plan的验证结果和st代码的语法结果并使用反馈信息重新生成st代码
    loop_count = 0
    smv_passed = False
    st_passed = False
    while (st_passed is not True or smv_passed is not True) and loop_count<3:
        smv_passed,smv_syntax_check_feedback = call_smv(smv_code)
        st_passed,st_syntax_check_feedback = syntax_check(st_code)
        st_code = call_gpt4(sys_prompts["generate_st_code_with_feedback"],smv_syntax_check_feedback+st_syntax_check_feedback+st_code+plan)
        loop_count += 1
    
    return smv_passed and st_passed,plan,st_code,smv_code
    
def run_llm4plc(dateset="competition"):
    dataset_path = f"{glovar.EXPERIMENT_DIR}/datasets/"
    output_path = f"{glovar.EXPERIMENT_DIR}/output/claude/"
    test_data = read_jsonl(dataset_path + f"{dateset}.jsonl")
    result = []
    for data in test_data:
        result.append(pipeline(str(data)))
        return 
    # 获取当前时间
    current_time = datetime.now()
    # 格式化日期和时间
    date_folder = current_time.strftime("%Y-%m-%d")
    time_folder = current_time.strftime("%H-%M-%S")
    # 构建输出文件路径
    with open(output_path + f"{date_folder}_{time_folder}.json", "w") as fp:
        # 将结果列表保存到输出文件中
        json.dump(result, fp, ensure_ascii=False)
