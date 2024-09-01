from rank_bm25 import BM25Okapi
# encoding=utf-8
import jieba
import time
import json
import os
import codecs
import numpy as np
from scl_team_coder import glovar

jieba.initialize()
# def prettify_task(json_data)->str:
#     """
#     json to beatiful nl
#     input: task of SCL competition
#     """
#     output = ""
    
#     def format_dict(data):
#         nonlocal output
#         output += f"{data['name']} ({data['type']}): {data.get('description', '')}\n"
    
#     def format_list(data):
#         nonlocal output
#         if len(data) == 0:
#             output += "None\n"
#         for item in data:
#             if "name" in item:
#                 output += f"- {item['name']} ({item['type']}): {item.get('description', '')}\n"
#             else:
#                 output += f"- item ({item['type']}): {item.get('description', '')}\n"
    
#     def format_status_codes(data):
#         nonlocal output
#         if len(data.items()) == 0:
#             output += "None\n"
#         for key, value in data.items():
#             output += f"- {key}: {value}\n"
    
#     def format_user_defined_types(data):
#         nonlocal output
#         if len(data) == 0:
#             output += "None\n"
#         for item in data:
#             output += f"- {item['name']}:\n"
#             for member in item['member']:
#                 format_dict(member)
#             output += "\n"
#     try:
#         output += f"{json_data['title']}\n"
#         output += f"--------------------------------\n"
#         output += f"Name: {json_data['name']}\n"
#         output += f"Type: {json_data['type']}\n"
#         output += f"Description: {json_data.get('description', '')}\n"

        
#         output += "Inputs:\n"
#         format_list(json_data.get("input", []))
        
#         output += "\nOutputs:\n"
#         format_list(json_data.get("output", []))
        
#         if "in/out" in json_data:
#             output += "\nIn/Out:\n"
#             format_list(json_data["in/out"])
        
#         if "return_value" in json_data:
#             output += "\nReturn Value:\n"
#             format_list(json_data["return_value"])
        
#         if "status_codes" in json_data:
#             output += "\nStatus Codes:\n"
#             format_status_codes(json_data["status_codes"])
        
#         if "user_defined_types" in json_data:
#             output += "\nUser Defined Types:\n"
#             format_user_defined_types(json_data["user_defined_types"])
        
#         return output
#     except :
#         return str(json_data)

def read_jsonl(filename):
    """Reads a jsonl file and yields each line as a dictionary"""
    lines = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            lines.append(json.loads(line))
    return lines

class BM25RetriverInstruction:
    def __init__(self,scl_instruction_path=f'{glovar.RAG_DATA_DIR}/instructions/brief_instruction_description common.jsonl'):
        start_time = time.time()
        self.instruction_corpus,self.instruction_names = self.read_ins_desc(scl_instruction_path)
        self.tokenized_corpus = [list(jieba.cut(doc)) for doc in self.instruction_corpus]
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        end_time = time.time()
        total_time = end_time - start_time
        # print(f"BM25Retriver Init in {total_time:.2f} seconds.")

    def query_algo_apis(self,algo:str):
        all_apis = set()
        algo_lines = algo.strip().split("\n")
        for line in algo_lines:
            if line:
                tokenized_query = list(jieba.cut(line))
                # 获取每个文档的得分
                scores = self.bm25.get_scores(tokenized_query)
                # 排序并获取排名
                ranked_indices = np.argsort(scores)[::-1]
                ranked_scores = sorted(scores, reverse=True)
                # 找到得分高于阈值的前三名文档
                top_docs = [(rank, score) for rank, score in zip(ranked_indices, ranked_scores) if score > 20][:2]
                for idx, (doc_idx, score) in enumerate(top_docs, start=1):
                    all_apis.add(self.instruction_names[doc_idx])
                # for api in results:
                #     all_apis.add(api.split(":")[0])
        all_apis = list(all_apis)
        # [self.instruction_names[name] for name in all_apis]
        return all_apis

    def query_doc(self,query,top_n=3):
        tokenized_query = list(jieba.cut(query))
        return self.bm25.get_top_n(tokenized_query, self.instruction_corpus, n=top_n)
    
    def read_ins_desc(self, scl_instruction_path):
        scl_instructions = read_jsonl(scl_instruction_path)
        ret = []
        names = []
        for api in scl_instructions:
            ret.append(
                f"""{api['instruction_name']}:{api['description']}"""
            )
            names.append(api['instruction_name'])
        return ret,names

