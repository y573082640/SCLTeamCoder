# from promptings.MapCoder import *
from datetime import datetime
import pytz
import json
import os
from scl_team_coder.util.prompt_res_util import PromptResultUtil
from scl_team_coder import glovar

class RetrievalAgent():
    retrieval_agent_prompt_sys_en: str = """Role: You are a searcher. Given a task, you can retrieve the most relevant Siemens SCL programming cases from the knowledge base and analyze them.

Input:
1. Task requirement description. It uses natural language to describe some goals or tasks that user want to achieve through programming with Siemens SCL language.

Goals:
1. Find three (03) relevant Siemens SCL programming cases from the knowledge base.
2. Describe them.
3. Identify how these cases can provide assistance in solving the given task.

Constraints:
1. Your response must follow the specified output format. Note that there are some comments in it suggesting what content you should fill in at that location.
2. The cases in your response must come from the retrieve results.
3. Every unique name must correspond to the retrieved case.
4. Do not add extra explanation or words outside of the specified output format.

Workflow:
1. Input Analysis: Carefully read and understand the task requirement description.
2. Search: Retrieve the most three (03) relevant and distinct Siemens SCL programming cases (different from given task mentioned above) from the knowledge base.
For each case,
3. Describe it.
4. Think: What may we learn from these cases to solve the given task? Describe how these cases can provide assistance in solving the given task.
5. Output Delivery: Present the final result in the specified output format.

Output Format:
<root>
<case>
# Retrieve three (03) relevant and distinct cases (different from given task mentioned above). Write each case in the following format.
<name>
# Unique name of the case. The name is obtained from the knowledge base during retrieval.
</name>
<description>
# Describe the case.
</description>
<assistance>
# How these cases can provide assistance in solving the given task, write the result you analyzed.
</assistance>
</case>
# similarly add more cases here...
<case>...</case>
</root>"""

    retrieval_agent_prompt_sys: str = """Role: 你是一名搜索者。给定一个任务，你可以从知识库中检索到最相关的Siemens SCL编程案例并进行分析。

Input:
1. 给定任务需求描述。这是一段使用自然语言描述的用户希望通过Siemens SCL语言编程实现的一些目标或任务。

Goals:
1. 从知识库中找到三(03)个相关的Siemens SCL编程案例。
2. 描述这些案例。
3. 识别这些案例如何在解决给定任务时提供帮助。

Constraints:
1. 你的回答必须遵循指定的输出格式。注意，其中有一些注释提示你在该位置填写什么内容。
2. 你的回答中的案例必须来自检索结果。
3. 每个唯一名称必须与检索到的案例相对应。
4. 请不要在指定的输出格式之外添加额外的解释或文字。

Workflow:
1. 输入分析：仔细阅读并理解任务需求描述。
2. 搜索：从知识库中检索最相关且不同于上述给定任务的三(03)个Siemens SCL编程案例。
对每个案例，
3. 描述它。
4. 思考：从这些案例中我们可以学到什么来解决给定的任务？描述这些案例如何在解决给定任务时提供帮助。
5. 输出交付：以指定的输出格式呈现最终结果。

Output Format:
<root>
<case>
# 检索到三个(03)相关且不同的案例（不同于上述给定任务）。按以下格式书写每个案例。
<name>
# 案例的唯一名称。名称可以在检索过程中从知识库中获得。
</name>
<description>
# 描述该案例。
</description>
<assistance>
# 这些案例如何在解决给定任务时提供帮助，写下你分析的结果。
</assistance>
</case>
# 同样地添加更多案例...
<case>...</case>
</root>
"""

    @classmethod
    def retrieval_agent_prompt(self, requirements: str) -> str:
        """
        ## 【输入】 任务需求requirements(JSON字符串形式)
        ## 【执行】 访问知识库, 提取与任务需求相似的样例描述，分析样例代码如何满足样例需求，并分析为什么有借鉴价值。
        ##         返回样例id。获取样例id, 找到本地的代码片段。
        ## 【输出】 样例id; 对可借鉴性的分析; 分析样例代码如何满足样例需求
        """
        retrieval_agent_prompt_user_en = f"""Here is a task requirement description: 
{requirements}"""
        retrieval_agent_prompt_user = f"""这里是一段任务需求的自然语言描述：{requirements}"""
        
        # for testing
        from zhipuai import ZhipuAI
        api_key = glovar.API_KEY_AIRX
        client = ZhipuAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="glm-4-airx",  # 填写需要调用的模型名称
            temperature=0.15,
            top_p=0.9,
            messages=[
                {"role": "system", "content": RetrievalAgent.retrieval_agent_prompt_sys},
                {"role": "user", "content": requirements},
            ],
            tools=[
                {
                    "type": "retrieval",
                    "retrieval": {
                        "knowledge_id": "1811717252865732608", # 提交用的
                        # "knowledge_id": "1823282853610450944", # 测试用的
                        "prompt_template": """这里是一段任务需求的自然语言描述：:
\"\"\"
{{question}}
\"\"\"
现在检索到了一些案例如下：
\"\"\"
{{knowledge}}
\"\"\"
请回答。"""
                    }
                }
            ],
            # stream=True,
        )
        # print(response.choices[0].message.content)
        new_base_folder = os.path.join('./output/retrive_test_logs')
        if not os.path.exists(new_base_folder):
            os.makedirs(new_base_folder)
        path = f"{new_base_folder}/retreival_agent_test_{datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y%m%d-%H%M%S')}.txt"
        with open(path, 'w', encoding='utf8') as f:
            f.write(response.choices[0].message.content)
        return response.choices[0].message.content
    
    @classmethod
    def retrieval_agent_bm25(self, requirements: str) -> str:
        pass

    @classmethod
    def get_result(self, response: str) -> list:
        response = PromptResultUtil.extract_xml_content(response)
        response = PromptResultUtil.replace_tag(response, 'name')
        response = PromptResultUtil.replace_tag(response, 'description')
        response = PromptResultUtil.replace_tag(response, 'assistance')
        response = PromptResultUtil.parse_xml(response)
        res = []
        try:
            for example_no, example in enumerate(response["case"], start=1):
                name = example["name"].strip()
                if not os.path.exists(f"{glovar.RAG_DATA_DIR}/scl_case_code_modified/{name}.json"):
                    print(f"Warning: There is no case named '{name}' in local files.")
                    continue
                code_json = json.loads(PromptResultUtil.get_json_content(name))
                code_scl = PromptResultUtil.get_source_code(name)
                res.append({
                    "name": name,
                    "json_desc": code_json,
                    "assistance": example["assistance"].strip(),
                    "code": code_scl
                })
        except Exception as e:
            res = []
        return res


