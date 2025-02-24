#!/bin/bash

# 获取当前脚本所在的目录，假设脚本放在项目根目录下的 tools 目录
SCRIPT_DIR=$(dirname "$(realpath "$0")")
# 设置项目根目录为脚本所在目录的上级目录
PROJECT_ROOT=$(realpath "$SCRIPT_DIR/..")
EXTERNAL_ROOT="$PROJECT_ROOT/external"
EXTERNAL_SAM_ROOT="$PROJECT_ROOT/external/gsam2"

# 设置 PYTHONPATH 为项目根目录
export PROJECT_ROOT="$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT:$EXTERNAL_ROOT:$EXTERNAL_SAM_ROOT:$PYTHONPATH"

