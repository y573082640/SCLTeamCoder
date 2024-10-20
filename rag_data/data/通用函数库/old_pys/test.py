import re

def extract_functions(text):
    # 定义一个正则表达式来匹配函数调用
    pattern = r'\b([A-Z_]+)\s*\((.*?)\)'
    
    # 初始化一个列表来存储所有提取到的函数名
    functions = []

    # 定义一个递归函数来处理嵌套结构
    def recursive_extract(text):
        matches = re.finditer(pattern, text)
        for match in matches:
            # 提取函数名并添加到列表中
            functions.append(match.group(1))
            # 递归处理括号内的内容
            recursive_extract(match.group(2))

    # 开始递归提取
    recursive_extract(text)
    
    return functions

# 示例字符串
text = "SHR(IN := #variableBinary, N := AND(X := #value2, Y := SHR(A := #innerVar)))"

# 提取所有函数名
functions = extract_functions(text)

print(functions)