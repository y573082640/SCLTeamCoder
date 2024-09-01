import os
import json
import time
import threading
from datetime import datetime
import codecs
from scl_team_coder.util.agent_tools import *
from .retrieval_agent import RetrievalAgent
from .planning_agent import planning_process,planning_agent
from zhipuai import ZhipuAI
import random
import multiprocessing
from scl_team_coder.util.agent_tools import programming_guidance,parse_patch,trasnform_example_code_to_template,remove_braces,expert_fix,remove_double_slash_comments
from scl_team_coder.util.bm25.BM25Retriver import BM25RetriverSCL,BM25RetriverInstruction
from scl_team_coder.util.antlr.antlr import syntax_check
from scl_team_coder import glovar
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError, wait, FIRST_COMPLETED

# 共享状态量，用于在线程完成任务时通知其他线程退出
timeout_event = threading.Event()

class TaskCompleteException(Exception):
    """自定义异常，用于指示任务成功完成"""
    pass

tools = [{
"type": "web_search",
"web_search": {
    "enable": False # 禁用：False，启用：True，默认为 True。
}
}]

def editor_prompt(TaskRequirements, AlgorithmProcess, APIDetails, CodeTemplate):
    system_prompt = f"""
参考我给你的信息，编写SCL代码以满足任务需求。尽可能使用循环、分支、顺序的结构来替代库函数，只在必要时使用库函数。遵守编程规范。
遵循提供的代码模板来正确构建SCL代码。参考SCL库函数示例代码使用。如果给定的算法步骤不能满足用户需求，你必须将其改正而不是盲目照搬。
OutputFormat:
```scl
    <!-- your scl code here -->
```
IMPORTANT:
SCL库函数:
{APIDetails}
SCL编程规范:
{programming_guidance}
SCL状态机编程:
1. 在没有触发上升沿/跳变时,根据oldState进行输出。
下面是伪代码
```scl
// 假设为上升沿跳变
IF #state AND NOT #oldState:
    // 更新状态，依照新状态进行操作
END_IF;
CASE #state OF 
    #CONST_STATE1: // 根据更新之后的状态操作
        //do something
    #CONST_STATE2:
        //do something
END_CASE;
#oldState := #state; // 保存当前状态
```
2. 如果涉及状态转换,使用repeat-until结合case-of的语法来确保状态转移后,当前周期的输出能正确更新。因为SCL语法中case-of不会重复检查case的改变,所以必须在外层嵌套repeat-until来完成状态更新。使用临时变量`tempExitStateLoop`来从repeat中退出。
下面是伪代码```scl\nREPEAT\n    tempExitStateLoop := TRUE; // 只有在不发生状态转移下才退出\n    CASE #state OF\n        #CONST_STATE1:\n            // do something\n            // if state change then tempExitStateLoop := FALSE; // 状态转移后设置此变量为FALSE以避免未执行新状态的操作\n        #CONST_STATE2:\n            // do something\n            // if state change then tempExitStateLoop := FALSE; // 状态转移后设置此变量为FALSE以避免未执行新状态的操作\n        #CONST_STATE3:\n            // do something\n            // if state change then tempExitStateLoop := FALSE; \n    END_CASE;\nUNTIL(TRUE = #tempExitStateLoop)\nEND_REPEAT;\n```
"""

    instance_prompt = f"""
这里是输入，以XML格式结构化：
<!-- 需要完成的SCL编程任务要求 -->
<Task_Requirements>
{TaskRequirements}
</Task_Requirements>
<!-- 你编写SCL函数时可以参考的状态机和算法流程 -->
<Algorithm_Process>
{AlgorithmProcess}
</Algorithm_Process>
<!-- SCL代码必须遵循的预定义代码模板 -->
<Code_Template>
{CodeTemplate}
</Code_Template>
    """
    return system_prompt, instance_prompt

def verify_and_improver_prompt(TaskRequirements, SCLcode, AlgorithmProcess, StaticAnalysisResults, APIDetails ):
    system_prompt = f"""
Role: 你是一个专家级的SCL（结构化控制语言）代码验证员，负责识别和纠正SCL代码中的语法错误。
Goals: 提供修复补丁。
Workflow:
1. 解释为什么出错。
2. 为每个识别出的错误提供详细的纠正建议。
3. 按照给定格式输出代码补丁。
Important:
1. <code_segment></code_segment>必须直接从SCL代码中复制(包括缩进),<patch></patch>需要能直接替换需要修改的代码段。
2. 结合可能违背的语法规则在代码中指出导致错误的真正原因。
3. 如果可能违背的语法规则不能指出错误原因，参考SCL语法规范和SCL库函数指出错误的真正原因。
4. 有时语法检查的“错误信息”可能指向不恰当的代码位置。
5. 尽可能保持算法逻辑，但使用正确的SCL语法实现。
Outputformat:
```plaintext
- 建议修正 1: [清晰和可操作的错误修正建议]
- 建议修正 k: [清晰和可操作的错误修正建议]
(1)
<code_segment>
</code_segment>
<patch>
</patch>
(n)
<code_segment>
</code_segment>
<patch>
</patch>
```
--附录--
SCL库函数:
{APIDetails}
SCL编程规范:
{programming_guidance}
"""
    instance_prompt = f"""
输入以XML格式结构化：
<!-- 有语法错误的代码。 -->
<SCL代码>
{SCLcode}
</SCL代码>
<!-- 语法检查结果及可能违背的语法规则。context表示语法检查器由于遇到错误而停止的位置。 -->
<语法检查结果>
{StaticAnalysisResults}
</语法检查结果>
"""
    return system_prompt, instance_prompt

