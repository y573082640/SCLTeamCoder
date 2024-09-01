# from promptings.MapCoder import *
from zhipuai import ZhipuAI
import xml.etree.ElementTree as ET
import json
import os
from scl_team_coder.util.agent_tools import prettify_task
from scl_team_coder.util.agent_tools import programming_guidance,parse_response
from scl_team_coder.util.bm25.BM25Retriver import BM25RetriverSCL,BM25RetriverInstruction
from scl_team_coder import glovar

tools = [{
"type": "web_search",
"web_search": {
    "enable": False # 禁用：False，启用：True，默认为 True。
}
}]

state_machine_and_old_prompt = f"""
先判断是过程控制任务还是数据处理任务。
对过程控制任务:
    1.分析有哪些状态。 
    2.分析状态转移事件。
    3.给出算法流程,不要输出代码
对数据处理任务:
    1.给出算法流程,不要输出代码
IMPORTANT:
- 保持语言专业严谨，符合PLC编程语言的规范。
- 考虑数据类型转换,必要时将Byte、Int转换为Real再计算。
- 如果没有发生转移事件，维持当前状态的动作。 
- 保持语言专业严谨，符合PLC编程语言的规范。
- 不允许对In_Out类型参数进行初始化操作。
- Static类型变量的初始化操作需要谨慎,防止误删其中保存的重要数据(如数据库的当前存储状态)。
- 如果需要检测“跳变”、“上升沿”或“下降沿”，你应当使用【静态变量】保存每个周期的输入状态state，再与下一周期的输入进行比较(`IF newState and not oldsState`)以确定是否发生跳变。
"""
state_machine_prompt = f"""
先判断是过程控制任务还是数据处理任务。
对过程控制任务:
    1.分析有哪些状态。 
    2.分析状态转移事件。
    3.给出算法流程,不要输出伪代码或者其他任何形式的代码内容!
对数据处理任务:
    1.给出算法流程,不要输出伪代码或者其他任何形式的代码内容!
注意事项:
- 保持语言专业严谨，符合PLC编程语言的规范。
- 不要进行初始化操作,防止误删重要数据。
- 如果没有发生转移事件，维持当前状态的动作。 
- 如果题目没有明确要求进行错误处理,则无需考虑错误处理逻辑,可以认为不会出现异常。
"""
# - 首先定义所有需要的变量,随后开始处理业务逻辑,不要在业务逻辑中定义新变量。
# (不要输出伪代码或者其他任何形式的代码内容!)
# - 如果题目没有给出相应错误代码,则无需进行异常判断,可以认为不会出现异常。
# - 如果有必要,使用`UPPERBOUND`和`LOWERBOUND`获取可变上限数组的长度;使用`LEN`获取STRING的长度;使用`CountOfElements`获取Variant数组的长度。
# - 考虑数据类型转换,将Byte、Int转换为Real再计算。
# - 每个状态通常需要维持多个周期,例如保持电机转动直到下一个状态。
# 2.分析状态转换事件。
# - 产品在电机上运输过程也是状态之一。
# 3.给出状态转移算法流程,不要输出代码
# - 不要自己定义函数。
# - 如果没有发生转移事件，维持当前状态。 
# - 确保状态发生转移后,当前周期输出新状态。
new_system_prompt = f"""
用中文描述你解决这个问题的算法步骤，不输出任何伪代码。告诉我解决这个问题需要特别注意的方面。
Important:
- 保持语言专业严谨，符合PLC编程语言的规范。
- 不允许对In_Out类型参数进行初始化操作。
- 无需考虑数据类型转换。
- Static类型变量的初始化操作需要谨慎,防止误删其中保存的重要数据(如数据库的当前存储状态)
- 如果需要检测“跳变”、“上升沿”或“下降沿”，你应当使用【静态变量】保存每个周期的输入状态state，再与下一周期的输入进行比较(`IF newState and not oldsState`)以确定是否发生跳变。
- 类似灌装生产线的控制系统通常被称为实时控制系统。因此在编程时，注意每个扫描周期检查和保持历史状态，确保在没有新信号时维持现有状态。意味着在每个扫描周期内，PLC会记住上一周期的状态，并在没有新输入信号的情况下维持这个状态。这样可以确保系统在没有新的输入信号时不会改变当前的输出状态。以灌装生产线为例，当传感器检测到瓶子到达灌装位置时，启动灌装阀门。只有在操作员确认灌装完成后，才关闭灌装阀门。如果没有操作员的确认信号，阀门应该保持打开状态。
"""

