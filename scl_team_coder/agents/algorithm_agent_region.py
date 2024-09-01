from datetime import datetime
import pytz
import json
import os
import time
from scl_team_coder.util.prompt_res_util import PromptResultUtil
from scl_team_coder.util.agent_tools import remove_braces,prettify_task,parse_response
from zhipuai import ZhipuAI
import codecs
import threading
import random
from scl_team_coder import glovar


class AlgorithmAgent():

    algorithm_agent_prompt_sys = """Role: You are a Siemens SCL code analyst. Given a task description and corresponding Siemens SCL programming case code, you can conduct a detailed analysis of the case code.

Input:
1. A task requirement description. The description will be given in the form of JSON.
2. A Siemens SCL programming case code. The case code implements the given task requirements.

Goals:
1. Identify the variables declared and used in the case code, along with their types and roles.
2. Identify the SCL instructions and their functions used in the case code.
3. Summarize the concrete planning used in the case code to solve the task.

Constraints:
1. Your response must follow the specified output format. Note that there are some comments in it suggesting what content you should fill in at that location.
2. Do not add extra explanation or words outside of the specified output format.
3. The SCL instruction you identified in the case code must follows a certain calling form of the 'INSTRUCTION_NAME(PARAMETER)', parameters must be passed in bracket after the name.

Workflow:
1. Input Analysis: Carefully read and understand the task requirement description. 
2. Splitting: Analyze and split the code, extract variable declarations and logical blocks: Variable declarations are usually located within declaration blocks starting with 'VAR', which typically come before the 'BEGIN' keyword. The logical blocks (used to implement tasks) are usually located after the 'BEGIN' keyword.
3. Variables Analysis: Find all declared variables, analyze their types, initial values, and usage locations. Determine the specific role and impact of each variable in the code.
4. Logical Analysis: Analyze the logical structure of the code, identify conditional judgments, loops, function calls, etc. Describe the algorithm plan for implementing tasks in logical order, step by step.
5. Instructions Analysis: Extract the SCL instruction calls involved in the logical block. The SCL instruction is a function call that is not implemented in the current code and is provided by SCL by default.
6. Output Delivery: Present the final result in the specified output format.

Output Format:
<root>
<vars>
# Variables analysis. For example:
1. name: value, type: Int, initial: None, role: An input number value for the function to process or use.
2. name: tempLoopIndex, type: DInt, initial: 0, role: An temp iteration variable used for iterating.
</vars>
<instructions>
# Instruction usage analysis. You just need to identify the instruction name used in case code. Use the ',' symbol to separate instruction names.
# For example: 
USINT_TO_DINT,SHR
</instructions>
<planning>
# Describe the algorithm plan for implementing tasks in logical order, step by step. The steps bellow show an algorithm plan for a bits counting task in DWord datatype.
# Step1. Initialize the temp output counters tempCountBitsFalse and tempCountBitsTrue to 0.
# Step2. Assign the input value value to tempBinaryValues.
# Step3. Use the 'FOR' loop to iteratively count each bit's TRUE and FALSE values and save the results to those two counters. Use the 'SHR' instruction to shift tempBinaryValues one bit to the right during each iteration.
# Step4. After the loop ends, assign the value of the temporary counter to the output parameters countBitsFalse and countBitsTrue.
# Step5. Due to no error handling, variable ENO is set to TRUE.
</planning>
</root>"""

    @classmethod
    def algorithm_agent_prompt(self, requirements: str, case_code: str) -> str:
        """
        ## 【输入】 任务需求requirements(JSON字符串形式) 和样例代码
        ## 【执行】 结合需求和代码进行分析
        ## 【输出】 1. 算法流程  2. 调用了哪些指令  3. 声明了哪些变量 变量作用是什么
        """
        algorithm_agent_prompt_user = f"""Here is a task requirement description, structured in JSON format: 
{requirements}
Here is the corresponding case code:
```scl
{case_code}
```
Please answer."""
        
        from zhipuai import ZhipuAI
        api_key = glovar.API_KEY_AIRX
        client = ZhipuAI(api_key=api_key)

        response = client.chat.completions.create(
            model="glm-4-0520",  # 填写需要调用的模型名称
            messages=[
                {"role": "system", "content": AlgorithmAgent.algorithm_agent_prompt_sys.strip()},
                {"role": "user", "content": algorithm_agent_prompt_user}
            ],
            max_tokens=96*1000,
            temperature=0.75,
        )
        # print(response.choices[0].message.content)
        # path = f"./output/algo_agent_test_{datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y%m%d-%H%M%S')}.txt"
        # with open(path, 'w', encoding='utf8') as f:
        #     f.write(response.choices[0].message.content)
        # f.close()
        return response.choices[0].message.content
    
    @classmethod
    def get_result(self, response: str, name: str) -> dict:
        response = PromptResultUtil.extract_xml_content(response)
        response = PromptResultUtil.replace_tag(response, 'vars')
        response = PromptResultUtil.replace_tag(response, 'instructions')
        response = PromptResultUtil.replace_tag(response, 'planning')
        response = PromptResultUtil.parse_xml(response)
        ins = response["instructions"].strip().split(',')
        res = {
            'variables': response["vars"].strip().split('\n'),
            'instructions': [i.strip() for i in ins],
            'planning': response["planning"].strip(),
            'name': name
        }
        return res

    @classmethod
    def auto_gen_algo(self):
        # get all FC/FB names
        directory = f"{glovar.DATA_DIR}/scl_case_code/"
        json_file_names = [
            os.path.splitext(file)[0] 
            # for file in os.listdir(directory) if file.endswith('.json')
            for file in os.listdir(directory) if file.endswith('.json') and file.startswith('FB')
        ]
        for name in json_file_names:
            if os.path.exists(f"{glovar.DATA_DIR}/scl_case_plan_0520/{name}.plan"):
                print(f"Warning: There is already plan named '{name}' in local files.")
                continue
            code_json = json.loads(PromptResultUtil.get_json_content(name))
            code_scl = PromptResultUtil.get_source_code(name)
            start_time = time.time()
            response = AlgorithmAgent.algorithm_agent_prompt(code_json, code_scl)

            try:
                res = AlgorithmAgent.get_result(response, name)
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"执行耗时：{elapsed_time}秒")

                with open(f"{glovar.DATA_DIR}/scl_case_plan_0520/{name}.plan", 'w', encoding='utf8') as f:
                    f.write(json.dumps(res))

            except Exception as e:
                print(f"Error in getting result: {e}")
                continue

