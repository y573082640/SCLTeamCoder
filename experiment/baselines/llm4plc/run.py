import os
import glob
from openai import OpenAI
from scl_team_coder import glovar
from scl_team_coder.util.prompt_res_util import *
from scl_team_coder.util.agent_tools import *
from datetime import datetime
import subprocess
import os
import tempfile

api_key = glovar.GPT_API_KEY
client = OpenAI(api_key=api_key,base_url=f"https://www.gptapi.us/v1")
model="gpt-4o"

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

def call_gpt4_with_history(prompt, max_tokens=2048, temperature=0.5):
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
        temperature=temperature
    )

    # 从响应中提取 GPT-4 的回复内容
    response_content = response.choices[0].message.content

    # 将 GPT-4 的回复添加到消息历史中
    call_gpt4_with_history.messages.append({"role": "assistant", "content": response_content})

    return response_content

def syntax_check(plc_code):
    # 创建一个临时文件来保存 PLC 代码
    with tempfile.NamedTemporaryFile(delete=False, suffix=".plc") as temp_file:
        temp_filename = temp_file.name
        temp_file.write(plc_code.encode('utf-8'))  # 将 PLC 代码写入临时文件
    
    try:
        # 使用 subprocess 调用 matiec 工具
        result = subprocess.run(
            ['./iec2iec', temp_filename],
            stdout=subprocess.PIPE,  # 捕获标准输出
            stderr=subprocess.PIPE  # 捕获标准错误输出
        )
        
        # 获取输出结果
        stdout = result.stdout.decode('utf-8')
        stderr = result.stderr.decode('utf-8')

        # 如果 stdout 和 stderr 都为空，表示语法检查通过
        if not stdout and not stderr:
            return True, ""  # 检查通过，返回 True 和空反馈信息
        else:
            # 如果有输出或错误，表示检查不通过，返回 False 和错误信息
            return False, stderr if stderr else stdout  # 优先返回错误输出
    finally:
        # 删除临时文件
        os.remove(temp_filename)

def call_nuXmv(smv_code):
    # 创建一个临时文件来保存 SMV 代码
    with tempfile.NamedTemporaryFile(delete=False, suffix=".smv") as temp_file:
        temp_filename = temp_file.name
        temp_file.write(smv_code.encode('utf-8'))  # 将 SMV 代码写入临时文件

    try:
        # 使用 subprocess 调用 nuXmv 工具，并指定要执行的命令
        result = subprocess.run(
            ['nuXmv', temp_filename],  # 调用 nuXmv 并传入文件名
            stdout=subprocess.PIPE,  # 捕获标准输出
            stderr=subprocess.PIPE  # 捕获标准错误输出
        )
        
        # 获取 nuXmv 的输出结果
        stdout = result.stdout.decode('utf-8')
        stderr = result.stderr.decode('utf-8')

        # 检查 nuXmv 的输出，判断是否有错误或验证失败
        if "is true" in stdout:  # 典型成功输出包含“is true”字样
            return True, ""  # 验证成功，返回 True 和空反馈
        elif stderr:  # 如果标准错误不为空，则返回错误信息
            return False, stderr
        else:
            # 如果验证失败但没有明显错误，返回标准输出作为反馈
            return False, stdout
    finally:
        # 删除临时文件
        os.remove(temp_filename)

