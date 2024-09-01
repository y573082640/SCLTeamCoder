from .sclListener import sclListener
from .sclParser import sclParser
from .sclLexer import sclLexer
import inspect
import json
import traceback
from antlr4 import *
special_type = ['\"LGF_ShellSort_DInt\"','FileWriteC','IEC_TIMER','TP_TIME','TON_TIME','TOF_TIME','TONR_TIME','R_TRIG','F_TRIG','HW_DEVICE','GEOADDR','HW_IOSYSTEM','DTL','FileReadC','\"LGF_typeDiagnostics\"']
def print_all_attributes(obj):
    # 打印对象的所有属性
    attributes = {attr: getattr(obj, attr) for attr in dir(obj) if not attr.startswith('__') and not inspect.isbuiltin(attr)}
    print("Attributes:")
    for attr, value in attributes.items():
        print(f"{attr}: {value}")

def print_all_methods(obj):
    # 打印对象的所有方法
    methods = [member for member in dir(obj) if inspect.ismethod(getattr(obj, member))]
    print("Methods:")
    for method in methods:
        print(method)

def get_rule_name(ctx):
    if isinstance(ctx, ParserRuleContext):
        rule_index = ctx.getRuleIndex()
        rule_name = ctx.parser.ruleNames[rule_index] if rule_index < len(ctx.parser.ruleNames) else "Unknown"
    else:
        rule_name = 'TerminalNodeImpl'  # 如果子节点是TerminalNodeImpl，打印其文本内容
    return rule_name

def get_children_rule_and_text(ctx):
    ret = []
    for child in ctx.getChildren():
        ret.append((get_rule_name(child),child.getText()))
        # {'Rule':get_rule_name(child),'Text':child.getText()}
    return ret

