import os
import glob
from openai import OpenAI
from zhipuai import ZhipuAI
from scl_team_coder import glovar
from scl_team_coder.util.prompt_res_util import *
from scl_team_coder.util.agent_tools import *
from datetime import datetime
import subprocess
import os
import tempfile

model="glm-4-plus"
api_key = glovar.API_KEY_AIRX
client = ZhipuAI(api_key=api_key)
baseline_path = f"{glovar.EXPERIMENT_DIR}/baselines/llm4plc"

def save_logs(user_input, assistant_output):
    """
    将对话日志保存到 logs/ 目录下的文件中。
    
    参数:
        user_input (str): 用户的输入。
        assistant_output (str): GPT-4 模型的输出。
    """
    # 创建 logs 目录，如果它不存在
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # 日志文件路径
    log_file = f"{baseline_path}/logs/log.txt"

    # 以追加模式打开文件，写入新的对话记录   
    with open(log_file, "a", encoding="utf-8") as f:
        f.write("\n================================\n")  # 每轮对话之间添加分隔符
        f.write("====== User: ======\n")
        f.write(user_input + "\n\n")
        f.write("====== Assistant: ======\n")
        f.write(assistant_output + "\n")
        
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

def call_gpt4_wo_history(prompt,max_tokens=2048,temperature=0.5):
    response = client.chat.completions.create(
        model = model,  # 填写需要调用的模型名称
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    response_content = response.choices[0].message.content
    return response_content

def call_gpt4_with_history(prompt, max_tokens=4096):
    """
    与 GPT-4 模型进行交互，发送给定的提示并接收模型的响应。
    
    参数:
        prompt (str): 要发送给 GPT-4 的提示。
        max_tokens (int, 可选): 生成的响应中最大的 token 数。默认值为 2048。
        temperature (float, 可选): 控制生成文本的随机性。值越低，生成的文本越确定。默认值为 0.5。
        
    返回:
        str: GPT-4 模型生成的响应。
    """
    # 如果 messages 属性不存在，则初始化它
    if not hasattr(call_gpt4_with_history, "messages"):
        call_gpt4_with_history.messages = []

    # 将用户的新输入添加到消息历史中
    call_gpt4_with_history.messages.append({"role": "user", "content": prompt})

    # 使用 OpenAI API 与 GPT-4 模型进行交互
    response = client.chat.completions.create(
        model=model,  # 填写需要调用的模型名称
        messages=call_gpt4_with_history.messages,
        max_tokens=max_tokens,
    )

    # 从响应中提取 GPT-4 的回复内容
    response_content = response.choices[0].message.content

    # 将 GPT-4 的回复添加到消息历史中
    call_gpt4_with_history.messages.append({"role": "assistant", "content": response_content})

    # 保存对话记录到 logs 目录下的文件中
    save_logs(prompt, response_content)
    
    return response_content

def syntax_check(plc_code):
    # 创建一个临时文件来保存 PLC 代码
    temp_filename = f"{baseline_path}/logs/temp_file.plc"
    with open(temp_filename, "w", encoding='utf-8') as f:
        f.write(plc_code)
    try:
        # 使用 subprocess 调用 matiec 工具，假设 iec2iec 工具在 ~/matiec/ 目录下
        result = subprocess.run(
            f"./iec2iec -f -p {temp_filename} 2>&1 > /dev/null | head -n -2",
            stdout=subprocess.PIPE,  # 捕获标准输出
            stderr=subprocess.PIPE,  # 捕获标准错误输出
            cwd="/root/matiec",  # 设置工作目录为 matiec 目录
            shell=True  # 启用 shell 特性
        )
        # 获取输出结果
        stdout = result.stdout.decode('utf-8')
        stderr = result.stderr.decode('utf-8')
        
        # 如果 stdout 和 stderr 都为空，表示语法检查通过
        if not stdout and not stderr:
            return True, "no syntax error"  # 检查通过，返回 True 和空反馈信息
        else:
            # 如果有输出或错误，表示检查不通过，返回 False 和错误信息
            return False, stderr if stderr else stdout  # 优先返回错误输出
    finally:
        # 删除临时文件
        os.remove(temp_filename)

def call_nuXmv(smv_code, smv_command):
    """
    调用 nuXmv 工具来验证 SMV 代码。

    参数:
        smv_code (str): 要验证的 SMV 代码。
        smv_command (str): 用于调用 nuXmv 的命令。

    返回:
        tuple: 包含验证结果和输出信息的元组。如果验证成功，第一个元素为 True，否则为 False；第二个元素为验证工具的输出信息。
    """
    smv_filename = f"{baseline_path}/logs/tmp_smv" # 临时的.smv 文件名
    command_filename = f"{baseline_path}/logs/tmp_command" # 临时的 command_file 文件名
    
    # 创建一个临时文件来保存 SMV 代码
    with open(smv_filename, "w") as f:
        f.write(smv_code)
    
    # 在 smv_command 中替换为实际的 smv 文件名
    smv_command = smv_command.replace("smv_model.smv", smv_filename)
    smv_command = f"set on_failure_script_quits\n{smv_command}"
    
    # 创建一个临时文件来保存 nuXmv 的 command_file
    with open(command_filename, "w") as f:
        f.write(smv_command)
    
    try:
        # 使用 subprocess 调用 nuXmv 工具，并指定要执行的命令文件
        result = subprocess.run(
            ['/usr/local/bin/nuXmv', '-source', command_filename],  # 调用 nuXmv，并传入 command_file 文件名
            stdout=subprocess.PIPE,  # 捕获标准输出
            stderr=subprocess.PIPE  # 捕获标准错误输出
        )
        
        # 获取 nuXmv 的输出结果
        stdout = result.stdout.decode('utf-8')
        stderr = result.stderr.decode('utf-8')
        
        # 对stdout进行过滤，删除 nuXmv 生成的额外信息
        filtered_stdout = re.sub(r'^\*\*\*.*$\n?', '', stdout, flags=re.MULTILINE)
        filtered_stdout = re.sub(r'\n\s*\n+', '\n', filtered_stdout)        
        
        # 如果输出中包含 "is false"，则表示验证失败
        if "is false" in filtered_stdout: 
            return False, filtered_stdout  
        # 如果输出中包含 "syntax error"，则表示存在语法错误
        elif "syntax error" in stderr or "aborting" in filtered_stdout:
            return False, stderr
        # 如果没有错误，则表示验证成功
        else:
            return True, filtered_stdout+stderr
    finally:
        # 删除临时文件
        os.remove(smv_filename)  # 删除临时的.smv 文件
        os.remove(command_filename)  # 删除临时的 command_file 文件


def save_prompt(prompt,output_file):
    """
    保存生成的提示到指定的文件中。

    参数:
        prompt (str): 要保存的提示。
        output_file (str): 输出文件的路径。
    """
    with open(output_file, "a+", encoding='utf-8') as f:
        f.write("\n================================\n")
        f.write(prompt)
        f.write("\n********************************\n")

import re

def extract_target_output(text,start="START_SCL",end="END_SCL"):
    """
    从给定文本中提取“START_SCL”和“END_SCL”之间的内容。
    
    参数:
        text (str): 包含 START_SCL 和 END_SCL 标签的文本。
        
    返回:
        list: 提取出的所有内容列表。
    """
    # 正则表达式匹配 START_SCL 和 END_SCL 之间的内容，非贪婪匹配
    pattern = f'{start}(.*?){end}'
    
    # 使用 re.findall 提取所有匹配的内容，re.DOTALL 使 . 能匹配换行符
    matches = re.findall(pattern, text, re.DOTALL)
    
    # 返回获取到的第一个内容
    if len(matches) == 0:
        return ""
    return parse_response(matches[0])

def pipeline(nl_task_requirements):
    
    print("开始任务管道...")
    
    # 定义prompt输出文件路径
    prompt_file = f"{baseline_path}/logs/prompt.txt"
    
    # 加载系统提示模板，获取不同阶段任务的提示语
    sys_prompts = load_prompt()
    print("加载系统提示模板完成.")
    
    # 阶段1：生成任务规划
    prompt_generate_plan = (
        sys_prompts['phase1']['task1_planning']
        .replace("[USER_SPECIFICATION_INPUT]", nl_task_requirements)
        .replace("[PLAN_EXAMPLE]", sys_prompts['meta']['mbd_prompt'])
        .replace("[SCL_EXAMPLE]", sys_prompts['meta']['scl_prompt'])
    )
    print("生成任务规划提示完成.")
    
    # 调用GPT模型生成计划
    plan = extract_target_output(call_gpt4_with_history(prompt_generate_plan), "START_PLAN", "END_PLAN")
    print(f"生成任务计划完成: {plan[:30]}")
    
    # 保存生成的计划到提示文件
    save_prompt(prompt_generate_plan, prompt_file)
    print("保存任务规划提示到文件完成.")
    
    # 阶段2：生成SCL代码并进行反馈循环
    loop_count = 0
    plc_passed = False
    
    # 生成初始SCL代码提示
    prompt_generate_plc_code = (
        sys_prompts['phase2']['task1_genSCL']
        .replace("[SCL_EXAMPLE]", sys_prompts['meta']['scl_prompt'])
    )
    print("生成初始SCL代码提示完成.")
    
    # 保存生成的SCL代码提示到文件
    save_prompt(prompt_generate_plc_code, prompt_file)
    print("保存初始SCL代码提示到文件完成.")
    
    # 调用GPT模型生成SCL代码
    plc_code = extract_target_output(call_gpt4_with_history(prompt_generate_plc_code), "START_SCL", "END_SCL")
    print(f"生成初始SCL代码完成: {plc_code[:30]}...")  # 只打印前100个字符
    
    # 对生成的SCL代码进行语法检查
    plc_passed, plc_syntax_check_feedback = syntax_check(plc_code)
    print(f"SCL代码语法检查结果: {'通过' if plc_passed else '未通过'}, 反馈: {plc_syntax_check_feedback}")
    
    # 如果语法检查未通过且未超过循环次数，则根据反馈修正代码并重新生成
    while not plc_passed and loop_count < 3:
        print(f"SCL代码语法检查未通过，开始第{loop_count + 1}次修正...")
        
        # 根据语法检查反馈生成新的SCL代码提示
        prompt_generate_plc_code_with_feedback = (
            sys_prompts['phase2']['task2_sclFeedback']
            .replace("[USER_FEEDBACK]", plc_syntax_check_feedback)
        )
        print("生成修正后的SCL代码提示完成.")
        
        # 保存修正后的提示到文件
        save_prompt(prompt_generate_plc_code_with_feedback, prompt_file)
        print("保存修正后的SCL代码提示到文件完成.")
        
        # 调用GPT模型生成新的SCL代码
        plc_code = extract_target_output(call_gpt4_with_history(prompt_generate_plc_code_with_feedback), "START_SCL", "END_SCL")
        print(f"生成修正后的SCL代码完成: {plc_code[:30]}...")
        
        # 再次进行语法检查
        plc_passed, plc_syntax_check_feedback = syntax_check(plc_code)
        print(f"SCL代码语法检查结果: {'通过' if plc_passed else '未通过'}, 反馈: {plc_syntax_check_feedback}")
        
        loop_count += 1
    
    # 阶段3：生成SMV代码并进行反馈循环
    loop_count = 0
    smv_passed = False
    
    # 生成初始SMV代码提示
    prompt_generate_smv_code = (
        sys_prompts['phase2']['task3_scl2smv']
        .replace("[SMV_GRAMMAR]", sys_prompts['meta']['VacuumGripper.smv'])
        .replace("[SMV_COMMAND_GRAMMAR]", sys_prompts['meta']['smv_command_prompt'])
    )
    print("生成初始SMV代码提示完成.")
    
    # 保存生成的SMV代码提示到文件
    save_prompt(prompt_generate_smv_code, prompt_file)
    print("保存初始SMV代码提示到文件完成.")
    
    # 调用GPT模型生成SMV代码
    smv_raw = call_gpt4_with_history(prompt_generate_smv_code)
    smv_code = extract_target_output(smv_raw, "START_SMV", "END_SMV")
    smv_command = extract_target_output(smv_raw, "START_SMV_COMMAND", "END_SMV_COMMAND")
    print(f"生成初始SMV代码完成: {smv_code[:30]}...")  # 只打印前100个字符
    
    # 对生成的SMV代码进行语法验证
    smv_passed, smv_check_feedback = call_nuXmv(smv_code, smv_command)
    print(f"SMV代码语法验证结果: {'通过' if smv_passed else '未通过'}, 反馈: {smv_check_feedback}")
    
    # 如果验证未通过且未超过循环次数，则根据反馈修正代码并重新生成
    while not smv_passed and loop_count < 3:
        print(f"SMV代码语法验证未通过，开始第{loop_count + 1}次修正...")
        
        # 根据SMV反馈生成新的SMV代码提示
        prompt_generate_smv_code_with_feedback = (
            sys_prompts['phase2']['task4_smvFeedback']
            .replace("[USER_FEEDBACK]", smv_check_feedback)
        )
        print("生成修正后的SMV代码提示完成.")
        
        # 保存修正后的提示到文件
        save_prompt(prompt_generate_smv_code_with_feedback, prompt_file)
        print("保存修正后的SMV代码提示到文件完成.")
        
        # 调用GPT模型生成新的SMV代码
        smv_raw = call_gpt4_with_history(prompt_generate_smv_code_with_feedback)
        smv_code = extract_target_output(smv_raw, "START_SMV", "END_SMV")
        smv_command = extract_target_output(smv_raw, "START_COMMAND", "END_COMMAND")
        print(f"生成修正后的SMV代码完成: {smv_code[:30]}...")
        
        # 再次进行SMV代码验证
        smv_passed, smv_check_feedback = call_nuXmv(smv_code, smv_command)
        print(f"SMV代码语法验证结果: {'通过' if smv_passed else '未通过'}, 反馈: {smv_check_feedback}")
        
        loop_count += 1
    
    # 阶段4：验证SMV对计划的反馈结果，并使用反馈重新生成SCL代码
    loop_count = 0
    smv_passed = False
    plc_passed = False
    
    # 同时检查SMV和SCL代码的状态，直到二者都通过或超过循环次数
    while (not plc_passed or not smv_passed) and loop_count < 3:
        print(f"开始第{loop_count + 1}次工具链反馈处理...")
        
        # 对SMV代码进行验证
        smv_passed, smv_feedback = call_nuXmv(smv_code, smv_command)
        print(f"SMV代码验证结果: {'通过' if smv_passed else '未通过'}, 反馈: {smv_feedback}")
        
        # 对SCL代码进行语法检查
        plc_passed, plc_syntax_check_feedback = syntax_check(plc_code)
        print(f"SCL代码语法检查结果: {'通过' if plc_passed else '未通过'}, 反馈: {plc_syntax_check_feedback}")
        
        # 根据SMV和SCL工具链的反馈生成新的SCL代码提示
        prompt_generate_plc_code_with_toolChainFeedback = (
            sys_prompts['phase3']['task1_logicFeedback']
            .replace(
                "[TOOLCHAIN_FEEDBACK]",
                f"smv check feedback:\n{smv_feedback}\nplc syntax check feedback:\n{plc_syntax_check_feedback}"
            )
        )
        print("生成工具链反馈处理后的SCL代码提示完成.")
        
        # 保存生成的提示到文件
        save_prompt(prompt_generate_plc_code_with_toolChainFeedback, prompt_file)
        print("保存工具链反馈处理后的SCL代码提示到文件完成.")
        
        # 调用GPT模型生成新的SCL代码
        plc_code = extract_target_output(call_gpt4_with_history(prompt_generate_plc_code_with_toolChainFeedback), "START_SCL", "END_SCL")
        print(f"生成工具链反馈处理后的SCL代码完成: {plc_code[:30]}...")
        
        loop_count += 1
    
    # 返回最终的任务计划、SCL代码、SMV代码，以及验证结果
    print(f"all done. smv_passed : {smv_passed} and plc_passed : {plc_passed}")
    data['code'] = plc_code
    return data

def run_llm4plc(dataset="competition_en"):
    """
    运行基于LLM的PLC代码生成器。

    参数:
        dataset (str): 要处理的数据集名称。默认为"competition_en"。

    返回:
        list: 包含生成的计划、PLC 代码、SMV 代码以及验证结果的元组列表。
    """
    dataset_path = f"{glovar.EXPERIMENT_DIR}/datasets/"
    output_path = f"{glovar.EXPERIMENT_DIR}/output/{dataset}/llm4plc"
    # 获取当前时间
    current_time = datetime.now()
    # 格式化日期和时间
    date_folder = current_time.strftime("%Y-%m-%d")
    time_folder = current_time.strftime("%H-%M-%S")
    # 构建输出文件路径
    output_to = f"{output_path}/{date_folder}_{time_folder}.jsonl"
    test_data = read_jsonl(dataset_path + f"{dataset}.jsonl")
    # 如果输出路径不存在，则创建它
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    with open(output_to, "w") as fp:
        for data in test_data:
            if 'description_zh' in data:
                del data['description_zh']
            result = pipeline(str(data))
            # 将结果列表保存到输出文件中
            fp.write(json.dumps(result, ensure_ascii=False)) 
            fp.write("\n")
            
            # FOR DEBUG ONLY
            return 0