list_problem_prompt = f"""
Role: 你是一名专家SCL（Structured Control Language）算法细化分析者，负责找出算法流程中需要进一步细化描述的部分，并进行细化，最终得到新的算法流程。不要输出伪代码，用自然语言描述！
Goals:
1. 根据提供的需求，找出需要进一步的细化的算法流程片段。
2. 细化需要进一步细化的算法流程片段。
3. 得到细化后的算法流程。
4. 确保算法描述尽可能详细、准确，涵盖尽可能多的信息，并易于理解。
Workflow:
1. 仔细阅读并理解提供的需求。
2. 仔细阅读并理解提供的算法流程。
3. 寻找流程中可以被进一步细化的部分，如数组排序等。
4. 详细地列出算法流程中可以被细化的部分。
5. 对列出的可细化部分进行细化。
6. 输出经过细化后的算法流程
Constraints:
1. 回答不要出现伪代码或者其他任何形式的代码内容，必须以自然语言描述算法流程。
Important:
1. 对于提出有待细化的部分，给出具体的细化措施！
2. 展开具体讲讲细化的具体步骤是什么。
3. 确保你的细化措施仍然遵循算法流程。
4. 确保你的细化措施满足任务需求。
5. 细化所采用的算法要尽可能从编码方面简单，不用过于考虑时间复杂度，例如对于排序，优先采用插入排序算法而非快速排序算法。
6. 利用原流程的信息以及细化的流程片段信息，将整合的算法流程写得尽可能细节，涵盖尽可能多的信息，包含你所知的所有信息！！！！
7. 整合的算法流程要包含所有原算法流程中出现的变量！！
8. 不要输出伪代码或者其他任何形式的代码内容，用自然语言描述算法流程！

Output Format:
```plaintext
----有待细化的算法流程片段以及细化操作流程----
1. [需要细化的部分]：
- [细化内容1]：
- [细化内容2]：
- [细化内容n]：
...
K. [需要细化的部分]：
- [细化内容1]：
- [细化内容2]：
- [细化内容n]：
--------
----细化后的算法流程----
// 根据需求撰写详细的自然语言算法描述，覆盖包括但不限于以下部分：
- [输入和输出变量声明]
- [临时变量声明]
- [常量声明]
- [初始化步骤]
- [输入输出验证]
- [主逻辑1]
- [主逻辑2]
...
- [主逻辑n]
- [结果输出]
--------
```
"""

# 以下是三个备选案例，为防止LLM的幻觉导致推荐不在案例库中的案例，因此选取三个备选案例，当找不到对应案例时填补缺漏
alternativeProcess1 = """
{"variables": ["1. name: left, type: String, initial: None, role: The first string to be compared in the function.", "2. name: right, type: String, initial: None, role: The second string to be compared in the function.", "3. name: tempResult, type: SInt, initial: None, role: A temporary variable to store the result of the string comparison before returning it.", "4. name: RETURN_STRINGS_ARE_EQUAL, type: SInt, initial: 0, role: A constant representing the result when strings are equal.", "5. name: RETURN_STRING_LEFT_LESS_THAN_RIGHT, type: SInt, initial: -1, role: A constant representing the result when the left string is less than the right string.", "6. name: RETURN_STRING_LEFT_GREATER_THAN_RIGHT, type: SInt, initial: 1, role: A constant representing the result when the left string is greater than the right string."], "instructions": [""], "planning": "Step1. Declare two input variables 'left' and 'right' of type String for the strings to be compared.\nStep2. Declare a temporary variable 'tempResult' of type SInt to hold the result of the comparison.\nStep3. Declare three constants to represent the possible outcomes of the string comparison.\nStep4. Compare the 'left' and 'right' strings using the '<' and '>' operators to determine if one string is less than or greater than the other.\nStep5. Assign the appropriate constant value to 'tempResult' based on the comparison outcome.\nStep6. Set the function's return value to 'tempResult'.\nStep7. Set the 'ENO' output parameter to FALSE (the meaning of this within the context of this function is not specified in the task requirement).", "name": "LGF_CompareString"}
"""