class AlgorithmAgent_zh(AlgorithmAgent):
    algorithm_agent_prompt_sys = f"""
Role：你是SCL(西门子的结构控制语言，用于PLC)编程专家和企业导师。你擅长能分析很长的SCL代码，并使用自然语言向他们介绍算法逻辑。
Goal：输出你对这段代码的分析，要求详细、不遗漏关键细节。
Important：
- 不要列举每个变量。用总结性的话语陈述定义了哪几类变量，有什么作用。
- 以REGION为单位，详细介绍REGION内的逻辑。
- 覆盖变量定义、初始化、输入输出验证、算法流程、输出结果等。
- 由于你的学生是SCL新手，对基础概念和控制思想不太熟悉，你需要在涉及定时器和状态机的部分解释如何使用定时器和为什么需要状态机。
Output Format：
```plaintext
- 概述
- 变量定义。代码中定义了以下几类变量....
- 主逻辑部分
-- REGION <name>：...
-- REGION <name>：...
-- ....
-- REGION <name>：...
```
"""
    @classmethod
    def algorithm_agent_prompt(self, case_code: str, long=False) -> str:
        """
        ## 【输入】 任务需求自然语言描述（中文）和样例代码
        ## 【执行】 结合需求和代码进行分析
        ## 【输出】 1. 算法流程
        """
        # 初始化few-shot
        with open(f'{glovar.RAG_DATA_DIR}/scl_case_code_modified/LGF_ActDeactDevice.scl','r') as fp:
            example_scl = fp.read()
            icl_prompt = remove_braces(example_scl)
        icl_output = f"""
```plaintext
	- 概述
	这段代码是一个使用SCL编写的功能块，名为“LGF_ActDeactDevice”，用于激活和监控或停用分布式设备。它还监控设备连接和错误状态。
	- 变量定义
	代码中定义了以下几类变量：
	 - 输入变量：使能、激活、停用、硬件ID、参数
	 - 输出变量：有效、忙、错误、状态、激活中、已激活、停用中、已停用、设备状态正常、诊断
	 - 内部变量：状态内部、状态激活/停用、状态设备状态、实例看门狗、实例看门狗重新集成、状态主状态
	 - 临时变量：临时使能、临时退出状态循环
	 - 常量：模式信息、模式激活、模式停用、设备处于活动状态、设备处于被动状态、设备激活超时、结果成功、从站存在、从站故障、从站禁用、FB状态无处理、FB状态使能开始、FB状态使能等待、FB状态停用开始、FB状态停用等待、FB状态已停用、FB状态激活开始、FB状态激活等待、FB状态已激活、FB状态禁用开始、FB状态禁用等待、状态无调用、状态第一次调用、状态后续调用、子状态无错误、错误未定义状态、错误日志2地理、错误地理2日志、错误设备停用中、错误设备停用超时、错误在停用状态下读取激活状态、错误设备激活中、错误设备激活超时、错误在激活期间读取设备状态、错误在活动状态下读取设备状态、错误在活动状态下设备状态、错误在活动状态下读取激活状态、错误禁用停用设备、错误禁用看门狗
	- 主逻辑部分
	-- REGION BLOCK INFO HEADER
	   此区域包含功能块的元信息，简单描述。
	-- REGION DESCRIPTION
	   此区域目前为空，但可以包含功能块的简单描述。
	-- REGION ENABLING/DISABLING
	   此区域处理功能块的使能和禁用逻辑。首先，使用临时变量存储使能输入的值。如果使能输入为真且状态为“无调用”，则初始化功能块并开始处理。这包括设置内部状态、错误和诊断信息，并将状态设置为“第一次调用”。如果使能输入为假且上一个周期为真，则开始禁用功能块。如果状态为“第一次调用”，则将状态设置为“后续调用”。最后，使用边缘检测来跟踪使能输入的变化。
	-- REGION Command dedection
	   此区域检测激活和停用命令。首先，检查当前状态是否在“使能等待”和“禁用开始”之间。如果是，则检查是否有激活或停用命令。如果有，则将状态设置为相应的开始状态，并清除请求和先前的错误标志。如果没有，则不执行任何操作。
	-- REGION STATE MACHINE
	   此区域实现了功能块的状态机。首先，使用一个循环来处理状态之间的转换。在循环中，首先将退出循环的标志设置为真。然后，根据当前状态，执行不同的逻辑。每个状态都有相应的处理逻辑，包括错误处理、超时处理等。在处理完一个状态后，检查是否有必要再次运行循环。如果是，则继续循环。否则，退出循环。
	   - #FB_STATE_NO_PROCESSING
	       此状态表示功能块当前没有处理任何操作。在这个状态下，不执行任何操作。
	   - #FB_STATE_ENABLING_START..#FB_STATE_ENABLING_WAIT
	       此状态表示功能块正在使能过程中。在这个状态下，首先重置看门狗定时器，并存储硬件ID。然后，使用LOG2GEO和GEO2LOG功能获取设备的地理地址和IO系统信息。如果获取信息成功，则设置请求和模式，并将状态设置为“使能等待”。否则，将错误信息存储到诊断缓冲区，并设置错误标志。
	   - #FB_STATE_DEACTIVATE_START..#FB_STATE_DEACTIVATE_WAIT
	       此状态表示功能块正在停用设备。在这个状态下，首先设置请求和模式，并将状态设置为“停用等待”。然后，检查是否有错误发生。如果有，则将错误信息存储到诊断缓冲区，并设置错误标志。否则，检查是否超时。如果超时，则将错误信息存储到诊断缓冲区，并设置错误标志。否则，将状态设置为“已停用”。
	   - #FB_STATE_DEACTIVATED
	       此状态表示设备已停用。在这个状态下，切换请求标志以获取状态信息，并检查是否有错误发生。如果有，则将错误信息存储到诊断缓冲区，并设置错误标志。否则，清除错误标志。
	   - #FB_STATE_ACTIVATE_START..#FB_STATE_ACTIVATE_WAIT
	       此状态表示功能块正在激活设备。在这个状态下，首先设置请求和模式，并将状态设置为“激活等待”。然后，检查是否有错误发生。如果有，则将错误信息存储到诊断缓冲区，并设置错误标志。否则，检查是否超时。如果超时，则将错误信息存储到诊断缓冲区，并设置错误标志。否则，将状态设置为“已激活”。
	   - #FB_STATE_ACTIVATED
	       此状态表示设备已激活。在这个状态下，切换请求标志以获取状态信息，并检查是否有错误发生。如果有，则将错误信息存储到诊断缓冲区，并设置错误标志。否则，清除错误标志。同时，启动看门狗定时器来监控设备状态。
	   - #FB_STATE_DISABLING_START..#FB_STATE_DISABLING_WAIT
	       此状态表示功能块正在禁用过程中。在这个状态下，首先设置请求和模式，并将状态设置为“禁用等待”。然后，检查是否有错误发生。如果有，则将错误信息存储到诊断缓冲区，并设置错误标志。否则，检查是否超时。如果超时，则将错误信息存储到诊断缓冲区，并设置错误标志。否则，将状态设置为“无处理”。
	   - ELSE
	       如果状态机达到未定义的状态，则将错误信息存储到诊断缓冲区，并设置错误标志。
	-- REGION OUTPUTS
	   此区域将内部变量的值写入输出变量。首先，检查是否禁用完成。如果是，则重置输出。然后，检查是否有用户清除的错误。如果有，则将错误输出设置为真，并写入诊断信息。否则，检查是否有自动清除的错误。如果有，则将错误输出设置为真，并写入诊断信息。否则，将有效和忙输出设置为相应的值。最后，写入一些应用特定的静态值到输出。
```
"""
        algorithm_agent_prompt_user = case_code
        api_keys = [glovar.API_KEY_AIRX]
        client = ZhipuAI(api_key=random.choice(api_keys))
        # 初始化few-shot
        response = client.chat.completions.create(
            model="glm-4-0520",  # 填写需要调用的模型名称
            messages=[
                {"role": "system", "content": AlgorithmAgent_zh.algorithm_agent_prompt_sys},
                {"role": "user", "content": icl_prompt},
                {"role": "assistant", "content": icl_output},
                {"role": "user", "content": algorithm_agent_prompt_user}
            ],
            max_tokens=4096,
            temperature=0.8,
            top_p=0.8,
        )
        if long:
            # 太长则需要两次
            second_response = client.chat.completions.create(
                model="glm-4-0520",  # 填写需要调用的模型名称
                messages=[
                    {"role": "system", "content": AlgorithmAgent_zh.algorithm_agent_prompt_sys},
                    {"role": "user", "content": icl_prompt},
                    {"role": "assistant", "content": icl_output},
                    {"role": "user", "content": algorithm_agent_prompt_user},
                    {"role": "assistant", "content": response.choices[0].message.content},
                    {"role": "user", "content": "主逻辑部分再详细一些"}
                ],
                max_tokens=4096*2,
                temperature=0.8,
                top_p=0.8,
            )
            before = parse_response(response.choices[0].message.content)
            before = before.split("主逻辑")[0]
            after = parse_response(second_response.choices[0].message.content)
            return before + after
        return parse_response(response.choices[0].message.content)

    @classmethod
    def get_result(self, response: str, name: str) -> dict:
        try:
            res = {
                'variables': [],
                'instructions': [],
                'planning': response,
                'name': name
            }
        except Exception as e:
            print(name,e)
            res = {
                'variables': [],
                'instructions': [],
                'planning': 'ERROR!!!!',
                'name': name
            }            
        return res

    @classmethod
    def auto_gen_algo_patch(self,json_file_names,output_path):
        for name in json_file_names:
            if os.path.exists(f"{output_path}{name}.plan"):
                print(f"Warning: There is already plan named '{name}' in local files.")
                continue
            code_scl = PromptResultUtil.get_source_code(name)
            code_scl = remove_braces(code_scl)
            start_time = time.time()
            if len(code_scl.split("\n")) > 120:
                response = AlgorithmAgent_zh.algorithm_agent_prompt(code_scl,True)
            else:
                response = AlgorithmAgent_zh.algorithm_agent_prompt(code_scl,False)
            try:
                res = AlgorithmAgent_zh.get_result(response, name)
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"--log {name}完成。执行耗时：{elapsed_time}秒")
                with open(f"{output_path}{name}.plan", 'w', encoding='utf8') as f:
                    f.write(json.dumps(res,ensure_ascii=False))
            except Exception as e:
                print(f"Error in getting result: {e}")
                continue
            

    @classmethod
    def auto_gen_algo(self):
        # get all FC/FB names
        directory = f"{glovar.RAG_DATA_DIR}/scl_case_code_modified/"
        output_path = f"{glovar.RAG_DATA_DIR}/scl_case_plan_0520_zh_region/"
        json_file_names = [
            os.path.splitext(file)[0] 
            for file in os.listdir(directory) if file.endswith('.json')
        ]
        chunk_size = 40  # For example, split into chunks of 10 files each
        chunks = [json_file_names[i:i + chunk_size] for i in range(0, len(json_file_names), chunk_size)]
        threads = []
        for chunk in chunks:
            thread = threading.Thread(target=AlgorithmAgent_zh.auto_gen_algo_patch, args=(chunk, output_path))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()        

# if __name__ == '__main__':
#     AlgorithmAgent_zh.auto_gen_algo()
    # AlgorithmAgent.auto_gen_algo()