def create_program_team_log_structure(base_output_dir,name):
    new_base_folder = os.path.join(base_output_dir, name)
    if not os.path.exists(new_base_folder):
        os.makedirs(new_base_folder)
    teams_messages_file = os.path.join(new_base_folder,'messages.json')
    code_output_file = os.path.join(new_base_folder,f'{name}.scl')
    verifier_output_file = os.path.join(new_base_folder,'verifier.log')
    improver_output_file = os.path.join(new_base_folder,'improver.log')
    syntax_output_file = os.path.join(new_base_folder,'syntaxt.log')
    return teams_messages_file,code_output_file,verifier_output_file,improver_output_file,syntax_output_file

def run_exps(task_path):
    """
        输入任务路径文件夹
    """
    # from antlr.antlr import syntax_check
    start_time = time.time()
    threads = []
    max_threads = 2 # 设置最大线程数为3
    # 获取当前日期和时间，并格式化为文件夹名称
    current_time = datetime.now()
    date_folder = current_time.strftime("%Y-%m-%d")
    time_folder = current_time.strftime("%H-%M-%S")
    # 创建日期和时间组合的文件夹路径
    new_base_folder = os.path.join('./output/program_team_logs', f"{date_folder}_{time_folder}")
    if not os.path.exists(new_base_folder):
        os.makedirs(new_base_folder)
    final_output = os.path.join(new_base_folder,'submit.jsonl')
    # 遍历所有任务，依次执行
    pool = multiprocessing.Pool(processes=min(max_threads,multiprocessing.cpu_count()))
    for filename in os.listdir(task_path):
        if filename.endswith('.json'):  # 确保处理的是 JSON 文件
            file_path = os.path.join(task_path, filename)
            # 读取任务 JSON 文件
            task = json.load(codecs.open(file_path, 'r', 'utf-8-sig'))
            # 提交任务到线程池
            pool.apply_async(start_agents,(task,new_base_folder,final_output,))
            # start_agents(task,new_base_folder,final_output)
    # 等待所有任务完成
    pool.close()
    pool.join()
    # 记录实验结束时间
    end_time = time.time()
    # 计算并打印实验运行的总时间
    total_time = end_time - start_time
    print(f"Experiment completed in {total_time:.2f} seconds.")

def run_api(task:dict):
    start_time = time.time()
    timeout_event.clear()
    default_result = {'name':task['name'],'success':True,'verify_count':0,'code':get_code_template(task=task)}
    result = default_result
    max_threads = 2 # 设置最大线程数为3
    # 获取当前日期和时间，并格式化为文件夹名称
    current_time = datetime.now()
    date_folder = current_time.strftime("%Y-%m-%d")
    time_folder = current_time.strftime("%H-%M-%S")
    # 创建日期和时间组合的文件夹路径
    new_base_folder = os.path.join('./output/program_team_logs', f"{date_folder}_{time_folder}")
    if not os.path.exists(new_base_folder):
        os.makedirs(new_base_folder)
    final_output = os.path.join(new_base_folder,'submit.jsonl')
    # 遍历所有任务，依次执行
    worker_ids = range(1, max_threads + 1)  # 创建 ID 列表 [1, 2, 3]
    # 使用 ThreadPoolExecutor 来并发执行 start_agents 函数
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(start_agents, task, new_base_folder, final_output, worker_id, None) for worker_id in worker_ids]
        # 使用 wait 方法等待第一个完成的任务
        # 加载jieba有时可能需要2s
        done, not_done = wait(futures, timeout=85, return_when=FIRST_COMPLETED)
        if done:
            worker_result = next(iter(done)).result()  # 获取第一个完成的任务结果
            if worker_result is not None and 'success' in worker_result and worker_result['success'] is True:  # 如果获取到有效结果
                result = worker_result
                print(f"{task['name']} success")
            else:
                print(f"task {task['name']} failed, returning default value")
        else:
            print(f"task {task['name']} timed out, returning default value")
        timeout_event.set()
    return result