alternativeProcess2 = """
{"variables": ["1. name: value, type: DWord, initial: None, role: The input value containing the bits to be counted.", "2. name: numberOfBits, type: USInt, initial: None, role: Specifies the number of bits to count in the input value.", "3. name: countBitsFalse, type: USInt, initial: None, role: Outputs the number of bits that are FALSE in the input value.", "4. name: countBitsTrue, type: USInt, initial: None, role: Outputs the number of bits that are TRUE in the input value.", "5. name: tempBinaryValues, type: DWord, initial: None, role: Temporary variable to hold the current state of the bits being processed.", "6. name: tempLoopIndex, type: DInt, initial: 1, role: Temporary loop index variable for iterating over the bits.", "7. name: tempCountBitsTrue, type: USInt, initial: 0, role: Temporary counter for TRUE bits.", "8. name: tempCountBitsFalse, type: USInt, initial: 0, role: Temporary counter for FALSE bits.", "9. name: ZERO, type: USInt, initial: 0, role: Constant representing the number zero.", "10. name: INCREMENT, type: USInt, initial: 1, role: Constant representing the increment value (one).", "11. name: SHIFT_ON_BIT_RIGHT, type: USInt, initial: 1, role: Constant representing the bit shift value for moving the bits to the right.", "12. name: START_INDEX, type: DInt, initial: 1, role: Constant representing the starting index for the loop."], "instructions": ["USINT_TO_DINT", "SHR"], "planning": "Step1. Initialize the temporary counters tempCountBitsTrue and tempCountBitsFalse to 0.\nStep2. Assign the input value value to tempBinaryValues.\nStep3. Use a 'FOR' loop to iterate over each bit of tempBinaryValues, from the least significant bit to the bit at position numberOfBits.\nStep4. Inside the loop, check the least significant bit of tempBinaryValues to determine if it is TRUE or FALSE, and increment the corresponding counter.\nStep5. Shift the bits of tempBinaryValues one position to the right using the SHR instruction to prepare for the next iteration.\nStep6. After the loop completes, assign the values of tempCountBitsFalse and tempCountBitsTrue to the output parameters countBitsFalse and countBitsTrue, respectively.\nStep7. Set ENO to TRUE as no error handling is required and the function is executed successfully.", "name": "LGF_BitCount"}
"""

