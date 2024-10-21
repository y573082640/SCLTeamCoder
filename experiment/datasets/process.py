import os
import json
from openai import OpenAI
from scl_team_coder import glovar
from scl_team_coder.util.prompt_res_util import *
from scl_team_coder.util.agent_tools import *
from tqdm import tqdm  # 导入tqdm库
import glob
project_base = glovar.PROJECT_ROOT
# 设置 API 密钥
api_key = glovar.GPT_API_KEY
# 创建GPT AI 客户端
client = OpenAI(api_key=api_key, base_url=f"https://m.gptapi.us/v1")
# 指定要使用的模型
model = "gpt-4o"

def call_llm(user_input,sys_prompt="将中文翻译为英文自然语言。直接输出翻译后的英文。"):
    # 调用智谱AI
    response = client.chat.completions.create(
        model = model,  # 填写需要调用的模型名称
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_input}
        ],
        max_tokens=4096,
    )
    return response.choices[0].message.content

def write_jsonl(data, output_path):
    with open(output_path, 'a+', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')

def read_and_translate(directory):
    
    # 获取目录中所有的文件，并过滤出.json结尾的文件
    all_files = [f for f in os.listdir(directory) if f.endswith(".json")]
    
    # 使用tqdm显示进度条
    for filename in tqdm(all_files, desc="Processing files"):
        file_path = os.path.join(directory, filename)
        try:
            with open(file_path, 'r', encoding="utf-8-sig") as file:
                data = json.load(file)
                if 'description_zh' in data:
                    # 假设translate_sentence是一个翻译函数
                    en_sentence = call_llm(data["description_zh"])
                    data['description'] = en_sentence
                    del data['description_zh']
                write_jsonl(data, f"{directory}.jsonl")
        except Exception as e:
            print(filename,e)

def translate_xml_to_st(file_path):
    import xml.etree.ElementTree as ET
    import re
    # prompt_en = "I'll give you a piece of xml text, and you'll need to generate the corresponding xml code from the text. You have to convert from xml to ST language. Note that the xml text contains the definition of variables as well as the code, for the variable definition part you need to extract the variables from the xml and for the code part you need to extract the source code in its entirety without any formal modifications. The generated result should be written in a code block"
    prompt_en = "given st variable declare in xml format, translate it into st code of iec 61131-3 standard and can be use in codesys. IMPORTANT: Output variable declare code according to given xml in this format ```st # your code here ```."
    tree = ET.parse(file_path)
    root = tree.getroot()
    filecount = 0
    # 获取命名空间，假设所有元素都使用同一个命名空间
    # 找到所有的 project -> pous -> pou 结构
    pous = []
    # 查找所有的 pous 元素
    for pou in root.findall('pous/pou'):
        # 1.使用大模型转换变量定义部分
        interface = pou.find('interface')
        # a.返回部分的代码
        return_type = interface.find('returnType')
        if return_type is not None:
            return_type_element = return_type.find("*")
            return_type_code = str(return_type_element.tag)
            if return_type_code == "derived":
                return_type_code = return_type_element.get('name')
        # b.变量定义的代码
        define_part_xml = ET.tostring(interface, encoding='unicode')
        # 正则表达式匹配<returnType>任意内容</returnType>
        pattern = r'<returnType>.*?</returnType>'
        # 使用空字符串替换匹配到的内容
        define_part_xml = re.sub(pattern, '', define_part_xml, flags=re.DOTALL)
        # 使用大模型翻译变量定义部分
        define_part_code = parse_response(call_llm(define_part_xml,prompt_en)).strip()
        # 2.手动提取变量定义和st代码主体
        # c.主体代码
        st_body = pou.find('.//ST')
        st_body_code = st_body.text.strip() # 使用 .strip() 去除前后空格和换行符
        
        # d.块的头部代码
        block_name_code = pou.get('name')  
        block_type_code = pou.get('pouType') 
        block_type_code = "FUNCTION_BLOCK" if block_type_code == "functionBlock" else "FUNCTION"
        
        # 3.拼接上述所有abcd代码保存为{pou_name}.st文件
        if return_type is not None:
            # 此时为function块，有返回值
            st_code = f"{block_type_code} {block_name_code} : {return_type_code}\n{define_part_code}\n{st_body_code}\nEND_{block_type_code}\n"
        else:
            # 此时为fb块，无返回值
            st_code = f"{block_type_code} {block_name_code}\n{define_part_code}\n{st_body_code}\nEND_{block_type_code}\n"
            
        with open(f"{project_base}/experiment/datasets/oscat/oscat_code/{block_name_code}.st","w") as fp:
            fp.write(st_code)
            
        filecount += 1
        print(f"{filecount}:{block_name_code} done. haha!")
        
    # #pous包含了545个FUNC的pou部分，带有标签
    return filecount 

def read_files_to_dict(files_path,prefix="st"):
    files_dict = {}
    for file in glob.glob(os.path.join(files_path, f'*.{prefix}')):
        with open(file, 'r') as f:
            content = f.read()
            key = os.path.splitext(os.path.basename(file))[0]
            files_dict[key] = content
    return files_dict
    
def get_oscat_requirements(code_path,txt_path,requirement_path):
    with open(f"{project_base}/experiment/datasets/oscat/oscat_prompt","r") as fp:
        prompt_en = fp.read()
    # 1.读取code_path下的所有st文件并转换为字典，key为名
    st_dict = read_files_to_dict(code_path,prefix="st")
    # 2.读取txt_path下的所有txt文件
    txt_dict = read_files_to_dict(txt_path,prefix="txt")
    # 3.调用大模型根据code和txt生成需求
    for key,value in st_dict.items():
        user_manual = txt_dict.get(key,"# No user manual for this st code")
        requirement = call_llm(f"user manual:\n{user_manual}\nst_code:\n{value}\n",prompt_en)
        requirement = parse_response(requirement)
        # 4.将生成的需求保存到requirement_path下的txt文件中
        with open(f"{requirement_path}/{key}.json","w") as fp:
            fp.write(requirement)
        print(f"{key} done.")
        return  

def run_process():
    code_path = f"{project_base}/experiment/datasets/oscat/oscat_code"
    txt_path = f"{project_base}/experiment/datasets/oscat/oscat_raws"
    requirement_path = f"{project_base}/experiment/datasets/oscat/oscat_en_v2"
    get_oscat_requirements(code_path,txt_path,requirement_path)
    # read_and_translate(f"{project_base}/experiment/datasets/lgf/lgf_en")