def pipeline(nl_task_requirements):
    # 加载系统提示模板，获取不同阶段任务的提示语
    sys_prompts = load_prompt()
    print(sys_prompts)
    
    # 阶段1：生成任务规划，替换用户输入的需求和示例计划、SCL代码
    # 在没有人工参与的情况下自动生成计划
    prompt_generate_plan = (
        sys_prompts['phase1']['task1_planning']  # 任务1的规划生成提示
        .replace("[USER_SPECIFICATION_INPUT]", nl_task_requirements)  # 将用户输入的自然语言需求嵌入提示中
        .replace("[PLAN_EXAMPLE]", sys_prompts['meta']['mbd_prompt'])  # 替换示例计划
        .replace("[SCL_EXAMPLE]", sys_prompts['meta']['scl_prompt'])   # 替换示例SCL代码
    )
    
    # 调用GPT模型生成计划
    plan = call_gpt4_with_history(prompt_generate_plan)
    
    # 阶段2：生成SCL代码并进行反馈循环
    loop_count = 0  # 循环计数器
    plc_passed = False  # 初始化SCL代码语法检查状态为未通过
    
    # 生成初始SCL代码的提示
    prompt_generate_plc_code = (
        sys_prompts['phase2']['task1_genSCL']  # 任务1：生成SCL代码的提示
        .replace("[SCL_EXAMPLE]", sys_prompts['meta']['scl_prompt'])  # 使用示例SCL代码替换占位符
    )
    
    # 调用GPT模型生成SCL代码
    plc_code = call_gpt4_with_history(prompt_generate_plc_code)
    # 对生成的SCL代码进行语法检查
    plc_passed, plc_syntax_check_feedback = syntax_check(plc_code)
    
    # 如果语法检查未通过且未超过循环次数，则根据反馈修正代码并重新生成
    while plc_passed is not True and loop_count < 3:
        # 根据语法检查反馈生成新的SCL代码提示
        prompt_generate_plc_code_with_feedback = (
            sys_prompts['phase2']['task2_sclFeedback']  # 任务2：根据反馈生成SCL代码
            .replace("[USER_FEEDBACK]", plc_syntax_check_feedback)  # 使用用户反馈替换占位符
        )
        
        # 调用GPT模型生成新的SCL代码
        plc_code = call_gpt4_with_history(prompt_generate_plc_code_with_feedback)
        # 再次进行语法检查
        plc_passed, plc_syntax_check_feedback = syntax_check(plc_code)
        loop_count += 1  # 更新循环次数
    
    # 阶段3：生成SMV代码并进行反馈循环
    loop_count = 0  # 重置循环计数器
    smv_passed = False  # 初始化SMV代码验证状态为未通过
    
    # 生成初始SMV代码的提示
    prompt_generate_smv_code = (
        sys_prompts['phase2']['task3_scl2smv']  # 任务3：从SCL代码转换为SMV代码
        .replace("[SMV_GRAMMAR]", sys_prompts['meta']['VacuumGripper.smv'])  # 替换SMV语法示例
    )
    
    # 调用GPT模型生成SMV代码
    smv_code = call_gpt4_with_history(prompt_generate_smv_code)
    # 对生成的SMV代码进行语法验证
    smv_passed, smv_check_feedback = call_nuXmv(smv_code)
    
    # 如果验证未通过且未超过循环次数，则根据反馈修正代码并重新生成
    while smv_passed is not True and loop_count < 3:
        # 根据SMV反馈生成新的SMV代码提示
        prompt_generate_smv_code_with_feedback = (
            sys_prompts['phase2']['task4_smvFeedback']  # 任务4：根据反馈生成SMV代码
            .replace("[USER_FEEDBACK]", smv_check_feedback)  # 使用用户反馈替换占位符
        )
        
        # 调用GPT模型生成新的SMV代码
        smv_code = call_gpt4_with_history(prompt_generate_smv_code_with_feedback)
        # 再次进行SMV代码验证
        smv_passed, smv_check_feedback = call_nuXmv(smv_code)
        loop_count += 1  # 更新循环次数
    
    # 阶段4：验证SMV对计划的反馈结果，并使用反馈重新生成SCL代码
    loop_count = 0  # 重置循环计数器
    smv_passed = False  # 重置SMV验证状态
    plc_passed = False  # 重置SCL验证状态
    
    # 同时检查SMV和SCL代码的状态，直到二者都通过或超过循环次数
    while (plc_passed is not True or smv_passed is not True) and loop_count < 3:
        # 对SMV代码进行验证
        smv_passed, smv_feedback = call_nuXmv(smv_code)
        # 对SCL代码进行语法检查
        plc_passed, plc_syntax_check_feedback = syntax_check(plc_code)
        
        # 根据SMV和SCL工具链的反馈生成新的SCL代码提示
        prompt_generate_plc_code_with_toolChainFeedback = (
            sys_prompts['phase3']['task1_logicFeedback']  # 任务1：根据工具链反馈生成SCL代码
            .replace(
                "[TOOLCHAIN_FEEDBACK]",
                f"smv check feedback:\n{smv_check_feedback}\nplc syntax check feedback:\n{plc_syntax_check_feedback}"
            )  # 替换反馈占位符，加入SMV和SCL检查的反馈
        )
        
        # 调用GPT模型生成新的SCL代码
        plc_code = call_gpt4_with_history(prompt_generate_plc_code_with_toolChainFeedback)
        loop_count += 1  # 更新循环次数
    
    # 返回最终的任务计划、SCL代码、SMV代码，以及验证结果
    return plan, plc_code, smv_code, smv_passed and plc_passed

def run_llm4plc(dateset="competition"):
    """
    运行基于LLM的PLC代码生成器。

    参数:
        dateset (str): 要处理的数据集名称。默认为"competition"。

    返回:
        list: 包含生成的计划、PLC 代码、SMV 代码以及验证结果的元组列表。
    """
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

