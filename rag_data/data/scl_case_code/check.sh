#!/bin/bash

# 设置要检查的目录路径
DIRECTORY="."

# 遍历目录中的所有 .json 文件
for json_file in "$DIRECTORY"/*.json; do
    # 获取不带扩展名的文件名
    base_name=$(basename "$json_file" .json)

    # 检查是否存在同名的 .scl 文件
    # if [ ! -f "$DIRECTORY/$base_name.scl" ]; then
    #     # 如果没有同名的 .scl 文件，输出 .json 文件的名字
    #     echo "$json_file has no scl codes."
    # fi
    if [ ! -f "../scl_case_plan_0520/$base_name.plan" ]; then
        echo "$json_file has no algos."
    fi
done