# This class defines a complete listener for a parse tree produced by sclParser.
class MyListener(sclListener):
    def __init__(self,error_pack:dict):
        #  保存当前所处的上下文
        self.context_stack = []
        self.symbol_table = SymbolTable()  # 初始化符号表
        self.error_pack = error_pack
        self.error = False
        self.function_stack = []
        self.error_msg = []
        self.special_type_variable = {}
        self.no_define_symbols = set()

    def enterFcBlock(self, ctx: sclParser.FbBlockContext):
        self.context_stack.append(get_rule_name(ctx))
    
    def exitFcBlock(self, ctx: sclParser.FbBlockContext):
        self.context_stack.pop()
    
    def enterBlockName(self, ctx: sclParser.BlockNameContext):
        if 'fcBlock' not in self.context_stack:
            return
        block_name = ctx.getText()
        if block_name.startswith('"'):
            block_name = block_name[1:]  # 去除第一个字符
        if block_name.endswith('"'):
            block_name = block_name[:-1]  # 去除最后一个字符
        value=SymbolItem(name=block_name, type=None, value=None, context=None)
        self.symbol_table.add_symbol(name=value.name,value=value)

    def enterExpressionName(self, ctx: sclParser.ExpressionNameContext):
        # print(self.context_stack, ctx.getText())
        if 'ambiguousNext' in self.context_stack or 'functionStatement' in self.context_stack or 'variableDefinitions' in self.context_stack:
            return
        if 'varName' in self.context_stack or 'switchLabelConstant' in self.context_stack:
            identifiers = ctx.getTokens(sclParser.Identifier)
            # print(self.context_stack, [i.getText() for i in identifiers])
            # print([i.getText() for i in identifiers])
            for identifier in identifiers:
                iden_txt = identifier.getText()
                if iden_txt.startswith('#') or iden_txt.startswith('"'):
                    iden_txt = iden_txt[1:]  # 去除第一个字符
                if iden_txt.endswith('"'):
                    iden_txt = iden_txt[:-1]  # 去除最后一个字符
                if not self.symbol_table.has_symbol(iden_txt):
                    self.error = True
                    if iden_txt not in self.no_define_symbols:
                        self.error_msg.append(f"变量名 {iden_txt} 未定义! 请先在变量定义块(VAR/VAR_TEMP/VAR CONSTANT)当中定义该变量!请根据该变量使用场景将其定义于合适的变量块当中.")
                        self.no_define_symbols.add(iden_txt)

    def enterVariableDefinitions(self, ctx: sclParser.VariableDefinitionsContext):
        self.context_stack.append(get_rule_name(ctx))
    
    def exitVariableDefinitions(self, ctx: sclParser.VariableDefinitionsContext):
        self.context_stack.pop()

    # Enter a parse tree produced by sclParser#switchStatement.
    def enterSwitchStatement(self, ctx:sclParser.SwitchStatementContext):
        self.context_stack.append(get_rule_name(ctx))

    # Exit a parse tree produced by sclParser#switchStatement.
    def exitSwitchStatement(self, ctx:sclParser.SwitchStatementContext):
        self.context_stack.pop()

    # Enter a parse tree produced by sclParser#ifCondition.
    def enterIfCondition(self, ctx:sclParser.IfConditionContext):
        self.context_stack.append(get_rule_name(ctx))

    # Exit a parse tree produced by sclParser#ifCondition.
    def exitIfCondition(self, ctx:sclParser.IfConditionContext):
        self.context_stack.pop()

    # Enter a parse tree produced by sclParser#stat.
    def enterStat(self, ctx:sclParser.StatContext):
        self.context_stack.append(get_rule_name(ctx))

    # Exit a parse tree produced by sclParser#stat.
    def exitStat(self, ctx:sclParser.StatContext):
        self.context_stack.pop()

    # Exit a parse tree produced by sclParser#functionStatement.
    def exitFunctionStatement(self, ctx:sclParser.FunctionStatementContext):
        self.context_stack.pop()
        # self.function_stack.pop()

    # Enter a parse tree produced by sclParser#functionStatement.
    def enterFunctionStatement(self, ctx:sclParser.FunctionStatementContext):
        self.context_stack.append(get_rule_name(ctx))
        # print(self.context_stack,get_children_rule_and_text(ctx))
        for rule,text in get_children_rule_and_text(ctx):
            ident = text.replace("#","")
            if rule == 'expressionName':
                current_function = ident
            if rule == 'functionParameterExpression':
                if current_function == 'LEN' or current_function == 'STRING' or current_function == 'TypeOf':
                    self.error = True
                    self.error_msg.append(f"`{current_function}`包含错误参数{ident}。")                        
                if current_function == 'SHR' or current_function == 'SHL':
                    cnt = 0
                    for rule,text in get_children_rule_and_text(ctx):
                        if "IN:=" in ident:
                            cnt += 1
                        elif  "N:=" in ident:
                            cnt += 1
                    if cnt < 2:
                        self.error = True
                        self.error_msg.append(f"`{current_function}`参数错误。 `{current_function}` 需要指定`IN`和`N`参数")                        
                if current_function == 'UPPER_BOUND' or current_function == 'LOWER_BOUND':
                    cnt = 0
                    for rule,text in get_children_rule_and_text(ctx):
                        if "ARR:=" in ident:
                            cnt += 1
                        elif  "DIM:=" in ident:
                            cnt += 1
                    if cnt < 2:
                        self.error = True
                        self.error_msg.append(f"`{current_function}`参数错误。 `{current_function}` 需要指定`DIM`和`ARR`参数")                        
                    if "ARR:=" in ident:
                        parameter = ident.split(":=")[-1]
                        symbol = self.symbol_table.get_symbol(parameter)
                        if symbol is not None:
                            if not ('ARRAY' in symbol.type.upper() and '*' in symbol.type.upper()):
                                self.error = True
                                self.error_msg.append(f"`{current_function}`参数错误。 `{current_function}` 仅可用于形如 Array[*]/Array[*,*] 类型的可变上下限数组,而`{symbol.name}`为`{symbol.type}`类型。")                        
            if rule == 'expr':
                if current_function in ['SHR','SHL','UPPER_BOUND','LOWER_BOUND'] :
                    self.error = True
                    self.error_msg.append(f"`{current_function}`缺少具名参数。")                        
                if current_function == 'LEN':
                    symbol = self.symbol_table.get_symbol(ident)
                    if symbol is not None:
                        if not 'STRING' in symbol.type.upper():
                            self.error = True
                            self.error_msg.append(f"`{current_function}`参数类型错误。`{current_function}`仅用于 字符串 类型,而`{symbol.name}`为`{symbol.type}`类型。")                        
                elif current_function == 'CountOfElements':
                    symbol = self.symbol_table.get_symbol(ident)
                    if symbol is not None:
                        if not 'VARIANT' in symbol.type.upper():
                            self.error = True
                            self.error_msg.append(f"`{current_function}`参数类型错误。`{current_function}`仅用于 Variant 类型数组,而`{symbol.name}`为`{symbol.type}`类型。")                        
                elif current_function == 'TypeOf' or current_function == 'TypeOfElements':
                    if not ('ifCondition' in self.context_stack or 'switchStatement' in self.context_stack):
                        self.error = True
                        self.error_msg.append(f"不允许将`TypeOf`的结果赋值给操作数。`TypeOf` 需要在 IF 指令 或 CASE 指令中直接使用")     

    # Enter a parse tree produced by sclParser#expr.
    def enterExpr(self, ctx:sclParser.ExprContext):
        pass

    # Exit a parse tree produced by sclParser#expr.
    def exitExpr(self, ctx:sclParser.ExprContext):
        pass

    def enterAmbiguousNext(self, ctx: sclParser.AmbiguousNextContext):
        self.context_stack.append(get_rule_name(ctx))
    
    def exitAmbiguousNext(self, ctx: sclParser.AmbiguousNextContext):
        self.context_stack.pop()
    
    def enterVarName(self, ctx: sclParser.VarNameContext):
        self.context_stack.append(get_rule_name(ctx))
    
    def exitVarName(self, ctx: sclParser.VarNameContext):
        self.context_stack.pop()
    
    def enterSwitchLabelConstant(self, ctx: sclParser.SwitchLabelConstantContext):
        for child in ctx.getChildren():
            if isinstance(child, sclParser.ConstantContext) and child.BOOLLiteral() is not None:
                # Has Bool in of statement for judge.
                self.error = True
                self.error_msg.append(f"CASE语句当中不应使用Bool类型的值（与返回Bool类型的表达式）进行分支判断. 请使用IF/ELSE结构代替基于Bool判断的CASE语句.")
        self.context_stack.append(get_rule_name(ctx))
    
    def exitSwitchLabelConstant(self, ctx: sclParser.SwitchLabelConstantContext):
        self.context_stack.pop()

    def enterBlockVarDeclarations(self, ctx: sclParser.BlockVarDeclarationsContext):
        self.context_stack.append(get_rule_name(ctx))
    
    def exitBlockVarDeclarations(self, ctx: sclParser.BlockVarDeclarationsContext):
        self.context_stack.pop()

    # Enter a parse tree produced by sclParser#blockInOutDeclarations.
    def enterBlockInOutDeclarations(self, ctx:sclParser.BlockInOutDeclarationsContext):
        self.context_stack.append(get_rule_name(ctx))

    # Exit a parse tree produced by sclParser#blockInOutDeclarations.
    def exitBlockInOutDeclarations(self, ctx:sclParser.BlockInOutDeclarationsContext):
        self.context_stack.pop()


    # Enter a parse tree produced by sclParser#blockInputDeclarations.
    def enterBlockInputDeclarations(self, ctx:sclParser.BlockInputDeclarationsContext):
        self.context_stack.append(get_rule_name(ctx))

    # Exit a parse tree produced by sclParser#blockInputDeclarations.
    def exitBlockInputDeclarations(self, ctx:sclParser.BlockInputDeclarationsContext):
        self.context_stack.pop()

    # Enter a parse tree produced by sclParser#blockConstantDeclarations.
    def enterBlockConstantDeclarations(self, ctx:sclParser.BlockConstantDeclarationsContext):
        self.context_stack.append(get_rule_name(ctx))

    # Exit a parse tree produced by sclParser#blockConstantDeclarations.
    def exitBlockConstantDeclarations(self, ctx:sclParser.BlockConstantDeclarationsContext):
        self.context_stack.pop()

    # Enter a parse tree produced by sclParser#blockOutputDeclarations.
    def enterBlockOutputDeclarations(self, ctx:sclParser.BlockOutputDeclarationsContext):
        self.context_stack.append(get_rule_name(ctx))

    # Exit a parse tree produced by sclParser#blockOutputDeclarations.
    def exitBlockOutputDeclarations(self, ctx:sclParser.BlockOutputDeclarationsContext):
        self.context_stack.pop()

    # Enter a parse tree produced by sclParser#blockConstDeclarations.
    def enterBlockConstDeclarations(self, ctx:sclParser.BlockConstDeclarationsContext):
        self.context_stack.append(get_rule_name(ctx))

    # Exit a parse tree produced by sclParser#blockConstDeclarations.
    def exitBlockConstDeclarations(self, ctx:sclParser.BlockConstDeclarationsContext):
        self.context_stack.pop()

    # Enter a parse tree produced by sclParser#blockStaticDeclarations.
    def enterBlockStaticDeclarations(self, ctx:sclParser.BlockStaticDeclarationsContext):
        self.context_stack.append(get_rule_name(ctx))

    # Exit a parse tree produced by sclParser#blockStaticDeclarations.
    def exitBlockStaticDeclarations(self, ctx:sclParser.BlockStaticDeclarationsContext):
        self.context_stack.pop()

    # Enter a parse tree produced by sclParser#blockTempVars.
    def enterBlockTempVars(self, ctx:sclParser.BlockTempVarsContext):
        self.context_stack.append(get_rule_name(ctx))

    # Exit a parse tree produced by sclParser#blockTempVars.
    def exitBlockTempVars(self, ctx:sclParser.BlockTempVarsContext):
        self.context_stack.pop()

    # Enter a parse tree produced by sclParser#variableDefinition.
    def enterVariableDefinition(self, ctx:sclParser.VariableDefinitionContext):
        # print(self.context_stack,get_children_rule_and_text(ctx))
        value=SymbolItem(name=None, type=None, value=None, context=self.context_stack[-1])
        for rule,text in get_children_rule_and_text(ctx):
            if rule == 'expressionName':
                value.name = text
                if value.name.startswith('"'):
                    value.name = value.name[1:]  # 去除第一个字符
                if value.name.endswith('"'):
                    value.name = value.name[:-1]  # 去除最后一个字符
            if rule == 'variableType':
                value.type = text
                if text in special_type:
                    self.special_type_variable[value.name] = value.type 
            if rule == 'constant_assign':
                value.value = text
        # print(value)
        self.symbol_table.add_symbol(name=value.name,value=value)

    # Enter a parse tree produced by sclParser#forInitialCondition.
    def enterForInitialCondition(self, ctx:sclParser.ForInitialConditionContext):
        # print(get_children_rule_and_text(ctx))
        cycle_var = ""
        for rule,text in get_children_rule_and_text(ctx):
            if rule == 'assignmentStatement':
                # 检查是否初始化
                cycle_var = text.split(":=")[0]
            elif rule == 'expressionName':
                # 检查是否初始化
                cycle_var = text
        # 移除一些前缀操作
        cycle_var_no_prefix = cycle_var.replace("#",'').split(".")[0].split("[")[0].split("(")[0]
        keys = self.symbol_table.to_list().keys()
        if not cycle_var_no_prefix in keys:
            self.error = True
            self.error_msg.append(f"循环变量 {cycle_var_no_prefix} 未定义! 请先在VAR TEMP中定义该变量! 定义该变量时请满足FOR循环要求:FOR 语句中不允许组合使用带符号整数(如`DINT`)和不带符号整数(如`UDINT`)。使用不带符号整数时，无法编程负方向循环。")

    def check_all(self):
        try:
            for name,symble in self.symbol_table.to_list().items():
                if symble.context == "blockConstantDeclarations" and ('ARRAY' in symble.type or 'STRUCT' in symble.type):
                    self.error = True
                    self.error_msg.append(f"常量 {name} 错误!在VAR CONSTANT块不允许定义ARRAY或STRUCT类型的常量!")          
            # 检查变量定义
        except Exception as e:
            print(e)
            traceback.print_exc()

        for i in range(len(self.error_msg)):
            self.error_msg[i] = f"---语义错误 No.{i+1}---\n-反馈信息: {self.error_msg[i]}\n"

    def exitR(self, ctx:sclParser.RContext):
        # print(self.special_type_variable)
        self.check_all()
        self.error_pack['has_error'] = self.error
        self.error_pack['error_log'] = "\n".join(self.error_msg)
        self.error_pack['special_type_variable'] = self.special_type_variable

