import json

instructions_keys = set()
with open('指令库/instructions.json','r') as fp:
    instructions = json.load(fp)
    for ins in instructions:
        instructions_keys.add(ins["指令名"])
    print(instructions_keys)

def read_txt_to_dict(file_path):
    instructions = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 移除首尾空白字符，然后将每行作为JSON字符串解析为字典
            instruction = json.loads(line.strip())
            if instruction["指令名"] in instructions_keys:
                instructions.append(instruction)
    
    return instructions

# 读取 .txt 文件并转换为字典
instructions_dict = read_txt_to_dict('InstructionJSONFormat.jsonl')
print(len(instructions_dict))
with open('instruction_details.json','w') as fp:
    fp.write(json.dumps(instructions_dict, ensure_ascii=False, indent=4))
