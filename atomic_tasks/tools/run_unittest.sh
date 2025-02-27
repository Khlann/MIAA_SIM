#!/bin/bash

# 引入环境设置脚本
source "$(dirname "$(realpath "$0")")/env_setup.sh"

# 检查是否传入单元测试脚本
if [ -z "$1" ]; then
  echo "请传入单元测试脚本路径"
  exit 1
fi

# 运行指定的单元测试脚本
python3 -m unittest "$1"