alternativeProcess3 = """
{"variables": ["1. name: amplitude, type: Real, initial: 1.0, role: The input parameter that sets the peak value of the sinusoidal signal.", "2. name: offset, type: Real, initial: 0.0, role: The input parameter that sets the vertical offset of the sinusoidal signal.", "3. name: periode, type: UDInt, initial: 1000, role: The input parameter that defines the period of the sinusoidal signal in milliseconds.", "4. name: phaseShift, type: Real, initial: 0.0, role: The input parameter that sets the phase shift of the sinusoidal signal.", "5. name: callOB, type: OB_CYCLIC, initial: None, role: The input parameter that specifies the cyclic interrupt OB number.", "6. name: reset, type: Bool, initial: FALSE, role: The input parameter that allows resetting the signal generator.", "7. name: value, type: Real, initial: None, role: The output parameter that holds the current value of the sinusoidal signal.", "8. name: error, type: Bool, initial: FALSE, role: The output parameter that indicates if an error has occurred.", "9. name: status, type: Word, initial: None, role: The output parameter that holds the status of the function block.", "10. name: subFunctionStatus, type: Word, initial: None, role: The output parameter that holds the status or return value of called FB's, FC's, and system blocks.", "11. name: statRad, type: Real, initial: None, role: A variable used to convert the counter to radians for the SIN function.", "12. name: statPhaseShift, type: Real, initial: 0.0, role: A variable used to store the calculated phase shift in radians.", "13. name: statCounter, type: UDInt, initial: None, role: A variable used to keep track of the time counter for generating the sinusoidal signal.", "14. name: tempCycleTime, type: UDInt, initial: None, role: A temporary variable used to store the cyclic interrupt OB's cycle time.", "15. name: tempCyclePhase, type: UDInt, initial: None, role: A temporary variable used to store the cyclic interrupt OB's phase.", "16. name: tempCycleStatus, type: Word, initial: None, role: A temporary variable used to store the status of the cyclic interrupt OB.", "17. name: tempReadTimeStatus, type: Int, initial: None, role: A temporary variable used to store the status of the QRY_CINT function call.", "18. name: SECOND_IN_MS, type: UDInt, initial: 1000, role: A constant that defines the number of milliseconds in one second.", "19. name: ZERO, type: Int, initial: 0, role: A constant used for comparisons.", "20. name: SLOPE, type: Int, initial: 2, role: A constant used in calculations, possibly for scaling.", "21. name: TWO_PI, type: Real, initial: 6.283185, role: A constant representing the value of 2 times pi.", "22. name: SUB_STATUS_NO_ERROR, type: Word, initial: 16#0000, role: A constant representing the status code for no error.", "23. name: STATUS_FINISHED_NO_ERROR, type: Word, initial: 16#0000, role: A constant representing the status code for finished with no error.", "24. name: QRY_CINT_OB_UNAVAILABLE, type: Word, initial: 16#0000, role: A constant representing the status code when OB is unavailable.", "25. name: ERR_OB_UNAVAILABLE, type: Word, initial: 16#8600, role: A constant representing the error code for OB unavailable.", "26. name: ERR_QRY_CINT, type: Word, initial: 16#8601, role: A constant representing the error code for QRY_CINT function error."], "instructions": ["QRY_CINT", "UDINT_TO_REAL", "MOD", "SIN", "INT_TO_WORD"], "planning": "Step1. Check if the reset input is set to TRUE, if so, reset the statCounter to 0 and set the value output to 0.\nStep2. If reset is not TRUE, increment the statCounter based on the tempCycleTime and convert it to a value within one period using MOD.\nStep3. Convert the statCounter to radians and calculate the phase shift in radians.\nStep4. Calculate the current value of the sinusoidal signal using the SIN function and assign it to the value output.\nStep5. Set the error output to FALSE, status output to STATUS_FINISHED_NO_ERROR, and subFunctionStatus output to SUB_STATUS_NO_ERROR.\nStep6. If there is an error in reading the cyclic interrupt OB time (QRY_CINT), set the error and status outputs accordingly and return.\nStep7. If the cyclic interrupt OB is not available, set the error and status outputs accordingly and return.", "name": "LGF_SinusCI"}
"""
alternatives = []
alternatives.append(alternativeProcess1)
alternatives.append(alternativeProcess2) 
alternatives.append(alternativeProcess3)
# print(alternatives)