def start_agents(task:dict,log_folder:str,final_output:str,worker_id=0,semaphore=None):
    """
        调用agents完成SCL编程
        params: task , 任务json
    """
    ret = None
    start_time = time.time()
    api_keys = [glovar.API_KEY_0520]
    client = ZhipuAI(api_key=random.choice(api_keys))
    model = 'glm-4-0520'
    bm25retriverAPI = BM25RetriverInstruction()
    bm25retriverCase = BM25RetriverSCL()
    print(task['name'],f"结束-bm25初始化-执行时间: {(time.time()-start_time):.3f} 秒")
    try:
        # task转换为易读的自然语言形式
        # nl_task_requirements = prettify_task(task)
        nl_task_requirements = str(task)
        # 获取输出log文件
        teams_messages_file,code_output_file,verifier_output_file,improver_output_file,syntax_output_file = create_program_team_log_structure(log_folder,f"{task['name']}_{worker_id}")
        retrieval_response = RetrievalAgent.retrieval_agent_prompt(task['description'])
        retrived_examples = RetrievalAgent.get_result(retrieval_response)
        if len(retrived_examples) == 0:
            retrived_examples = bm25retriverCase.query_doc(task['description'])
        print(task['name'],f"结束-检索相似样例-执行时间: {(time.time()-start_time):.6f} 秒")
        with open(teams_messages_file,'a+') as fp:
            example_names = [item['name'] for item in retrived_examples]
            print(f"检索到的相似案例:{example_names}")
            fp.write(json.dumps(example_names,ensure_ascii=False))
        # 获取 算法
        algorithm_for_this_task,related_algorithm = planning_agent(str(task),retrived_examples)
        # 去除 算法的代码/伪代码
        algorithm_for_this_task = remove_code(algorithm_for_this_task)
        print(task['name'],f"结束-获取算法-执行时间: {(time.time()-start_time):.6f} 秒")
        # 获取 api 细节
        api_names_for_algorithm = bm25retriverAPI.query_algo_apis(algorithm_for_this_task)
        api_details_str,api_details = get_api_details([item['name'] for item in retrived_examples],api_names_for_algorithm,nl_task_requirements)
        # print(task['name'],algorithm_for_this_task)
        print(task['name'],api_details.keys())
        print(task['name'],f"结束-获取api细节-共获取{len(api_details.keys())}个API-执行时间: {(time.time()-start_time):.6f} 秒")
        # 构造editor prompt 
        editor_system_prompt,editor_instance_prompt = editor_prompt(
            TaskRequirements=nl_task_requirements,
            AlgorithmProcess=algorithm_for_this_task,
            APIDetails=api_details_str,
            CodeTemplate=get_code_template(task=task)
        ) 
        # 构造shot的prompt
        code_messages = [{"role": "system", "content":editor_system_prompt}]
        for example,algorithm in list(zip(retrived_examples,related_algorithm))[::-1]:
            _,icl_example = editor_prompt(
                # TaskRequirements=prettify_task(example['json_desc']),
                TaskRequirements=str(example['json_desc']),
                AlgorithmProcess=algorithm,
                APIDetails=api_details_str,
                CodeTemplate=trasnform_example_code_to_template(example['code'])
            )
            code_messages.append({"role": "user", "content": icl_example})
            code_messages.append({"role": "assistant", "content":remove_braces(example['code'])})
        code_messages.append({"role": "user", "content": editor_instance_prompt})
        # 写入prompt
        with open(teams_messages_file,'a+') as fp:
            fp.write(json.dumps([code_messages[0],code_messages[-1]],ensure_ascii=False))
        # glm-4调用 获取SCL代码
        stream_code_response = client.chat.completions.create(
            model=model,  # 填写需要调用的模型名称
            max_tokens=16*1024 if model=='glm-4-0520' else 4*1024,
            temperature=0.8 if model=='glm-4-0520' else 0.25,
            top_p=0.2 if model=='glm-4-0520' else 0.8,
            messages=code_messages,
            tools=tools,
            stream=True
        )
        ## 检测任务状态量来决定是否超时
        code_response = ""
        ccount = 0
        for chunk in stream_code_response:
            if ccount == 30:
                time.sleep(0.05)
                ccount = 0
            ccount += 1
            if timeout_event.is_set():
                return
            code_response += chunk.choices[0].delta.content
        print(task['name'],f"EDITOR AGENT-执行时间: {(time.time()-start_time):.6f} 秒")
        with open(code_output_file,'a+') as fp:
            # scl_code = parse_response(code_response.choices[0].message.content)
            scl_code = parse_response(code_response)
            scl_code = expert_fix(scl_code)
            fp.write(scl_code)
        verify_count = 0
        verifier_messages = []
        while verify_count < 3:
            verify_count += 1
            error_log,no_error = syntax_check(scl_code)
            if no_error:
                print(task['name'],'SUCCESS!')
                break
            else:
                print(task['name'],'Start Verification!')
                with open(syntax_output_file,'a+') as fp:
                    fp.write(error_log)
                    fp.write('\n' + '='*20)
            verifier_system_prompt,verifier_instance_prompt = verify_and_improver_prompt(
                StaticAnalysisResults=error_log,
                SCLcode=scl_code,
                TaskRequirements=nl_task_requirements,
                APIDetails=api_details_str,
                AlgorithmProcess=algorithm_for_this_task
            )            
            if len(verifier_messages)==0:
                # 输入系统提示词
                verifier_messages.append({"role": "system", "content": verifier_system_prompt})
                with open(f'{glovar.RAG_DATA_DIR}/few-shots/verifier_fewshot.txt','r') as fp:
                    verifier_fewshots = fp.read()
                # 输入补丁few-shot
                verifier_fewshots = verifier_fewshots.split("=====")
                for example in verifier_fewshots:
                    buggy_code,check_feedback,response_patch = example.split("&&&&&")
                    _,verifier_icl = verify_and_improver_prompt(
                        StaticAnalysisResults=check_feedback,
                        SCLcode=buggy_code,
                        TaskRequirements="",
                        APIDetails=api_details_str,
                        AlgorithmProcess=""
                    )           
                    verifier_messages.append({"role": "user", "content": verifier_icl})
                    verifier_messages.append({"role": "assistant", "content": response_patch})
            verifier_messages.append({"role": "user", "content": verifier_instance_prompt})
            stream_verifier_response = client.chat.completions.create(
                model=model,  # 填写需要调用的模型名称
                max_tokens=12*1024 if model=='glm-4-0520' else 2*1024,
                temperature=0.2,
                top_p=0.9,
                messages=verifier_messages,
                tools=tools,
                stream=True
            )
            ## 检测任务状态量来决定是否超时
            code_response = ""
            ccount =0
            for chunk in stream_verifier_response:
                if ccount == 30:
                    time.sleep(0.05) # 防止饥饿
                    ccount = 0
                ccount += 1
                if timeout_event.is_set():
                    return
                code_response += chunk.choices[0].delta.content
            with open(verifier_output_file,'a+') as fp:
                # verify_result = code_response.choices[0].message.content
                verify_result = code_response
                verifier_messages.append({"role": "assistant", "content": verify_result})
                fp.write(verify_result)  
            segments_and_patches = parse_patch(verify_result)
            with open(teams_messages_file,'a+') as fp:
                fp.write(json.dumps(segments_and_patches,ensure_ascii=False))
                fp.write('\n')    
            for buggy, patch in segments_and_patches:
                scl_code = scl_code.replace(buggy, patch)
            with open(code_output_file,'a+') as fp:
                # scl_code = parse_response(code_response.choices[0].message.content)  
                scl_code = expert_fix(scl_code)
                fp.write(scl_code)  
            print(task['name'],f"结束-Verify_and_improver ({verify_count}) -执行时间: {(time.time()-start_time):.6f} 秒")
        with open(teams_messages_file,'a+') as fp:
            fp.write(json.dumps(verifier_messages,ensure_ascii=False))
        scl_code = remove_double_slash_comments(scl_code)
        if no_error:
            ret = {'name':task['name'],'success':True,'verify_count':verify_count,'code':scl_code}
        else:
            ret = {'name':task['name'],'success':False,'verify_count':verify_count,'code':get_code_template(task=task)}
        print(task['name'],worker_id,f"结束总执行时间: {(time.time()-start_time):.6f} 秒")       
        return ret
    except Exception as e:
        print(task['name'],e)
        traceback.print_exc()
        ret = {'name':task['name'],'success':False,'verify_count':verify_count,'code':get_code_template(task=task)}
        return ret
    finally:
        if ret:
            with open(final_output,'a+') as fp:
                fp.write(json.dumps(ret,ensure_ascii=False))  
                fp.write('\n')  

def test_run_single(task_path, task_name):
    task0 = {}
    for filename in os.listdir(task_path):
        if filename.endswith('.json'):  # 确保处理的是 JSON 文件
            file_path = os.path.join(task_path, filename)
            # 读取任务 JSON 文件
            task = json.load(codecs.open(file_path, 'r', 'utf-8-sig'))
            if task["name"] == task_name:
                task0 = task
                break
    out = run_api(task0)
    print(out)
    return


def run_exps_service(task: dict):
    res = run_api(task)
    return {
        "name": res.get("name"),
        "code": remove_double_slash_comments(res.get("code"))
    }