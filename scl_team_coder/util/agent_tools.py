import json
import re
import os
import codecs
from zhipuai import ZhipuAI
import time
from scl_team_coder import glovar
import traceback
## 一些常量
# api_key = '42253decc3d85bad61464e9f5813cfc4.GicxpDMXwGZVEzA7'
# client = ZhipuAI(api_key=api_key) # 请填写您自己的APIKey
# REGION Initialization
#     // initialize variable in VAR_TEMP here if necessary
#     // don't modify variable in INPUT or IN/OUT illegally
#     // if no need, delete this region
# END_REGION
# 1.请使用 `16#0000` 的语法格式定义16进制常量，而不是 `0x0` !
# 2.如果函数接受多个参数，请明确指定输入参数和输出参数。 如 `SHR(IN:=Tag_Value,N:=Tag_Number)`。
# 3.如果函数接受一个参数，请采用匿名参数形式，如 `LEN(#TempArray)` 。
# 4.禁止使用三元表达式!禁止使用 `? :` 作为条件表达式。
# 5.请使用`FOR #start TO #end BY -1 DO ..`来执行【逆序】遍历。
# 6.请在`VAR_TEMP...EDN_VAR`块中定义FOR循环中使用的所有循环变量(比如`TEMP_i`)
# 7.请按照示例代码使用`SHR()`执行右移操作。使用`SHL()`执行左移操作。
# 8.编写控制类型程序(Control)时(如控制传送带、控制机械臂)时,记得保持上一周期的状态,除非有新的输入信号改变状态。如果需要检测“跳变”、“上升沿”或“下降沿”，你应当使用【静态变量】保存每个周期的输入状态state，再与下一周期的输入进行比较(`IF state and not oldsState`)以确定是否发生跳变。
# 9.在`VAR...END_VAR`中定义Array和Struct类型的常量。在`VAR CONSTANT...END_VAR`中定义其他类型的常量。
# 10.不允许使用SCL-1200/SCL-1500编程中不存在的语法。
# 11.请将强制类型转换函数BYTE()换成类似`INT_TO_BYTE(#byte_variable)`的【显式类型转换】函数。其他类型的赋值操作类似。
# 12.不要自己定义函数。使用朴素的循环、分支、顺序结构实现目标。
programming_guidance = """
1.请使用 `16#0000` 的语法格式定义16进制常量，而不是 `0x0` !
2.如果函数接受多个参数，请明确指定输入参数和输出参数。 如 `#result := SHR(IN := #ValueForSHR,N := #NumberOfShift)`。
3.如果函数接受一个参数，请采用匿名参数形式，如 `#result := LEN(#TempString)` 。
4.禁止使用三元表达式!禁止使用 `<expr> ? <result1> : <result2>;` 作为条件表达式。
5.使用`FOR <Run_tag> := <Start_value> TO <End_value> BY <Increment> DO <Instructions>;END_FOR;`来执行FOR循环。FOR 语句中不允许组合使用带符号整数(如`DINT`)和不带符号整数(如`UDINT`)。使用不带符号整数时，无法编程负方向循环。
6.请在`VAR_TEMP...EDN_VAR`块中定义FOR循环中使用的所有循环变量(比如`TEMP_i`)
7.请按照示例代码使用`SHR()`执行右移操作。使用`SHL()`执行左移操作。
8.编写控制类型程序(Control)时(如控制传送带、控制机械臂)时,记得保持上一周期的状态,除非有新的输入信号改变状态。如果需要检测“跳变”、“上升沿”或“下降沿”，你应当使用【静态变量】保存每个周期的输入状态state，再与下一周期的输入进行比较(`IF state and not oldsState`)以确定是否发生跳变。
9.在`VAR/END_VAR`中定义Array和Struct类型的常量。在`VAR CONSTANT...END_VAR`中定义其他类型的常量。
10.不允许使用西门子 S7 PLC编程中不存在的语法。
11.请将强制类型转换函数BYTE()换成类似`INT_TO_BYTE(#byte_variable)`的【显式类型转换】函数。将`REAL()`换为`INT_TO_REAL()`。其他类型的赋值操作类似。
12.不要自己定义函数。使用朴素的循环、分支、顺序结构实现目标。
13.使用`取地址操作`访问和修改位字段。如希望访问整数的字，可以使用`#byte1 := #inputNum.%B1;`。如希望设置Dword类型的字，可以使用`#tempDWord.%B1 := #byte1;`
15.将`Bool`类型的变量与整数(`Byte`,`Int`,`DInt`,`UDInt`,`USInt`等)或字符串(`String`等)类型进行运算时,必须使用`类型转换函数`如`BOOL_TO_INT(#boolValue)`。
16.不允许出现空ELSE块。请删除空ELSE块或添加至少一条表达式<statement>。
17.如果需要处理可变长度数组(Array[*]),可以使用`UPPERBOUND`和`LOWERBOUND`获取长度
"""
# 17.如果需要处理多种数据类型(Variant),可以使用`CASE TypeOf(#value) OF`或者`IF <expr> THEN /ELSIF`来根据不同类型执行对应操作。
# 14.使用`UPPER_BOUND()`和`LOWER_BOUND()`获取ARRAY[*]的上下界;使用`LEN`获取String的长度;使用`CountOfElements`获取Variant指向的可变数组的长度。
# 11.请将强制类型转换函数BYTE()换成类似`INT_TO_BYTE(#byte_variable)`的【显式类型转换】函数。将`REAL()`换为`INT_TO_REAL()`。其他类型的赋值操作类似。
# 13.`UNTIL`循环需要以`END_REPEAT`结束。
# 12.不要自己定义函数。使用朴素的循环、分支、顺序结构实现目标。
# 8.PLC按固定的扫描周期（毫秒级）执行输入读取、逻辑控制和输出更新，确保控制系统的实时性和稳定性。在每个扫描周期内，PLC会保持上一周期的状态，除非有新的输入信号改变状态。这保证了系统的稳定运行，不会因短暂信号波动而误动作。因此编写控制类型程序(Control)时(如控制传送带、控制机械臂)，确保每个扫描周期内检查并保持历史状态，以便在没有新信号时维持现有状态。这样可以确保系统稳定且响应及时。
# 6.请使用合法的数学运算符。不允许使用`//`运算符【整除】。不允许使用`>>`运算符【右移】。
# 10.FUNCTION BLOCK块在测试时每个周期都会被调用。因此编写控制类型程序(Control)时(如控制传送带、控制机械臂)需要使用静态变量保存上一周期结束时的控制状态。本周期初始化时,先将静态变量赋值给OUTPUT变量(你需要维持历史状态,你也不想造成传送带断电等工业伤亡事故吧？),再根据触发信号修改OUTPUT变量。
# 9.请将强制类型转换函数BYTE()换成类似`INT_TO_BYTE(byte_variable)`的【显式类型转换】函数。其他类型的赋值操作类似。
# 5.请在变量声明时使用字面量(如常数)初始化，
# 7.请使用`:=`进行赋值。
# 11.请按照示例代码正确使用`SHR()`和`SHL()`完成移位操作。
# - 编写控制类型程序(Control)时(如控制传送带、控制机械臂)需要使用静态变量保存上一周期结束时的控制状态。如果触发信号没有修改输出变量,则将旧状态赋值给输出变量(你需要维持历史状态,你也不想造成传送带断电等工业伤亡事故吧？)

