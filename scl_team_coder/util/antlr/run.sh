#!/bin/bash
# 加载环境
export CLASSPATH=".:/usr/local/lib/antlr-4.13.1-complete.jar:$CLASSPATH"
alias antlr4='java -Xmx500M -cp "/usr/local/lib/antlr-4.13.1-complete.jar:$CLASSPATH" org.antlr.v4.Tool'
alias grun='java -Xmx500M -cp "/usr/local/lib/antlr-4.13.1-complete.jar:$CLASSPATH" org.antlr.v4.gui.TestRig'
pip install antlr-python-runtime==4.13.1
source ~/.bashrc
# 使用ANTLR4生成解析器
antlr4 -Dlanguage=Python3 -visitor scl.g4