def planning_agent(requirements: str, retrival_data):
    """
    #requirements: 当前任务描述 relatedCases: 相关算法流程分析 jsons: 相关算法源代码
    ## 【输入】 任务需求;样例需求和样例代码;常见函数库
    ## 【执行】 分析样例代码如何满足样例需求
    ##         分析自己的任务需求
    ##         分析完成需求需要的函数
    ## 【输出】 算法流程；需要的函数名
    """
    # relate_cases = f""" Here is a collection of related case descriptions structured in JSON array format:
    # {relateCases}
    # """
    relatedCases = []
    # 提取所有的 name 字段
    names = [item['name'] for item in retrival_data]
    for name in names:
        fileContent = get_files_content_with_string(name, names.index(name))
        json_data = json.loads(fileContent)
        # 提取 'planning' 字段
        planning_content = json_data.get('planning', None)
        relatedCases.append(planning_content)
        
    # print(relatedCases)
    # retrieval_agent_prompt_user = f"""Here is a task requirement description, structured in JSON format: 
    #     {requirements}
    # """
    retrieval_agent_prompt_user = requirements
    api_key = glovar.API_KEY_AIRX
    client = ZhipuAI(api_key=api_key)
    msgs = [ {"role": "system", "content": state_machine_prompt} ]
    # for tem in retrival_data:
        # print(tem)
        # print('-'*80)
    # for user,ass in list(zip(retrival_data, relatedCases)):
    #     msgs.append({"role": "user", "content": str(user['json_desc'])})
    #     msgs.append({"role": "assistant", "content": str(ass)})
    msgs.append({"role": "user", "content": retrieval_agent_prompt_user})
    response = client.chat.completions.create(
        model="glm-4-airx",  # 填写需要调用的模型名称
        temperature=0.25,
        top_p=0.8,
        messages=msgs,
    )
    res = response.choices[0].message.content
    with open('./output/planning_agent_test.txt', 'w', encoding='utf8') as f:
        f.write(response.choices[0].message.content)
    
    return res,relatedCases

def extract_names_from_file(file_path):
    # Read the content of the file
    with open(file_path, 'r') as file:
        content = file.read()

    # Load the JSON data from the content
    json_data = json.loads(content)
    pre_data = json_data
    # Extract "name" values from the JSON data
    names = []
    for item in json_data:
        if 'name' in item:
            names.append(item['name'])
    # print(names)
    return names, pre_data

def get_files_content_with_string(search_str, number):      #这个number标记函数是第几次被调用，进而返回alternatives对应项
    directory = f"{glovar.RAG_DATA_DIR}/scl_case_plan_0520_zh_region/"
    content = None  # 初始化content变量
    file_found = False  # 添加一个标志来检查是否找到了文件
    for root, dirs, files in os.walk(directory):
        for file in files:
            if search_str in file:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    print(f"读取文件 {file_path} 时发生错误: {e}")
                    content = None
                file_found = True  # 设置标志表示文件已找到
                break  # 由于只有一个匹配结果，找到后即可退出循环
        if file_found:
            break  # 如果文件已找到，退出外层循环
        else:
            content = alternatives[number]
    # print(alternatives[number])
    # print(content)  # 现在content已经被赋值，或者为None
    return content

def refine_agent(task_requirement, alogrithm_process):
    api_key = glovar.API_KEY_AIRX
    client = ZhipuAI(api_key=api_key)
    msgs = [ {"role": "system", "content": list_problem_prompt} ]
    # for tem in retrival_data:
        # print(tem)
        # print('-'*80)
    # msgs.append({"role": "user", "content": "任务描述：" + str(task_requirement) +"\n\n 算法流程" + str(alogrithm_process)})
    msgs.append({"role": "user", "content": f"""
输入为xml格式:
<任务描述>
{str(task_requirement)}
</任务描述>
<算法流程>
{alogrithm_process}
</算法流程>
"""})
    
    response = client.chat.completions.create(
        model="glm-4-airx",  # 填写需要调用的模型名称
        temperature=0.75,
        top_p=0.25,
        max_tokens=8 * 1000,
        messages=msgs,
        # stream=True,
    )
    res = response.choices[0].message.content
    substring = "----细化后的算法流程----"
    # 找到子串的位置
    index = res.find(substring)
    # 检查子串是否在原始字符串中
    part_after_substring = res[index + len(substring):]
    print(part_after_substring)
    return part_after_substring

def planning_process(task_information, retrival_data):
    nl_task_requirements = prettify_task(task_information)
    planning_result,related_algorithm = planning_agent(nl_task_requirements, retrival_data)
    refine_result = refine_agent(nl_task_requirements, planning_result)
    return refine_result,related_algorithm