functionblock = f"""
BEGIN
    REGION Validation of INPUT and OUTPUT 
        // validate input and output here if necessary
    END_REGION

    // main function logic here
    REGION <name>
        // you should name the REGION properly
    END_REGION

    REGION Writting to outputs
        // assign your output variable here if necessary
    END_REGION
"""

with open(f"{glovar.RAG_DATA_DIR}/instructions/dict_new_instruction_165_brief_description.json",'r') as fp:
    api_detail_dict = json.load(fp)

with open(f"{glovar.RAG_DATA_DIR}/data/通用函数库/new_functions_usage.json",'r') as fp:
    functions_usage = json.load(fp)

with open(f"{glovar.RAG_DATA_DIR}/data/Keywords.json",'r') as fp:
    Keywords = json.load(fp)
    
def write_jsonl(data, output_path):
    with open(output_path, 'a+', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')
        
def read_jsonl(filename):
    """Reads a jsonl file and yields each line as a dictionary"""
    lines = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            lines.append(json.loads(line))
    return lines
import os

def apply_patch(scl_code:str,patch:str):
    with open("./tmp/buggy_code.scl","w") as fp:
        fp.write(scl_code)
    with open("./tmp/fix.patch","w") as fp:
        fp.write(patch)
    os.system("patch ./tmp/buggy_code.scl ./tmp/fix.patch --verbose")
    with open("./tmp/buggy_code.scl","r") as fp:
        fix_code = fp.read()    
    os.remove('./tmp/buggy_code.scl')
    os.remove('./tmp/fix.patch') 
    return fix_code

common_apis = read_jsonl(f"{glovar.RAG_DATA_DIR}/instructions/brief_instruction_description common.jsonl")
common_api_list = [api['instruction_name'] for api in common_apis]

def get_api_details(case_names:list[str],other_api_names:list[str]=[],nl_task_requirements:str=""):
    api_details = {}
    data_tranforms = []
    ##　专家推荐
    if "Variant" in nl_task_requirements:
        other_api_names.extend(['TypeOf',"VariantGet","VariantPut"])
    if "Variant" in nl_task_requirements and "数组" in nl_task_requirements:
        other_api_names.extend(['TypeOfElements','CountOfElements',"IS_ARRAY","MOVE_BLK_VARIANT"])
    if "可变长度" in nl_task_requirements or "Array" in nl_task_requirements:
        other_api_names.extend(['UPPER_BOUND','LOWER_BOUND'])
    if "String" in nl_task_requirements:
        other_api_names.extend(['LEN','FIND'])
    if "时间" in nl_task_requirements or "超时" in nl_task_requirements:
        other_api_names.extend(['TON','TOF','TP','TONR'])
    if "移位" in nl_task_requirements:
        other_api_names.extend(['SHR','SHL'])
    if "复制" in nl_task_requirements:
        other_api_names.extend(['MOVE_BLK','MOVE_BLK_VARIANT'])
    ##　专家知识
    for name in case_names:
        if name in functions_usage:
            case_used_functions = functions_usage[name]
            for api in case_used_functions:
                if api in api_detail_dict and api in common_api_list: # 功能api
                    api_details[api] = api_detail_dict[api]
                elif "_TO_" in api: # 类型转换api
                    data_tranforms.append(api)
    for api in other_api_names:
        if api in api_detail_dict: # 其他需要加入的api
            api_details[api] = api_detail_dict[api]
    api_details_str = ""
    count= 1
    for api_name,api in api_details.items():
        api_details_str += f"""{count}. {prettify_api(api)}\n"""
        count+=1
    for data_api in data_tranforms:
        data_from,data_to = data_api.split('_TO_')
        api_details_str += f"""\n{count}. {data_api}() : 将{data_from}类型转换为\{data_to}类型\n"""
        count+=1
    api_details_str += '\n'
    return api_details_str,api_details


def parse_patch(text:str):
    pattern = re.compile(
        r'<code_segment>(.*?)</code_segment>\s*<patch>(.*?)</patch>', 
        re.DOTALL
    )
    # 搜索所有匹配项
    matches = pattern.findall(text)
    # 创建一个列表来存储结果
    results = []
    # 遍历匹配项并填充列表
    for buggy, patch in matches:
        results.append((buggy.strip(), patch.strip()))
    # 打印结果列表
    return results

def parse_response(response: str) -> str:
    """
    Retriving the code blocks from the response.
    """
    # print(response)
    # start_time = time.time()
    # response = response.replace("```scl", "").replace("```plaintext", "")\
    #                 .replace("```json", "").replace("```", "")
    # end_time = time.time()
    # execution_time = end_time - start_time
    # print(f"parse_response耗时: {execution_time:.6f} 秒")
    # return response

    code_pattern = r'```((.|\n)*?)```'
    if "```scl" in response:
        code_pattern = r'```scl((.|\n)*?)```'
    elif "```plaintext" in response:
        code_pattern = r'```plaintext((.|\n)*?)```'
    elif "```st" in response:
        code_pattern = r'```st((.|\n)*?)```'
    elif "```json" in response:
        code_pattern = r'```json((.|\n)*?)```'
    else:
        response = response.replace("```scl", "").replace("```plaintext", "")\
                        .replace("```json", "").replace("```", "")
        return response

    code_blocks = re.findall(code_pattern, response, re.DOTALL)

    if len(code_blocks) == 0:
        response = response.replace("```scl", "").replace("```plaintext", "")\
                           .replace("```json", "").replace("```", "")
        return response
    elif type(code_blocks[-1]) == tuple or type(code_blocks[-1]) == list:
        code_str = "\n".join(code_blocks[-1])
    elif type(code_blocks[-1]) == str:
        code_str = code_blocks[-1]
    else:
        code_str = response

    return code_str

def get_status_code_from_desc(spec):
    example_input1 = """
    编写一个函数FC，实现两个矩阵的加法功能。\n\n该函数接受两个可变长度的二维浮点数数组matrix1和matrix2作为输入参数。函数应检查两个输入矩阵以及用于返回结果的输出矩阵是否具有相同的行数和列数，如果不相同，则返回错误状态和特定的错误代码。\n\n状态代码：\n16#0000：执行FB没有出错\n16#8200：第一矩阵数组行的下界值与第二矩阵行的下界值不同\n16#8201：第一矩阵数组行的下界值与结果矩阵行的下界值不同\n16#8202：第一矩阵数组列的下界值与第二矩阵列的下界值不同\n16#8203：第一矩阵数组列的下界值与结果矩阵列的下界值不同\n16#8204：第一矩阵数组行的上界值与第二矩阵行的上界值不同\n16#8205：第一矩阵数组行的上界值与结果矩阵行的上界值不同\n16#8206：第一矩阵数组列的上界值与第二矩阵列的上界值不同\n16#8207：第一矩阵数组列的上界值与结果矩阵列的上界值不同
    """
    example_output1 = """
    ```json
    {
        \"status_codes\": {
            \"16#0000\": \"执行FB没有出错\",
            \"16#8200\": \"第一矩阵数组行的下界值与第二矩阵行的下界值不同\",
            \"16#8201\": \"第一矩阵数组行的下界值与结果矩阵行的下界值不同\",
            \"16#8202\": \"第一矩阵数组列的下界值与第二矩阵列的下界值不同\",
            \"16#8203\": \"第一矩阵数组列的下界值与结果矩阵列的下界值不同\",
            \"16#8204\": \"第一矩阵数组行的上界值与第二矩阵行的上界值不同\",
            \"16#8205\": \"第一矩阵数组行的上界值与结果矩阵行的上界值不同\",
            \"16#8206\": \"第一矩阵数组列的上界值与第二矩阵列的下界值不同\",
            \"16#8207\": \"第一矩阵数组列的上界值与结果矩阵列的下界值不同\"
        }
    }
    ```
    """
    example_input2 = """
    编写一个函数块FB，实现一个先进先出（FIFO）循环队列的功能，其中队列的最大长度和数据类型都是可变的。循环队列应能够支持以下操作：\n\n1. 入队操作（enqueue）：在队列未满的情况下，将一个元素添加到队列的队尾。\n2. 出队操作（dequeue）：在队列不空的情况下，从队列的队首移除一个元素，并返回该元素的值。\n3. 判断队列是否为空：检查队列中是否没有元素。\n4. 判断队列是否已满：检查队列是否已达到最大容量。\n5. 获取队列元素数量：返回队列中当前元素的数量。    """
    example_output2 = """
    ```json
    {
        \"status_codes\": {
        }
    }
    ```    
    """
    message = [
        {"role": "system", "content": '根据文本输出json格式的状态数字描述。不要输出文本中不存在的数字。'},
        {"role": "user", "content":example_input1},
        {"role": "assistant", "content":example_output1},        
        {"role": "user", "content":example_input2},
        {"role": "assistant", "content":example_output2},        
        {"role": "user", "content":spec['description']},
    ]
    response = client.chat.completions.create(
        model='glm-4-Flash',  # 填写需要调用的模型名称
        max_tokens=9182,
        temperature=0.01,
        messages=message
    )

    status_code_str = parse_response(response.choices[0].message.content)
    try :
        status_code_dict = json.loads(status_code_str)
    except :
        print('oops!',status_code_str)
        status_code_dict = {
            "status_codes":{}
        }
    return status_code_dict

def get_status_code(spec):
    example_input1 = """
    {
        \"16#0000\": \"执行FB没有出错\",
        \"16#8001\": \"队列是空的\",
        \"16#8002\": \"队列是满的\"
    }
    """
    example_output1 = """
    ```scl
    VAR CONSTANT
        STATUS_NO_ERROR : Word := 16#0000; // 执行FB没有出错
        ERR_BUFFER_EMPTY : Word := 16#8001; // 队列是空的
        ERR_BUFFER_FULL : Word := 16#8002; // 队列是满的
    END_VAR
    ```
    """
    # print(spec['status_codes'])
    message = [
        {"role": "system", "content": '您是 SCL（结构化控制语言）专家。努力根据我的输入生成状态码变量定义。注意类型必须为WORD。注意不能生成其他逻辑代码'},
        {"role": "user", "content":example_input1},
        {"role": "assistant", "content":example_output1},
        {"role": "user", "content":spec['status_codes'] },
    ]
    response = client.chat.completions.create(
        model='glm-4-Flash',  # 填写需要调用的模型名称
        max_tokens=4096,
        temperature=0.01,
        messages=message
    )
    return parse_response(response.choices[0].message.content)

def remove_braces(code):
    code = code.replace("{ S7_Optimized_Access := 'TRUE' }","HELLOWORLD")
    code = re.sub(r'\{.*?\}', '', code)
    code = code.replace("HELLOWORLD","{ S7_Optimized_Access := 'TRUE' }")
    return code    
    
def trasnform_example_code_to_template(code):

    # 定义需要替换的区域
    function_block_pattern = r'BEGIN\s+(.*?)(?=END_FUNCTION_BLOCK|END_FUNCTION)'
    
    # 清空VAR、VAR_TEMP、VAR_CONSTANT定义
    # code = re.sub(r'(VAR[ \t\n]*).*?(END_VAR)', r'\1// define your temp variables here\n   \2', code, flags=re.DOTALL)
    code = re.sub(r'(VAR_TEMP\s*).*?(END_VAR)', r'\1// define your temp variables here\n   \2', code, flags=re.DOTALL)
    code = re.sub(r'(VAR CONSTANT\s*).*?(END_VAR)', r'\1// define status codes and your constant variables here please\n   \2', code, flags=re.DOTALL)
    
    # 替换BEGIN...END_FUNCTION_BLOCK/END_FUNCTION的内容
    code = re.sub(function_block_pattern, functionblock, code, flags=re.DOTALL)
    
    # 移除花括号
    code = remove_braces(code)
    return code

def fileds_to_struct_define(dict_data):
    result = f"{    dict_data['name']} : {dict_data['type']}\n"
    if isinstance(dict_data['fields'],list):
        for field in dict_data['fields']:
            if 'fields' in field:
                result += fileds_to_struct_define(field)
            else:
                result += f"    {field['name']} : {field['type']};\n"
    elif isinstance(dict_data['fields'],dict):
        for key,field in dict_data['fields'].items():
            if 'fields' in field:
                result += fileds_to_struct_define(field)
            else:
                result += f"    {key} : {field['type']};\n"
    else:
        result += "// define struct according to given requirements.\n"
    result += "    END_STRUCT;\n"
    return result

def user_type_to_struct_define(io_list, user_defined_types):
    for item in io_list:
        if item['type'] in user_defined_types:
            item['fields'] = user_defined_types.get(item['type'], "").get('member', [])
            item['type'] = 'Struct'

def remove_double_slash_comments(code):
    # 匹配以 // 开头的注释
    code = re.sub(r'//.*\n', '\n', code)
    return code

def get_code_template(file_path=None,task=None):
    if task is not None:
        spec = task
    else:
        with open(file_path,'r',encoding='utf-8 sig') as fp:
            spec = json.load(fp)
    # status_code_dict = get_status_code_from_desc(spec)
    # if 'status_codes' in spec:
    #     spec['status_codes'] = spec['status_codes'] | status_code_dict
    # else:
    #     spec['status_codes'] = status_code_dict
    # spec['status_codes'] = {}
    # 处理用户定义类型
    try:
        user_defined_types = {
            user_type['name']: user_type
            for user_type in spec.get('user_defined_types', [])
        }
        # print(user_defined_types)
        # 处理输入、输出和输入/输出
        for io_type in ['input', 'output', 'in/out']:
            if io_type in spec:
                for item in spec[io_type]:
                    item['description'] = item['description'].replace("\n",'。')
                user_type_to_struct_define(spec[io_type], user_defined_types)
        ## 处理用户定义类型
        # print(task['name'],f"1")
    except Exception as e:
        print(spec['name'],e)
        traceback.print_exc()
    
    try:
        if spec['type'] == 'FUNCTION_BLOCK':
            head = f"FUNCTION_BLOCK \"{spec['name']}\"\n"
        elif spec['type'] == 'FUNCTION':
            head = f"FUNCTION \"{spec['name']}\" : <return type>\n"
            if "return_value" in spec and len(spec["return_value"])>0:
                head = head.replace("<return type>",spec["return_value"][0]['type'])
            else:
                head = head.replace("<return type>","Void")
        else:
            head = '<you need to define head accoring to given requirement.>\n'
    except Exception as e:
        print(spec['name'],e)
        traceback.print_exc()
        head = '<you need to define head accoring to given requirement.>\n'

    head += '{ S7_Optimized_Access := \'TRUE\' }\n'

    try:
        # Input variables
        var_input = "VAR_INPUT\n// define input variables accoring to given requirement. don't change here!\n"
        if 'input' in spec:
            for inp in spec['input']:
                if 'fields' in inp:
                    var_input += fileds_to_struct_define(inp)
                else:
                    if inp['name'].upper() in Keywords:
                        var_input += f"    \"{inp['name']}\" : {inp['type']};\n"
                    else:
                        var_input += f"    {inp['name']} : {inp['type']};\n"  
        var_input += "END_VAR\n\n"
        # print(task['name'],f"2")
        # Output variables
    except Exception as e:
        var_input = "VAR_INPUT\n//define input variables accoring to given requirement.\nEND_VAR\n\n"
        print(spec['name'],e)
        traceback.print_exc()

    try:
        var_output = "VAR_OUTPUT\n// Ouput variables you should write to. don't change here!\n"
        if 'output' in spec:
            for out in spec['output']:
                if 'fields' in out:
                    var_output += fileds_to_struct_define(out)
                else:
                    if out['name'].upper() in Keywords:
                        var_output += f"    \"{out['name']}\" : {out['type']};\n"
                    else:
                        var_output += f"    {out['name']} : {out['type']};\n"   
                                        
        var_output += "END_VAR\n\n"
    except Exception as e:
        var_output = "VAR_OUTPUT\n//define output variables accoring to given requirement.\nEND_VAR\n\n"
        print(spec['name'],e)
        traceback.print_exc()    

    try:
        # print(task['name'],f"3")
        # In/Out variables
        if 'in/out' in spec:
            var_inout = "VAR_IN_OUT\n// These variables are already storing IMPORTANT data, do not initialize them unless you are quite sure that the operation is safe.\n"
            for inout in spec['in/out']:
                if 'fields' in inout:
                    var_inout += fileds_to_struct_define(inout)
                else:
                    if inout['name'].upper() in Keywords:
                        var_inout += f"    \"{inout['name']}\" : {inout['type']};\n"
                    else:
                        var_inout += f"    {inout['name']} : {inout['type']};\n"
            var_inout += "END_VAR\n\n"
        else:
            var_inout = ""
    except Exception as e:
        var_inout = "VAR_IN_OUT\n// you can define in/out variables accoring to given requirement.\n"
        print(spec['name'],e)
        traceback.print_exc()

    # print(task['name'],f"4")
    # Constant variables for status codes
    var_constant = "VAR CONSTANT\n"
    # if len(spec['status_codes'].values()) > 0:
    #     status_codes = get_status_code(spec)
    #     status_codes = status_codes.replace("VAR CONSTANT","").replace("END_VAR","")
    # else:
    #     status_codes = ""
    var_constant += f"//    Define status code and constant variables except for array/struct type \n// CANNNOT define type of ARRAY or STRUCT here!\nEND_VAR\n"
    
    # Temp
    var_temp = "VAR_TEMP\n//    Define your temporary variables\n//    define index for loop here!\nEND_VAR\n"

    # Static
    if spec['type'] == 'FUNCTION_BLOCK':
        var_static = "VAR\n//    Define array/struct type, such as DAYS_IN_MONTHS, and static variables here. keep history status like database index for next time usage here. one example is \n statLastItemIndex : Int; \nEND_VAR\n"
    else:
        var_static = ""

    # Combine all parts
    scl_code = head +  var_input + var_output + var_inout + var_temp + var_static + var_constant +  functionblock + f"END_{spec['type']}"
    scl_code = scl_code.replace("* *",'*, *')
    # print(task['name'],f"5")
    return scl_code

def prettify_api(data):
    output = f"{data['instruction_name']}()\n"
    output += f"- 函数描述: {data['brief_description']}\n"
    
    for category in data['parameters']:
        output += f"- {category} 参数:\n"
        for param in data['parameters'][category]:
            output += f"-- {param['name']} ({param['type']}): {param['description']}\n"
        output += "\n"
    
    output += f"- 示例代码:```scl\n {data['example_code']}\n```\n"
    output += f"- 重要提示: {data['additional_info']}\n"
    
    return output

def prettify_task(json_data)->str:
    """
    json to beatiful nl
    input: task of SCL competition
    """
    output = ""
    
    def format_dict(data):
        nonlocal output
        output += f"{data['name']} ({data['type']}): {data.get('description', '')}\n"
    
    def format_list(data):
        nonlocal output
        if len(data) == 0:
            output += "None\n"
        for item in data:
            if "name" in item:
                output += f"- {item['name']} ({item['type']}): {item.get('description', '')}\n"
            else:
                output += f"- item ({item['type']}): {item.get('description', '')}\n"

    def format_status_codes(data):
        nonlocal output
        if len(data.items()) == 0:
            output += "None\n"
        for key, value in data.items():
            output += f"- {key}: {value}\n"
    
    def format_user_defined_types(data):
        nonlocal output
        if len(data) == 0:
            output += "None\n"
        for item in data:
            output += f"- {item['name']}:\n"
            for member in item['member']:
                format_dict(member)
            output += "\n"
    try:
        output += f"{json_data['title']}\n"
        output += f"--------------------------------\n"
        output += f"Name: {json_data['name']}\n"
        output += f"Type: {json_data['type']}\n"
        output += f"Description: {json_data.get('description', '')}\n"

        
        output += "Inputs:\n"
        format_list(json_data.get("input", []))
        
        output += "\nOutputs:\n"
        format_list(json_data.get("output", []))
        
        if "in/out" in json_data:
            output += "\nIn/Out:\n"
            format_list(json_data["in/out"])
        
        if "return_value" in json_data:
            output += "\nReturn Value:\n"
            format_list(json_data["return_value"])
        
        if "status_codes" in json_data:
            output += "\nStatus Codes:\n"
            format_status_codes(json_data["status_codes"])
        
        if "user_defined_types" in json_data:
            output += "\nUser Defined Types:\n"
            format_user_defined_types(json_data["user_defined_types"])
        
        return output
    except :
        return str(json_data)

def expert_fix(scl_code):
    """
        针对常见SCL错误模式进行专家知识修复
    """
    scl_code = scl_code\
            .replace(" % "," MOD ")\
            .replace(" DIV "," / ")\
            .replace("END_IF;","END_IF").replace("END_IF","END_IF;")\
            .replace("END_WHILE;","END_WHILE").replace("END_WHILE","END_WHILE;")\
            .replace("END_FOR;","END_FOR").replace("END_FOR","END_FOR;")\
            .replace("END_REPEAT;","END_REPEAT").replace("END_REPEAT","END_REPEAT;")\
            .replace("END_CASE;","END_CASE").replace("END_CASE","END_CASE;")\
            .replace("VAR_CONSTANT","VAR CONSTANT")\
            .replace("ELSEIF","ELSIF")\
            .replace(" of "," OF ")\
            .replace(" to "," TO ")\
            .replace("```scl", "")\
            .replace("```plaintext", "")\
            .replace("```json", "")\
            .replace("```", "")

    scl_code = replace_array_declaration(scl_code)
    return scl_code

def replace_array_declaration(text):
    # # 定义正则表达式模式
    # pattern = r'(\w+)\s*:\s*ARRAY\[(\d+)\.\.(\d+)\]\s*OF\s*(\w+)\s*:=\s*\[(.*?)\];'
    # # 使用正则表达式找到所有匹配项
    # matches = re.finditer(pattern, text)
    # # 遍历所有匹配项并替换
    # for match in matches:
    #     # 获取匹配的各个部分
    #     array_name = match.group(1)
    #     start_index = match.group(2)
    #     end_index = match.group(3)
    #     element_type = match.group(4)
    #     array_values = match.group(5)
    #     # 构建新的字符串
    #     new_string = f"{array_name} : ARRAY[{start_index}..{end_index}] OF {element_type} := {array_values};"
    #     # 替换原字符串中的匹配项
    #     text = text.replace(match.group(0), new_string)

    # 定义正则表达式模式
    pattern = r'(\w+)\s*:\s*ARRAY\[(\d+)\.\.(\d+)\]\s*OF\s*(\w+)\s*:=\s*\{(.*?)\};'
    # 使用正则表达式找到所有匹配项
    matches = re.finditer(pattern, text)
    # 遍历所有匹配项并替换
    for match in matches:
        # 获取匹配的各个部分
        array_name = match.group(1)
        start_index = match.group(2)
        end_index = match.group(3)
        element_type = match.group(4)
        array_values = match.group(5)
        # 构建新的字符串
        new_string = f"{array_name} : ARRAY[{start_index}..{end_index}] OF {element_type} := {array_values};"
        # 替换原字符串中的匹配项
        text = text.replace(match.group(0), new_string)
        
    # 定义正则表达式模式
    pattern = r'(\w+)\s*:\s*ARRAY\[(\d+)\.\.(\d+)\]\s*OF\s*(\w+)\s*:=\s*\((.*?)\);'
    # 使用正则表达式找到所有匹配项
    matches = re.finditer(pattern, text)
    # 遍历所有匹配项并替换
    for match in matches:
        # 获取匹配的各个部分
        array_name = match.group(1)
        start_index = match.group(2)
        end_index = match.group(3)
        element_type = match.group(4)
        array_values = match.group(5)
        # 构建新的字符串
        new_string = f"{array_name} : ARRAY[{start_index}..{end_index}] OF {element_type} := {array_values};"
        # 替换原字符串中的匹配项
        text = text.replace(match.group(0), new_string)
    return text

def remove_code(response: str) -> str:
    pattern = r'```[\s\S]*?```'
    return re.sub(pattern, '', response)
