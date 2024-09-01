import os
from antlr4 import *
from antlr4.error.DiagnosticErrorListener import DiagnosticErrorListener
from antlr4.error.ErrorListener import ErrorListener
import json
import re
from scl_team_coder import glovar
from scl_team_coder.util.antlr.antlr_genetated.sclLexer import sclLexer
from scl_team_coder.util.antlr.antlr_genetated.sclParser import sclParser
from scl_team_coder.util.antlr.antlr_genetated.myListener import MyListener

with open(f"{glovar.RAG_DATA_DIR}/instructions/dict_new_instruction_165.json",'r') as fp:
    all_funcs = json.load(fp)
with open(f"{glovar.UTILS_DIR}/antlr/antlr_genetated/g4_grammar.json",'r') as fp:
    g4_grammar = json.load(fp)

expert_suggestion = {
    'quato_expression':"SCL编程不允许使用`?`进行三元表达式运算，请替换为简单的IF-ELSIF-ELSE的分支结构。",
    'DOWNTO':"SCL编程不允许使用`DOWNTO`关键字",
    'double_div':"SCL编程不允许使用`//`进行整除,请替换为`MOD`和`/`的组合",
}


def parse_g4_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        grammar = file.read()
    
    g4_dict = {}
    current_rule = None
    # 正则表达式来匹配规则和内容
    rule_pattern = re.compile(r"(\w+)\s*:\s*(.*?);", re.DOTALL)
    alternative_pattern = re.compile(r"\s*\|\s*")

    # 解析语法字符串
    grammar_dict = {}
    for match in rule_pattern.finditer(grammar):
        rule_name = match.group(1).strip()
        rule_body = match.group(2).strip()
        
        # 分割各个选项
        alternatives = alternative_pattern.split(rule_body)
        grammar_dict[rule_name] = [alt.strip() for alt in alternatives]

    return grammar_dict

def remove_double_slash_comments(code):
    # 匹配以 // 开头的注释
    code = re.sub(r'//.*\n', '\n', code)
    return code


class GrammarErrorListener(ErrorListener):
    def __init__(self, text_lines):
        super().__init__()  # 对于Python 3
        # 或者
        # super(GrammarErrorListener, self).__init__()  # 对于Python 2
        self.text_lines = text_lines
        self.error_log = ''
        self.SUCCESS = True
        self.errors = {}
        self.count = 1
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        if line not in self.errors :
            self.SUCCESS = False
            text_lines = self.text_lines
            # context = ''.join(text_lines[line-6:line]) + f"# stop_line\n{text_lines[line]}# stop_line\n"+ ''.join(text_lines[line+1:line+6])
            # with open('syntax_check_result.txt','a+') as fp:
            #     syntax_error_record = f"<syntax_check>\n<syntax_error>\n{msg}\n</syntax_error>\n<context>\n{context}\n</context>\n</syntax_check>\n"
            #     syntax_error_record = syntax_error_record.replace('\r\n\r\n', '\r\n').replace('\n\n', '\n')
            #     self.error_log += syntax_error_record
            #     self.error_log += '\n'

            context = '\n'.join(text_lines[line-5:line+5])
            # context = '\n'.join(text_lines[line-6:line-1]) + f"\n// stop_line\n{text_lines[line-1]}\n// stop_line\n"+ '\n'.join(text_lines[line:line+6])

            # print(context)

            # 获取期望的token类型
            expected_tokens = recognizer.getExpectedTokens().toString(recognizer.literalNames, recognizer.symbolicNames)
            
            # 获取实际的token类型
            actual_token = offendingSymbol.text

            # 获取前一个token
            token_stream = recognizer.getTokenStream()
            if token_stream is not None and offendingSymbol.tokenIndex > 0:
                previous_token = token_stream.get(offendingSymbol.tokenIndex - 1)
                previous_token_text = previous_token.text
            else:
                previous_token_text = ""
            
            # get current rules
            rule_stack = recognizer.getRuleInvocationStack()
            final_rule_grammars = g4_grammar.get(rule_stack[0],"找不到相关语法")
            relevant_rule = [rule_stack[0]]
            # for or_rules in final_rule_grammars:
            #     for rule in or_rules.split(' '):
            #         rule = rule.replace(')',"").replace('?',"").replace('+',"").replace('*',"")
            #         if rule in g4_grammar:
            #             relevant_rule.append(rule)
            # relevant_rule = list(set(relevant_rule))
            reference_rules = ""
            count_grammar = 1
            for r in relevant_rule:
                relevant_rule_grammars = g4_grammar.get(r,"找不到相关语法")
                reference_rules += f"""\n[{count_grammar}] {r}:{" | ".join(relevant_rule_grammars)};"""
                count_grammar+=1
            # f"- Previous token: '{previous_token_text}'\n"
            # f"- Expected To be: {expected_tokens}\n"
            # f"- Actual token: '{actual_token}'\n"
            msg = f"语法检查器在`{actual_token}`处意外终止了。"
            error_message = (
                f"\n---语法错误 No.{self.count}---\n"
                f"-反馈信息: {msg}\n"
                f"-代码上下文: \n```scl\n{context}\n```\n"
                f"-代码可能违背的SCL语法规则(.g4格式): {reference_rules}" 
            )
            if '?' in context:
                error_message += f"""\n[{count_grammar}] {expert_suggestion['quato_expression']}"""
            elif 'DOWNTO' in context:
                error_message += f"""\n[{count_grammar}] {expert_suggestion['DOWNTO']}"""
            self.error_log += error_message
            self.errors[line] = error_message
            self.count += 1

        # f"- Previous token: '{previous_token_text}'\n"
        # f"- Message: {msg}\n"
        # f"- Syntax error at line {line}, column {column}.\n"
        
        # print(error_message)

