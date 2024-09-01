// Generated from /root/TIA/SCLTeamCoder/scl_team_coder/util/antlr/antlr_genetated/scl.g4 by ANTLR 4.13.1
import org.antlr.v4.runtime.tree.ParseTreeListener;

/**
 * This interface defines a complete listener for a parse tree produced by
 * {@link sclParser}.
 */
public interface sclListener extends ParseTreeListener {
	/**
	 * Enter a parse tree produced by {@link sclParser#r}.
	 * @param ctx the parse tree
	 */
	void enterR(sclParser.RContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#r}.
	 * @param ctx the parse tree
	 */
	void exitR(sclParser.RContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#whileStatement}.
	 * @param ctx the parse tree
	 */
	void enterWhileStatement(sclParser.WhileStatementContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#whileStatement}.
	 * @param ctx the parse tree
	 */
	void exitWhileStatement(sclParser.WhileStatementContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#forStatement}.
	 * @param ctx the parse tree
	 */
	void enterForStatement(sclParser.ForStatementContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#forStatement}.
	 * @param ctx the parse tree
	 */
	void exitForStatement(sclParser.ForStatementContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#ifStatement}.
	 * @param ctx the parse tree
	 */
	void enterIfStatement(sclParser.IfStatementContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#ifStatement}.
	 * @param ctx the parse tree
	 */
	void exitIfStatement(sclParser.IfStatementContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#whileCondition}.
	 * @param ctx the parse tree
	 */
	void enterWhileCondition(sclParser.WhileConditionContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#whileCondition}.
	 * @param ctx the parse tree
	 */
	void exitWhileCondition(sclParser.WhileConditionContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#whileBlockStatements}.
	 * @param ctx the parse tree
	 */
	void enterWhileBlockStatements(sclParser.WhileBlockStatementsContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#whileBlockStatements}.
	 * @param ctx the parse tree
	 */
	void exitWhileBlockStatements(sclParser.WhileBlockStatementsContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#repeatStatement}.
	 * @param ctx the parse tree
	 */
	void enterRepeatStatement(sclParser.RepeatStatementContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#repeatStatement}.
	 * @param ctx the parse tree
	 */
	void exitRepeatStatement(sclParser.RepeatStatementContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#switchStatement}.
	 * @param ctx the parse tree
	 */
	void enterSwitchStatement(sclParser.SwitchStatementContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#switchStatement}.
	 * @param ctx the parse tree
	 */
	void exitSwitchStatement(sclParser.SwitchStatementContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#block}.
	 * @param ctx the parse tree
	 */
	void enterBlock(sclParser.BlockContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#block}.
	 * @param ctx the parse tree
	 */
	void exitBlock(sclParser.BlockContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#dataBlock}.
	 * @param ctx the parse tree
	 */
	void enterDataBlock(sclParser.DataBlockContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#dataBlock}.
	 * @param ctx the parse tree
	 */
	void exitDataBlock(sclParser.DataBlockContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#typeBlock}.
	 * @param ctx the parse tree
	 */
	void enterTypeBlock(sclParser.TypeBlockContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#typeBlock}.
	 * @param ctx the parse tree
	 */
	void exitTypeBlock(sclParser.TypeBlockContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#fbBlock}.
	 * @param ctx the parse tree
	 */
	void enterFbBlock(sclParser.FbBlockContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#fbBlock}.
	 * @param ctx the parse tree
	 */
	void exitFbBlock(sclParser.FbBlockContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#fcBlock}.
	 * @param ctx the parse tree
	 */
	void enterFcBlock(sclParser.FcBlockContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#fcBlock}.
	 * @param ctx the parse tree
	 */
	void exitFcBlock(sclParser.FcBlockContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#blockName}.
	 * @param ctx the parse tree
	 */
	void enterBlockName(sclParser.BlockNameContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#blockName}.
	 * @param ctx the parse tree
	 */
	void exitBlockName(sclParser.BlockNameContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#dbInstanceName}.
	 * @param ctx the parse tree
	 */
	void enterDbInstanceName(sclParser.DbInstanceNameContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#dbInstanceName}.
	 * @param ctx the parse tree
	 */
	void exitDbInstanceName(sclParser.DbInstanceNameContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#structType}.
	 * @param ctx the parse tree
	 */
	void enterStructType(sclParser.StructTypeContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#structType}.
	 * @param ctx the parse tree
	 */
	void exitStructType(sclParser.StructTypeContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#variableDefinitions}.
	 * @param ctx the parse tree
	 */
	void enterVariableDefinitions(sclParser.VariableDefinitionsContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#variableDefinitions}.
	 * @param ctx the parse tree
	 */
	void exitVariableDefinitions(sclParser.VariableDefinitionsContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#variableDefinition}.
	 * @param ctx the parse tree
	 */
	void enterVariableDefinition(sclParser.VariableDefinitionContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#variableDefinition}.
	 * @param ctx the parse tree
	 */
	void exitVariableDefinition(sclParser.VariableDefinitionContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#weirdThing}.
	 * @param ctx the parse tree
	 */
	void enterWeirdThing(sclParser.WeirdThingContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#weirdThing}.
	 * @param ctx the parse tree
	 */
	void exitWeirdThing(sclParser.WeirdThingContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#constant_assign}.
	 * @param ctx the parse tree
	 */
	void enterConstant_assign(sclParser.Constant_assignContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#constant_assign}.
	 * @param ctx the parse tree
	 */
	void exitConstant_assign(sclParser.Constant_assignContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#variableType}.
	 * @param ctx the parse tree
	 */
	void enterVariableType(sclParser.VariableTypeContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#variableType}.
	 * @param ctx the parse tree
	 */
	void exitVariableType(sclParser.VariableTypeContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#udtType}.
	 * @param ctx the parse tree
	 */
	void enterUdtType(sclParser.UdtTypeContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#udtType}.
	 * @param ctx the parse tree
	 */
	void exitUdtType(sclParser.UdtTypeContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#elementaryType}.
	 * @param ctx the parse tree
	 */
	void enterElementaryType(sclParser.ElementaryTypeContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#elementaryType}.
	 * @param ctx the parse tree
	 */
	void exitElementaryType(sclParser.ElementaryTypeContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#arrayType}.
	 * @param ctx the parse tree
	 */
	void enterArrayType(sclParser.ArrayTypeContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#arrayType}.
	 * @param ctx the parse tree
	 */
	void exitArrayType(sclParser.ArrayTypeContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#arrayRange}.
	 * @param ctx the parse tree
	 */
	void enterArrayRange(sclParser.ArrayRangeContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#arrayRange}.
	 * @param ctx the parse tree
	 */
	void exitArrayRange(sclParser.ArrayRangeContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#dbAssignments}.
	 * @param ctx the parse tree
	 */
	void enterDbAssignments(sclParser.DbAssignmentsContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#dbAssignments}.
	 * @param ctx the parse tree
	 */
	void exitDbAssignments(sclParser.DbAssignmentsContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#dbAssignment}.
	 * @param ctx the parse tree
	 */
	void enterDbAssignment(sclParser.DbAssignmentContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#dbAssignment}.
	 * @param ctx the parse tree
	 */
	void exitDbAssignment(sclParser.DbAssignmentContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#nonRetainBlock}.
	 * @param ctx the parse tree
	 */
	void enterNonRetainBlock(sclParser.NonRetainBlockContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#nonRetainBlock}.
	 * @param ctx the parse tree
	 */
	void exitNonRetainBlock(sclParser.NonRetainBlockContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#blockVarDeclarations}.
	 * @param ctx the parse tree
	 */
	void enterBlockVarDeclarations(sclParser.BlockVarDeclarationsContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#blockVarDeclarations}.
	 * @param ctx the parse tree
	 */
	void exitBlockVarDeclarations(sclParser.BlockVarDeclarationsContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#blockTempVars}.
	 * @param ctx the parse tree
	 */
	void enterBlockTempVars(sclParser.BlockTempVarsContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#blockTempVars}.
	 * @param ctx the parse tree
	 */
	void exitBlockTempVars(sclParser.BlockTempVarsContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#blockInOutDeclarations}.
	 * @param ctx the parse tree
	 */
	void enterBlockInOutDeclarations(sclParser.BlockInOutDeclarationsContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#blockInOutDeclarations}.
	 * @param ctx the parse tree
	 */
	void exitBlockInOutDeclarations(sclParser.BlockInOutDeclarationsContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#blockInputDeclarations}.
	 * @param ctx the parse tree
	 */
	void enterBlockInputDeclarations(sclParser.BlockInputDeclarationsContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#blockInputDeclarations}.
	 * @param ctx the parse tree
	 */
	void exitBlockInputDeclarations(sclParser.BlockInputDeclarationsContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#blockOutputDeclarations}.
	 * @param ctx the parse tree
	 */
	void enterBlockOutputDeclarations(sclParser.BlockOutputDeclarationsContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#blockOutputDeclarations}.
	 * @param ctx the parse tree
	 */
	void exitBlockOutputDeclarations(sclParser.BlockOutputDeclarationsContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#blockConstDeclarations}.
	 * @param ctx the parse tree
	 */
	void enterBlockConstDeclarations(sclParser.BlockConstDeclarationsContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#blockConstDeclarations}.
	 * @param ctx the parse tree
	 */
	void exitBlockConstDeclarations(sclParser.BlockConstDeclarationsContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#blockStaticDeclarations}.
	 * @param ctx the parse tree
	 */
	void enterBlockStaticDeclarations(sclParser.BlockStaticDeclarationsContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#blockStaticDeclarations}.
	 * @param ctx the parse tree
	 */
	void exitBlockStaticDeclarations(sclParser.BlockStaticDeclarationsContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#blockConstantDeclarations}.
	 * @param ctx the parse tree
	 */
	void enterBlockConstantDeclarations(sclParser.BlockConstantDeclarationsContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#blockConstantDeclarations}.
	 * @param ctx the parse tree
	 */
	void exitBlockConstantDeclarations(sclParser.BlockConstantDeclarationsContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#blockLabelDeclarations}.
	 * @param ctx the parse tree
	 */
	void enterBlockLabelDeclarations(sclParser.BlockLabelDeclarationsContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#blockLabelDeclarations}.
	 * @param ctx the parse tree
	 */
	void exitBlockLabelDeclarations(sclParser.BlockLabelDeclarationsContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#blockFunctionality}.
	 * @param ctx the parse tree
	 */
	void enterBlockFunctionality(sclParser.BlockFunctionalityContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#blockFunctionality}.
	 * @param ctx the parse tree
	 */
	void exitBlockFunctionality(sclParser.BlockFunctionalityContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#function_type}.
	 * @param ctx the parse tree
	 */
	void enterFunction_type(sclParser.Function_typeContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#function_type}.
	 * @param ctx the parse tree
	 */
	void exitFunction_type(sclParser.Function_typeContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#stat}.
	 * @param ctx the parse tree
	 */
	void enterStat(sclParser.StatContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#stat}.
	 * @param ctx the parse tree
	 */
	void exitStat(sclParser.StatContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#functionStatement}.
	 * @param ctx the parse tree
	 */
	void enterFunctionStatement(sclParser.FunctionStatementContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#functionStatement}.
	 * @param ctx the parse tree
	 */
	void exitFunctionStatement(sclParser.FunctionStatementContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#labelStatment}.
	 * @param ctx the parse tree
	 */
	void enterLabelStatment(sclParser.LabelStatmentContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#labelStatment}.
	 * @param ctx the parse tree
	 */
	void exitLabelStatment(sclParser.LabelStatmentContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#forInitialCondition}.
	 * @param ctx the parse tree
	 */
	void enterForInitialCondition(sclParser.ForInitialConditionContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#forInitialCondition}.
	 * @param ctx the parse tree
	 */
	void exitForInitialCondition(sclParser.ForInitialConditionContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#forEndCondition}.
	 * @param ctx the parse tree
	 */
	void enterForEndCondition(sclParser.ForEndConditionContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#forEndCondition}.
	 * @param ctx the parse tree
	 */
	void exitForEndCondition(sclParser.ForEndConditionContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#forStepCondition}.
	 * @param ctx the parse tree
	 */
	void enterForStepCondition(sclParser.ForStepConditionContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#forStepCondition}.
	 * @param ctx the parse tree
	 */
	void exitForStepCondition(sclParser.ForStepConditionContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#forBlockStatements}.
	 * @param ctx the parse tree
	 */
	void enterForBlockStatements(sclParser.ForBlockStatementsContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#forBlockStatements}.
	 * @param ctx the parse tree
	 */
	void exitForBlockStatements(sclParser.ForBlockStatementsContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#ifCondition}.
	 * @param ctx the parse tree
	 */
	void enterIfCondition(sclParser.IfConditionContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#ifCondition}.
	 * @param ctx the parse tree
	 */
	void exitIfCondition(sclParser.IfConditionContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#ifBlockStatments}.
	 * @param ctx the parse tree
	 */
	void enterIfBlockStatments(sclParser.IfBlockStatmentsContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#ifBlockStatments}.
	 * @param ctx the parse tree
	 */
	void exitIfBlockStatments(sclParser.IfBlockStatmentsContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#switchBlock}.
	 * @param ctx the parse tree
	 */
	void enterSwitchBlock(sclParser.SwitchBlockContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#switchBlock}.
	 * @param ctx the parse tree
	 */
	void exitSwitchBlock(sclParser.SwitchBlockContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#switchLabel}.
	 * @param ctx the parse tree
	 */
	void enterSwitchLabel(sclParser.SwitchLabelContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#switchLabel}.
	 * @param ctx the parse tree
	 */
	void exitSwitchLabel(sclParser.SwitchLabelContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#switchLabelConstant}.
	 * @param ctx the parse tree
	 */
	void enterSwitchLabelConstant(sclParser.SwitchLabelConstantContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#switchLabelConstant}.
	 * @param ctx the parse tree
	 */
	void exitSwitchLabelConstant(sclParser.SwitchLabelConstantContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#switchBlockStatements}.
	 * @param ctx the parse tree
	 */
	void enterSwitchBlockStatements(sclParser.SwitchBlockStatementsContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#switchBlockStatements}.
	 * @param ctx the parse tree
	 */
	void exitSwitchBlockStatements(sclParser.SwitchBlockStatementsContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#defualtswitchBlockStatements}.
	 * @param ctx the parse tree
	 */
	void enterDefualtswitchBlockStatements(sclParser.DefualtswitchBlockStatementsContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#defualtswitchBlockStatements}.
	 * @param ctx the parse tree
	 */
	void exitDefualtswitchBlockStatements(sclParser.DefualtswitchBlockStatementsContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#assignmentStatement}.
	 * @param ctx the parse tree
	 */
	void enterAssignmentStatement(sclParser.AssignmentStatementContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#assignmentStatement}.
	 * @param ctx the parse tree
	 */
	void exitAssignmentStatement(sclParser.AssignmentStatementContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#leftHandAssignment}.
	 * @param ctx the parse tree
	 */
	void enterLeftHandAssignment(sclParser.LeftHandAssignmentContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#leftHandAssignment}.
	 * @param ctx the parse tree
	 */
	void exitLeftHandAssignment(sclParser.LeftHandAssignmentContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#rightHandAssignment}.
	 * @param ctx the parse tree
	 */
	void enterRightHandAssignment(sclParser.RightHandAssignmentContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#rightHandAssignment}.
	 * @param ctx the parse tree
	 */
	void exitRightHandAssignment(sclParser.RightHandAssignmentContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#expr}.
	 * @param ctx the parse tree
	 */
	void enterExpr(sclParser.ExprContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#expr}.
	 * @param ctx the parse tree
	 */
	void exitExpr(sclParser.ExprContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#functionParameterExpression}.
	 * @param ctx the parse tree
	 */
	void enterFunctionParameterExpression(sclParser.FunctionParameterExpressionContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#functionParameterExpression}.
	 * @param ctx the parse tree
	 */
	void exitFunctionParameterExpression(sclParser.FunctionParameterExpressionContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#inputParameter}.
	 * @param ctx the parse tree
	 */
	void enterInputParameter(sclParser.InputParameterContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#inputParameter}.
	 * @param ctx the parse tree
	 */
	void exitInputParameter(sclParser.InputParameterContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#outputParameter}.
	 * @param ctx the parse tree
	 */
	void enterOutputParameter(sclParser.OutputParameterContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#outputParameter}.
	 * @param ctx the parse tree
	 */
	void exitOutputParameter(sclParser.OutputParameterContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#numberConstant}.
	 * @param ctx the parse tree
	 */
	void enterNumberConstant(sclParser.NumberConstantContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#numberConstant}.
	 * @param ctx the parse tree
	 */
	void exitNumberConstant(sclParser.NumberConstantContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#constant}.
	 * @param ctx the parse tree
	 */
	void enterConstant(sclParser.ConstantContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#constant}.
	 * @param ctx the parse tree
	 */
	void exitConstant(sclParser.ConstantContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#expressionName}.
	 * @param ctx the parse tree
	 */
	void enterExpressionName(sclParser.ExpressionNameContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#expressionName}.
	 * @param ctx the parse tree
	 */
	void exitExpressionName(sclParser.ExpressionNameContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#ambiguousName}.
	 * @param ctx the parse tree
	 */
	void enterAmbiguousName(sclParser.AmbiguousNameContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#ambiguousName}.
	 * @param ctx the parse tree
	 */
	void exitAmbiguousName(sclParser.AmbiguousNameContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#identifierIndex}.
	 * @param ctx the parse tree
	 */
	void enterIdentifierIndex(sclParser.IdentifierIndexContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#identifierIndex}.
	 * @param ctx the parse tree
	 */
	void exitIdentifierIndex(sclParser.IdentifierIndexContext ctx);
	/**
	 * Enter a parse tree produced by {@link sclParser#identifierIndexValue}.
	 * @param ctx the parse tree
	 */
	void enterIdentifierIndexValue(sclParser.IdentifierIndexValueContext ctx);
	/**
	 * Exit a parse tree produced by {@link sclParser#identifierIndexValue}.
	 * @param ctx the parse tree
	 */
	void exitIdentifierIndexValue(sclParser.IdentifierIndexValueContext ctx);
}