class BM25RetriverSCL:
    def __init__(self,scl_cases_path=f'{glovar.RAG_DATA_DIR}/scl_case_json_zh_simple'):
        start_time = time.time()
        self.case_desc_corpus = self.read_case_desc(scl_cases_path)
        self.tokenized_corpus = [list(jieba.cut(doc)) for doc in self.case_desc_corpus]
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        end_time = time.time()
        total_time = end_time - start_time
        # print(f"BM25Retriver Init in {total_time:.2f} seconds.")

    def query_doc(self,query,top_n=3,base=f'{glovar.RAG_DATA_DIR}/scl_case_code_modified'):
        try:
            tokenized_query = list(jieba.cut(query))
            top_n_case = self.bm25.get_top_n(tokenized_query, self.case_desc_corpus, n=top_n)
            ret = []
            for case in top_n_case:
                name_decs = case.split(":")
                name = name_decs[0]
                with open(f"{base}/{name}.json", 'r', encoding='utf8') as f:
                    code_json = f.read()
                with open(f"{base}/{name}.scl", 'r', encoding='utf8') as f:
                    code_scl = f.read()
                ret.append({
                    "name": name,
                    "json_desc": code_json,
                    "assistance": "",
                    "code": code_scl
                })
        except Exception as e:
            print(e)
        return ret
    
    def read_case_plans(self, scl_plans_path):
        plans = []
        for filename in os.listdir(scl_plans_path):
            if filename.endswith('.plan'):
                file_path = os.path.join(scl_plans_path, filename)
                with open(file_path, 'r') as file:
                    try:
                        data = json.load(file)
                        description = data.get('planning', None)
                        if description:
                            plans.append(description)
                        else:
                            print(f"No 'planning' field in {filename}")
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON from {filename}")
        return plans
    
    def read_case_desc(self, scl_cases_path):
        descs = []
        for filename in os.listdir(scl_cases_path):
            if filename.endswith('.json'):
                file_path = os.path.join(scl_cases_path, filename)
                with open(file_path, 'r') as file:
                    try:
                        data = json.load(file)
                        description = data.get('description_zh', None)
                        if description is None:
                            description = data.get('description', None)
                        if description:
                            descs.append(f"""{data['name']}:{description}""")
                        else:
                            print(f"No 'description' field in {filename}")
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON from {filename}")
        return descs

if __name__  == "__main__":
    # scl_cases_path = '../scl_case_json_zh_simple/'
    # scl_plans_path = '../scl_case_plan_0520_zh/'
    # retriver = BM25RetriverSCL(scl_cases_path)
    # directory_path = '../初赛题目/'
    # for filename in os.listdir(directory_path):
    #     if filename.endswith('.json'):
    #         file_path = os.path.join(directory_path, filename)
    #     with open(file_path, 'r') as file:
    #         try:
    #             data = json.load(codecs.open(file_path, 'r', 'utf-8-sig'))
    #             prettified_data = prettify_task(data)
    #             print(data['name'],":",retriver.query_doc(data['description'],top_n=1))
    #         except json.JSONDecodeError as e:
    #             print(f"Error decoding JSON from {file_path}: {e}")

    scl_instruction_path = f'{glovar.RAG_DATA_DIR}/instructions/brief_instruction_description common.jsonl'
    retriver = BM25RetriverInstruction(scl_instruction_path)
    query = "首先获取数组长度,随后找到位置在1/2的元素"
    ret = retriver.query_algo_apis("""
        1. 输入和输出变量声明:
            - 输入变量：`enqueue`（入队）、`dequeue`（出队）、`reset`（重置）、`clear`（清除）以及初始项 `initialItem`。
            - 输出变量：错误标志 `error`、状态 `status`、元素计数 `elementCount` 以及是否为空 `isEmpty`。
            - 输入输出变量：当前项 `item` 和缓冲区 `buffer`。
        2. 临时变量声明:
            - 用于存储状态边缘、内部错误、索引、缓冲区大小和计数器的临时变量。
        3. 常量声明:
            - 定义了一些常量用于标记缓冲区状态、错误代码和缓冲区操作。
        4. 初始化:
            - 初始化必要的变量。
        5. 块执行控制:
            - 收集边缘信号（即入队、出队和清除操作的变化）。
            - 如果没有触发输入信号（即没有入队、出队、重置或清除操作），则设置状态为“无当前任务”，并退出程序。
        6. 输入验证:
            - 检查缓冲区是否为数组，并读取数组元素数量。如果不是数组，则返回错误。
            - 检查数组元素的数据类型是否与项的类型匹配。如果不匹配，则返回错误。
            - 检查初始值的数据类型是否与项的类型匹配。如果不匹配，则返回错误。
            - 检查索引是否在数组范围内。如果超出范围，则返回错误。
            - 如果 `reset` 为真，重置缓冲区计数器，并返回。
            - 如果 `clear` 信号有上升沿，则初始化缓冲区为初始值，并重置计数器和索引。
        7. FIFO算法:
            - 如果 `dequeue` 信号有上升沿，执行出队操作：
                - 检查缓冲区是否为空。如果为空，则返回错误。
                - 返回缓冲区的第一个项，并用初始值替换该项。
                - 更新第一个项的索引。如果缓冲区为空，重置索引。否则，递增第一个项的索引。
                - 减少元素计数。
            - 如果 `enqueue` 信号有上升沿，执行入队操作：
                - 检查缓冲区是否已满。如果已满，则返回错误。
                - 将项写入缓冲区，并更新下一个空项的索引。
                - 如果缓冲区尚未初始化，初始化第一个项的索引。
                - 增加元素计数。
        8. 结果输出:
            - 将元素计数和是否为空的状态输出。
            - 设置错误标志为假，并设置状态为无错误。
        整个过程实现了一个基本的FIFO缓冲区管理，包括入队、出队、重置和清除操作，并进行了必要的错误检查和状态更新。        
    """)
    print(ret)