def extract_functions_from_block(block_content):
    # 定义一个正则表达式来匹配函数调用，确保函数名后面紧跟着括号
    pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\('    
    # 初始化一个列表来存储所有提取到的函Z数名
    functions = []
    
    # 定义一个递归函数来处理嵌套结构
    def recursive_extract(text):
        matches = re.finditer(pattern, text)
        for match in matches:
            # 提取函数名并添加到列表中
            functions.append(match.group(1))
            # 找到匹配的括号内部内容进行递归处理
            start = match.end()  # 括号内部的起始位置
            depth = 1
            for i in range(start, len(text)):
                if text[i] == '(':
                    depth += 1
                elif text[i] == ')':
                    depth -= 1
                    if depth == 0:
                        inner_text = text[start:i]
                        recursive_extract(inner_text)
                        break
    # 开始递归提取
    recursive_extract(block_content)
    # 去重和LGF（特判一个奇怪的东西）
    ret = set(functions)
    ret.discard('LGF') 
    return list(ret)

def syntax_check(scl_code):
    ## 防止//当做整除带来的干扰
    # scl_code = remove_double_slash_comments(scl_code)
    ## 
    error_log = ""
    SUCCESS = True
    ## 检查语法
    input_stream = InputStream(scl_code)
    lexer = sclLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = sclParser(stream)
    parser.removeErrorListeners()
    error_logger = GrammarErrorListener(scl_code.split("\n"))
    parser.addErrorListener(error_logger)
    tree = parser.r()  # 这里的 myStartRule 是你语法中的起始规则
    listener_pack = {}
    listener = MyListener(listener_pack)
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    # listener_pack -> {'error': False, 'error_msg': '', 'special_type_variable': {'ManModeTimer1': 'TON_TIME', 'ManModeTimer2': 'TON_TIME', 'AutoModeTimer': 'TON_TIME'}}
    ## 检查函数使用部分
    function_list = extract_functions_from_block(remove_double_slash_comments(scl_code))
    # print(function_list)
    for func in function_list:
        if func in listener_pack['special_type_variable']:
            continue
        if "_TO_" in func :
            data_from,data_to = func.split("_TO_")
            if data_from != data_to:
                continue
        if not func in all_funcs:
            SUCCESS = False
            error_message = (
                f"\n---语法错误 No.{error_logger.count} ---\n"
                f"-使用了不存在的SCL函数 {func}() ! \n"
                f"-代码上下文 : {func}() ! \n"
                f"-反馈信息 : 1.仔细分析使用该函数的目的,并替换为合适的SCL库函数。\n 2.如果库函数列表中没有可用函数,不要自己定义函数。使用朴素的循环、分支、顺序结构实现目标。\n 3.使用规范的类型转换函数\n"
            )
            error_logger.count += 1
            error_log += error_message
    return listener_pack['error_log'] + error_log + error_logger.error_log , not listener_pack['has_error'] and SUCCESS and error_logger.SUCCESS

# if __name__ == '__main__':
#     file_path = '/root/MapCoder/src/promptings/agents/antlr/input.scl'
#     with open(file_path,'r') as fp:
#         error, success = syntax_check(fp.read())
#         print(error, success)
#     # print(json.dumps(parse_g4_file('antlr_genetated/scl.g4')))


