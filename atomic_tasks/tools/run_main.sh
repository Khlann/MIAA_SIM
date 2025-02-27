#!/bin/bash

source "$(dirname "$(realpath "$0")")/env_setup.sh"

# 检查是否传递了 "clear" 参数
if [ "$1" == "clear" ]; then
    # 调用 clear_logs.sh 清理日志
    echo "Calling clear_logs.sh script..."
    bash "$SCRIPT_DIR/clear_logs.sh"
fi

# 运行指定的单元测试脚本
python3 "$PROJECT_ROOT/main.py"
