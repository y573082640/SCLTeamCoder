# import json


# def trans(parts):       #至多len = 4
#     return{
#             'name': parts[0],
#             'type': parts[2],
#             'description': parts[3]
#         }
# # 打开JSONL文件
# with open('all_InstructionJSONFormat_165.jsonl', 'r') as file:
#     # 逐行读取
#     jsons = []
#     for line in file:
#         # 解析每一行为JSON对象
#         instruction = json.loads(line)
#         # 提取信息
#         instruction_name = instruction.get("指令名", "")
#         instruction_description = instruction.get("指令说明", "")
#         parameters = instruction.get("参数列表", [])
#         example_code = instruction.get("示例代码和代码解读", "")
#         additional_info = instruction.get("其他有用信息", "")

#         # 打印提取的信息
#         # print(f"指令名: {instruction_name}")
#         # print(f"指令说明: {instruction_description}")
#         # print("参数列表:")
#         Input = []
#         Output = []
#         InOut = []
#         Static = []
#         Return = []
#         Other = []
#         for param in parameters:            #Input Output InOut Static Return None
#             param = param.replace(',', '，')
#             parts = param.split('，', 3)
#             # print(parts)
#             if len(parts) <= 1:     #不完整
#                 continue
#             stripPartOne = parts[1].strip()             #去掉两边括号进行匹配
#             if stripPartOne in ['Input', 'Output', 'InOut', 'Static', 'Return']:
#                 if stripPartOne == 'Input':
#                     Input.append(trans(parts))
#                 elif stripPartOne == 'Output':
#                     Output.append(trans(parts))
#                 elif stripPartOne == 'InOut':
#                     InOut.append(trans(parts))
#                 elif stripPartOne == 'Static':
#                     Static.append(trans(parts))
#                 elif stripPartOne == 'Return':
#                     Return.append(trans(parts))
#                 else:
#                     Other.append(trans(parts))
#         param_dict = {}
#         if Input:
#             param_dict['Input'] = Input
#         if Output:
#             param_dict['Output'] = Output
#         if InOut:
#             param_dict['InOut'] = InOut
#         if Static:
#             param_dict['Static'] = Static
#         if Return:
#             param_dict['Return'] = Return
#         if Other:
#             param_dict['Other'] = Other
#         # json_string = json.dumps({
#         #     'instruction_name': instruction_name,
#         #     'instruction_description': instruction_description,
#         #     'parameters': param_dict,
#         #     'example_code': example_code,
#         #     'additional_info': additional_info,
#         #     # **param_dict
#         # }, ensure_ascii=False, indent=4)
#         json_string = {
#             'instruction_name': instruction_name,
#             'instruction_description': instruction_description,
#             'parameters': param_dict,
#             'example_code': example_code,
#             'additional_info': additional_info,
#             # **param_dict
#         }   
#         print(json_string)
#         jsons.append(json_string)
#         # print(Input)
#         # print(f"示例代码和代码解读: {example_code}")
#         # print(f"其他有用信息: {additional_info}")
#         # print("-"*40 )  # 分隔线
#     # print(json_string)
#     # with open('new_instruction_165.jsonl', 'w', encoding='utf-8') as file:
#     # # 遍历列表，将每个元素写入文件
#     #     for item in jsons:
#     #         # print(item)
#     #         file.write(item + '\n')
#     ret = {}
#     for item in jsons:
#         ret[item['instruction_name']] = item
#     with open('dict_new_instruction_165.json', 'w', encoding='utf-8') as file:
#     # 遍历列表，将每个元素写入文件
#         json.dump(ret,file,ensure_ascii=False)


Read an jsonl file and convert it into a python list of dictionaries.
def read_jsonl(filename):
    """Reads a jsonl file and yields each line as a dictionary"""
    lines = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            lines.append(json.loads(line))
    return lines

import json
with open('dict_new_instruction_165.json','r') as fp:
    dict_new_instruction_165 = json.load(fp)
lines = read_jsonl('brief_instruction_description.jsonl')

for l in lines:
    if l['instruction_name'] in dict_new_instruction_165:
        dict_new_instruction_165[l['instruction_name']]['brief_description'] = l['description']
with open('dict_new_instruction_common_brief_description.json','w') as fp:
    json.dump(dict_new_instruction_165,fp,ensure_ascii=False)
print(dict_new_instruction_165)