# if __name__ == '__main__':
#     retrievalFileName = "./output/retrive_test_logs/retreival_agent_next.txt"
#     res, retrival_data = extract_names_from_file(retrievalFileName)
#     sample_analysis = []
#     # print(res)
#     for name in res:
#         fileContent = get_files_content_with_string(name, res.index(name))
#         json_data = json.loads(fileContent)
# # 提取 'planning' 字段
#         planning_content = json_data.get('planning', None)
#         sample_analysis.append(planning_content)

#     # test_prompt = """
#     #     {"title":"特殊堆栈","description":"编写一个函数块FB，实现一个特殊堆栈功能，在出栈时移除栈内的最小值。\n1. 入栈操作：当新元素入栈时，首先检查栈是否为满。如果栈为满，则不进行任何操作。否则，将其添加到数组的栈顶位置，并更新栈顶位置。\n2. 出栈操作：当执行出栈操作时，首先检查栈是否为空。如果栈为空，则不进行任何操作。否则，移除栈内的最小值，并返回该元素的值，同时更新栈顶位置。\n状态代码：\n16#0000：执行FB没有出错\n16#8A04：堆栈是满的\n16#8A05：堆栈是空的","type":"FUNCTION_BLOCK","name":"StackMin","input":[{"name":"push","type":"Bool","description":"入栈操作，在栈未满的情况下，将一个元素添加到栈内"},{"name":"pop","type":"Bool","description":"出栈操作，在栈不空的情况下，从栈内移除最小值元素，并返回该元素的值。"},{"name":"reset","type":"Bool","description":"复位操作，栈顶位置将被重置。"}],"output":[{"name":"error","type":"Bool","description":"FALSE: 没有发生错误; TRUE: 执行FB时出错"},{"name":"status","type":"Word","description":"状态代码"}],"in_out":[{"name":"item","type":"Int","description":"用于入栈或从栈内返回的值"},{"name":"stack","type":"Array[0..3] of Int","description":"用于作为栈的数组"}],"prompt":"<任务标题>特殊堆栈</任务标题>\n        <任务描述>编写一个函数块FB，实现一个特殊堆栈功能，在出栈时移除栈内的最小值。\n1. 入栈操作：当新元素入栈时，首先检查栈是否为满。如果栈为满，则不进行任何操作。否则，将其添加到数组的栈顶位置，并更新栈顶位置。\n2. 出栈操作：当执行出栈操作时，首先检查栈是否为空。如果栈为空，则不进行任何操作。否则，移除栈内的最小值，并返回该元素的值，同时更新栈顶位置。\n状态代码：\n16#0000：执行FB没有出错\n16#8A04：堆栈是满的\n16#8A05：堆栈是空的</任务描述>\n\n        <函数名称> StackMin</函数名称>\n        <函数类型> FUNCTION_BLOCK</函数类型>\n        <输入参数>\n - 名称: push, 类型: Bool, 描述: 入栈操作，在栈未满的情况下，将一个元素添加到栈内\n - 名称: pop, 类型: Bool, 描述: 出栈操作，在栈不空的情况下，从栈内移除最小值元素，并返回该元素的值。\n - 名称: reset, 类型: Bool, 描述: 复位操作，栈顶位置将被重置。\n</输入参数>\n<输出参数>\n - 名称: error, 类型: Bool, 描述: FALSE: 没有发生错误; TRUE: 执行FB时出错\n - 名称: status, 类型: Word, 描述: 状态代码\n</输出参数>\n<返回值>\n</返回值>","sample_io":[],"sample_io_prompt":""}

