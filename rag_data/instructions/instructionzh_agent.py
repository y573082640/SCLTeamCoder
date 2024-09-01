import json
import re
import os
import time
import threading
from multiprocessing import Process
import random
from zhipuai import ZhipuAI
class instructionZHAegnt():

    instruction_zh_agent = """
Role: 你是一个Siemens SCL编程领域的指令总结专家，可以帮我总结指令的功能和应用场景。

Goals:
1. 总结给定的指令，形成一段简要的关于指令功能和应用场景的中文自然语言描述。

Constraints:
1. 你的回答必须遵循指定的输出格式。
2. 指令名字、保持与提供的指令相一致。

Workflow:
1. 输入分析：仔细阅读并理解所提供的指令。
2. 结合指令的信息（该指令的总体描述、涉及到的变量），使用中文总结该指令。
3. 输出交付：以指定的输出格式呈现最终结果。

Input:
1. 给定指令的信息描述。这是一段以json形式的使用中文自然语言描述的指令叙述。

IMPORTANT:
1. 按照指定的格式进行输出。具体格式为：该指令的name为xxx,功能为xxx,可以应用于xxx。

Output Format:
```plaintext
    你的简要总结
```
"""
    @classmethod
    def getPerfectWriteFormat(self, text):
        start_phrase = r"功能为"
        end_phrase = r"\n```"
        # 找到所需短语的起始索引
        start_index = text.find(start_phrase)
        # 如果找到了短语，从该索引开始截取字符串直到末尾
        if start_index != -1:
            result = text[start_index:]
        else:
            result = "未找到前短语。"
            return
        end_index = result.find(end_phrase)
        if end_index != -1:
            result = result[:-6]
        return result
    output_file_path = './scl_case_json_zh_simple/'
    fewshot_file_path = '../bm25/'
    @classmethod
    def instruction_zh_agent_prompt(self, requirements) -> str:
        instruction_name = requirements['instruction_name']
        name = requirements['instruction_name']
        json_zh_agent_prompt_user = f"""
            下面是给定指令的信息描述：
            {requirements}
        """
        msgs = [{"role": "system", "content": instructionZHAegnt.instruction_zh_agent.strip()}]
        msgs.append({"role": "user", "content": json_zh_agent_prompt_user.strip()})
        from zhipuai import ZhipuAI
        api_keys = '17de3703e7f860b222c8e90572645905.3DrTPrr6QJuJwMja'
        client = ZhipuAI(api_key=api_keys)
        response = client.chat.completions.create(
            model="glm-4-0520",  # 填写需要调用的模型名称
            messages=msgs,
            temperature=0.75,
            max_tokens=96*1000,
        )
        path = instructionZHAegnt.output_file_path + name + '.json'
        try:
            res = response.choices[0].message.content
            with open("./brief_instruction_description.jsonl", 'a', encoding='utf8') as f:
                json_str = json.dumps(res, ensure_ascii=False)
                value = instructionZHAegnt.getPerfectWriteFormat(json_str)
                finallyJson = {"instruction_name": instruction_name, "description": value}
                # 直接将字典转换为 JSON 字符串并写入文件
                f.write(json.dumps(finallyJson, ensure_ascii=False) + '\n')
        except Exception as e:
            print("--warning!",requirements['name'],e)


    @classmethod
    def generateBrief(self):
        with open("./brief_instruction_description.jsonl", "w", encoding='utf-8') as file:  # 清空文件内容
            file.write('')
        directory = "./dict_new_instruction_165.json"
        with open(directory, 'r', encoding='utf-8') as file:
            instructions = json.load(file)
    # 遍历字典中的每个指令对象
        for instruction_key, instruction_value in instructions.items():
            print(f"提取的指令对象：{instruction_key}")
            instructionZHAegnt.instruction_zh_agent_prompt(instruction_value)

if __name__ == '__main__':
    instructionZHAegnt.generateBrief()
