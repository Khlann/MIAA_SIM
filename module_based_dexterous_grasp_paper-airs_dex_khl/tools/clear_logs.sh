#!/bin/bash

# 获取当前脚本所在的目录，假设脚本放在项目根目录下的 tools 目录
SCRIPT_DIR=$(dirname "$(realpath "$0")")
# 设置项目根目录为脚本所在目录的上级目录
PROJECT_ROOT=$(realpath "$SCRIPT_DIR/..")

# 设置日志目录
LOGS_DIR="$PROJECT_ROOT/logs"

# 检查日志目录是否存在
if [ -d "$LOGS_DIR" ]; then
    echo "Clearing logs in $LOGS_DIR"
    rm -rf "$LOGS_DIR"/*
    echo "Logs cleared."
else
    echo "Logs directory does not exist."
fi
