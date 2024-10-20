import xml.etree.ElementTree as ET
import os
def read_pou_names_from_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    filecount = 0
    # 获取命名空间，假设所有元素都使用同一个命名空间
    # 找到所有的 project -> pous -> pou 结构
    pous = []
    # 查找所有的 pous 元素
    for pou in root.findall('pous/pou'):
        name = pou.get('name')  # 获取 name  FUNC的名称
        content = ET.tostring(pou, encoding='unicode')
        print(content)
        pous.append(content)
        filecount += 1
    # 返回找到的 pou 名称列表
    return pous, filecount          #pous包含了545个FUNC的pou部分，带有标签

#prompt:
#我会给你一段xml文本， 你需要根据文本生成对应的xml代码。你要从xml转换为ST语言。注意，xml文本内容包含定义变量以及代码，变量定义部分你需要从xml中提取出变量，代码部分你只需要完整地提取出源代码，不要进行任何形式上的修改。生成结果要写在一个代码块里

file_path = 'oscat.xml'
pou_names, filecount = read_pou_names_from_xml(file_path)
print(filecount)