class Type:
    def __init__(self):
        super().__init__()

    def get_type_name(self):
        pass

    def get_type(self):
        pass


class Value:
    def __init__(self, value_type, name):
        self.userList = []  # 使用这个值的
        self.type = value_type  # 类型
        self.name = name  # 寄存器名

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> Type:
        return self.type

class SymbolItem:
    def __init__(self, name, type, value, context=None):
        self.name = name  # 名字
        self.type = type  # 类型，为CONST VARIABLE
        self.value = value  # 值
        self.context = context  # 数组分配空间

    def __str__(self):
        # 定义如何将 SymbolItem 实例转换为字符串
        # 这里使用简单的字符串格式化来展示所有属性
        context_str = f", context={self.context}" if self.context is not None else ""
        return f"SymbolItem(name={self.name}, type={self.type}, value={self.value}{context_str})"

class SymbolTable:
    def __init__(self, parent=None):
        self.symbol_table = {}
        self.parent = parent

    def get_symbol(self, name) -> SymbolItem:
        if self.symbol_table.__contains__(name):
            return self.symbol_table[name]
        else:
            return None

    def add_symbol(self, name: str, value) -> bool:
        if self.get_symbol(name) is not None:
            return False
        self.symbol_table[name] = value
        return True

    def update_symbol(self, name: str, value: Value):
        if self.symbol_table.__contains__(name):
            self.symbol_table[name].value = value

    def to_list(self):
        values = []
        for key, value in self.symbol_table.items():
            values.append(value.value)
        return self.symbol_table
    
    def has_symbol(self, name: str) -> bool:
        return name in self.symbol_table

