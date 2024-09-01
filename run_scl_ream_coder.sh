#!/bin/bash

export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m scl_team_coder

# 生成镜像
# docker build -t scl_team_coder .

# 导出镜像
# docker save scl_team_coder | gzip > scl_team_coder.tar.gz

# 导入镜像
# 解压得到.tar镜像
# gzip -d scl_team_coder.tar.gz
# 导入.tar镜像到docker
# docker load -i scl_team_coder.tar
# docker image ls

# 创建实例并且运行
# docker run -d -p 8000:8000 --name coder scl_team_coder

# 模拟外界测试接口
# curl -X POST http://localhost:8000/ -H "Content-Type: application/json" -d @./rag_data/data/初赛题目/FB_WarehouseManagement.json

# 查看日志（另一个终端）
# docker logs -f coder