#     # """    
#     test_prompt = """
#     {"title":"FIFO先进先出队列","description":"编写一个函数块FB，实现一个先进先出（FIFO）循环队列的功能，其中队列的最大长度和数据类型都是可变的。循环队列应能够支持以下操作：\n\n1. 入队操作（enqueue）：在队列未满的情况下，将一个元素添加到队列的队尾。\n2. 出队操作（dequeue）：在队列不空的情况下，从队列的队首移除一个元素，并返回该元素的值。\n3. 判断队列是否为空：检查队列中是否没有元素。\n4. 判断队列是否已满：检查队列是否已达到最大容量。\n5. 获取队列元素数量：返回队列中当前元素的数量。\n状态代码：\n16#0000：执行FB没有出错\n16#8001：队列是空的\n16#8002：队列是满的","type":"FUNCTION_BLOCK","name":"FIFO","input":[{"name":"enqueue","type":"Bool","description":"入队操作，在队列未满的情况下，将一个元素添加到队列的队尾"},{"name":"dequeue","type":"Bool","description":"出队操作，在队列不空的情况下，从队列的队首移除一个元素，并返回该元素的值。"},{"name":"reset","type":"Bool","description":"复位操作，复位头尾指针，元素计数（elementCount）输出被设置为零，并且isEmpty输出被设置为TRUE。"},{"name":"clear","type":"Bool","description":"清除操作，复位头尾指针，队列将被清空并用初始值initialItem进行初始化。元素计数（elementCount）输出被设置为零，并且isEmpty输出被设置为TRUE。"},{"name":"initialItem","type":"Variant","description":"用于初始化队列的值"}],"output":[{"name":"error","type":"Bool","description":"FALSE:没有发生错误 TRUE:执行FB时出错"},{"name":"status","type":"Word","description":"状态代码"},{"name":"elementCount","type":"DInt","description":"队列中元素的数量"},{"name":"isEmpty","type":"Bool","description":"当为TRUE时表示队列是空的"}],"in/out":[{"name":"item","type":"Variant","description":"用于加入队列或从队列返回的值"},{"name":"buffer","type":"Variant","description":"用于作为队列的数组"}],"status_codes":{"16#0000":"执行FB没有出错","16#8001":"队列是空的","16#8002":"队列是满的"},"prompt":"<任务标题>FIFO先进先出队列</任务标题>\n        <任务描述>编写一个函数块FB，实现一个先进先出（FIFO）循环队列的功能，其中队列的最大长度和数据类型都是可变的。循环队列应能够支持以下操作：\n\n1. 入队操作（enqueue）：在队列未满的情况下，将一个元素添加到队列的队尾。\n2. 出队操作（dequeue）：在队列不空的情况下，从队列的队首移除一个元素，并返回该元素的值。\n3. 判断队列是否为空：检查队列中是否没有元素。\n4. 判断队列是否已满：检查队列是否已达到最大容量。\n5. 获取队列元素数量：返回队列中当前元素的数量。\n状态代码：\n16#0000：执行FB没有出错\n16#8001：队列是空的\n16#8002：队列是满的</任务描述>\n\n        <函数名称> FIFO</函数名称>\n        <函数类型> FUNCTION_BLOCK</函数类型>\n        <输入参数>\n - 名称: enqueue, 类型: Bool, 描述: 入队操作，在队列未满的情况下，将一个元素添加到队列的队尾\n - 名称: dequeue, 类型: Bool, 描述: 出队操作，在队列不空的情况下，从队列的队首移除一个元素，并返回该元素的值。\n - 名称: reset, 类型: Bool, 描述: 复位操作，复位头尾指针，元素计数（elementCount）输出被设置为零，并且isEmpty输出被设置为TRUE。\n - 名称: clear, 类型: Bool, 描述: 清除操作，复位头尾指针，队列将被清空并用初始值initialItem进行初始化。元素计数（elementCount）输出被设置为零，并且isEmpty输出被设置为TRUE。\n - 名称: initialItem, 类型: Variant, 描述: 用于初始化队列的值\n</输入参数>\n<输出参数>\n - 名称: error, 类型: Bool, 描述: FALSE:没有发生错误 TRUE:执行FB时出错\n - 名称: status, 类型: Word, 描述: 状态代码\n - 名称: elementCount, 类型: DInt, 描述: 队列中元素的数量\n - 名称: isEmpty, 类型: Bool, 描述: 当为TRUE时表示队列是空的\n</输出参数>\n<返回值>\n</返回值>","sample_io":[],"sample_io_prompt":""}
#     """
#     agentResult = planning_agent(prettify_task(test_prompt), retrival_data)
#     # print(agentResult)
	
