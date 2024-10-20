import re

def analyze_st_code(st_code):
    # 统计代码长度
    code_lines = st_code.strip().split('\n')
    code_length = len(code_lines)

    # 统计输入输出变量个数
    input_vars = re.findall(r'VAR_INPUT', st_code)
    output_vars = re.findall(r'VAR_OUTPUT', st_code)
    input_var_count = len(input_vars)
    output_var_count = len(output_vars)

    # 统计循环数量
    loops = re.findall(r'\b(FOR|WHILE|REPEAT)\b', st_code)
    loop_count = len(loops)

    # 统计条件判断数量
    conditions = re.findall(r'\b(IF|CASE)\b', st_code)
    condition_count = len(conditions)

    # 统计库函数调用数量
    # 这里假设库函数名称全为大写或者匹配一些常见函数名
    library_functions = re.findall(r'\b[A-Z_]+\b\(', st_code)
    library_function_count = len(library_functions)

    # 计算控制流复杂度 (Cyclomatic Complexity)
    # 简单情况下，控制流复杂度等于判断条件 + 1
    cyclomatic_complexity = condition_count + 1

    # 统计注释密度
    comments = re.findall(r'\(\*.*?\*\)', st_code, re.DOTALL)  # 多行注释
    comment_lines = sum([comment.count('\n') + 1 for comment in comments])
    comment_density = comment_lines / code_length if code_length > 0 else 0

    # 输出分析结果
    print(f"代码总行数: {code_length}")
    print(f"输入变量个数: {input_var_count}")
    print(f"输出变量个数: {output_var_count}")
    print(f"循环数量: {loop_count}")
    print(f"条件判断数量: {condition_count}")
    print(f"库函数调用数量: {library_function_count}")
    print(f"控制流复杂度 (Cyclomatic Complexity): {cyclomatic_complexity}")
    print(f"代码注释密度: {comment_density:.2f}")