# for testing
# if __name__ == '__main__':
#     test_prompt = "在一些自动化系统中，可能需要将一个整数的各个位分离出来，以便于显示或进一步处理。例如，在一些计数器或生产计数应用中，需要将当前的计数值分离成个位、十位、百位和千位。\n控制要求：\n系统需要接收一个最多四位整数作为输入。\n根据输入的整数，计算并输出其个位、十位、百位和千位数值。\n如果输入的整数少于四位，则在缺失的高位上显示0。\n输出结果应该是四个独立的整数，分别代表个位、十位、百位和千位。\n说明：\n1. 要求输入的整数InputNumber大于等于0且小于10000，否则输出错误状态error=true和错误代码status=16#8001。\n2. 在计算出个、十、百、千这四个数位的数值后，对这四个数位值中非0的值进行比较并输出最小值到Min；如果InputNumber=0，则输出Min=0。"
#     response = RetrievalAgent.retrieval_agent_prompt(test_prompt)
#     # with open('./output/retreival_agent_test_20240716-150955.txt', 'r', encoding='utf8') as f:
#     #     response = f.read()
#     # f.close()
#     res = RetrievalAgent.get_result(response)
#     # for r in res:
#     #     print(r["json_desc"])
#     path = f"./output/retreival_agent_next_{datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y%m%d-%H%M%S')}.txt"
#     with open(path, 'w', encoding='utf8') as f:
#         f.write(json.dumps(res))