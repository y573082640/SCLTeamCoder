from zhipuai import ZhipuAI
import multiprocessing
import json
import numpy as np
with open('./instructions_embeddings_common.json','r') as fp:
    instruction_dict = json.load(fp)
names = list(instruction_dict.keys())
embeddings = np.array(list(instruction_dict.values()))
# Read an jsonl file and convert it into a python list of dictionaries.
def read_jsonl(filename):
    """Reads a jsonl file and yields each line as a dictionary"""
    lines = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            lines.append(json.loads(line))
    return lines

def get_embedding(task):
    client = ZhipuAI(api_key='42253decc3d85bad61464e9f5813cfc4.GicxpDMXwGZVEzA7')
    name = task.split(":")[0]
    response = client.embeddings.create(
        model="embedding-2",  # 填写需要调用的模型名称
        input=task
    )
    return response.data[0].embedding
    # return {'name':name,'embedding':response.data[0].embedding}

task = """
解决这个问题的算法步骤如下：
0. 右移
1. 接收输入参数InputWord，该参数是一个16位的二进制数。
2. 使用位操作将InputWord分解为四个4位的二进制数：
   - 对于Byte0，将InputWord与0x0F（即0000 1111）进行位与操作，得到最低的4位。
   - 对于Byte1，将InputWord右移4位后与0x0F进行位与操作，得到次低的4位。
   - 对于Byte2，将InputWord右移8位后与0x0F进行位与操作，得到次高的4位。
   - 对于Byte3，将InputWord右移12位后与0x0F进行位与操作，得到最高的4位。
3. 将得到的四个4位二进制数分别赋值给Byte0、Byte1、Byte2和Byte3。
4. 初始化一个计数器count和累加器sum，用于计算非0字节的平均值。
   - 遍历Byte0到Byte3，对于每个非0的字节，将count加1，并将该字节的值加到sum中。
5. 计算平均值average，如果count为0（即所有字节都是0），则average为0；否则，average等于sum除以count。
6. 输出Byte0、Byte1、Byte2、Byte3和average。
"""
# 任务列表
# sentences = task.split("\n")
# sentences = [ss for ss in sentences if len(ss)>0]
# sentences = []
# with open('/root/MapCoder/src/promptings/agents/instructions/brief_instruction_description common.jsonl','r') as fp:
#     instructions = json.load(fp)
#     for k,v in instructions.items():
#         sentences.append(f"{k}:{v['description']}")
# 创建进程池
# instructions = read_jsonl('/root/MapCoder/src/promptings/agents/instructions/brief_instruction_description common.jsonl')
# for v in instructions:
#     sentences.append(f"{v['instruction_name']}:{v['description']}")
# with multiprocessing.Pool(5) as pool:
#     # 异步调用get_embedding函数并收集结果
#     results = pool.map(get_embedding, sentences)
# results = {item['name']: item['embedding'] for item in results}
# # 输出结果
# with open('instructions_embeddings_common.json','w+') as fp:
#     json.dump(results,fp,ensure_ascii=False)
# def cosine_similarity_batch(vec, matrix):
#     """
#     计算一个向量与多个向量之间的余弦相似度
#     vec: 需求的向量表示
#     matrix: 指令描述向量的矩阵
#     """
#     dot_products = np.dot(matrix, vec)
#     norm_vec = np.linalg.norm(vec)
#     norm_matrix = np.linalg.norm(matrix, axis=1)
#     return dot_products / (norm_vec * norm_matrix)

# def recommend_similar_instructions(demand_vec,top_k=5):
#     """
#     推荐与需求向量最相似的指令
#     instruction_dict: 包含指令名和指令描述向量的字典
#     demand_vec: 需求的向量表示
#     top_k: 推荐的指令数量，默认为5
#     """
#     similarities = cosine_similarity_batch(demand_vec, embeddings)
#     # 获取相似度最高的top_k个指令及其相似度
#     top_indices = np.argsort(similarities)[::-1][:top_k]
#     top_similarities = similarities[top_indices]
#     top_names = [names[i] for i in top_indices]
#     return list(zip(top_names, top_similarities))

# with multiprocessing.Pool(5) as pool:
#     # 异步调用get_embedding函数并收集结果
#     sentence_embeddings = pool.map(get_embedding, sentences)

# for embedding in sentence_embeddings:
#     print(recommend_similar_instructions(embedding))
