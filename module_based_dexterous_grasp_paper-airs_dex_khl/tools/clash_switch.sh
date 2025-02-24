#!/bin/bash

# 定义路径
CLASH_PATH="/home/airs/Application/clash_2.0.24_linux_arm64"
CONFIG_DIR="/home/airs/.config/clash"

# 定义 YAML 配置文件
CONFIG_YEKAI="${CONFIG_DIR}/config_yekai.yaml"
CONFIG_ZHENHUA="${CONFIG_DIR}/config_zhenhua.yaml"
CONFIG_MAIN="${CONFIG_DIR}/config.yaml"

# 根据输入参数切换 YAML 文件
if [ "$1" == "yekai" ]; then
    echo "切换到 yekai 配置文件"
    cp "$CONFIG_YEKAI" "$CONFIG_MAIN"
elif [ "$1" == "zhenhua" ]; then
    echo "切换到 zhenhua 配置文件"
    cp "$CONFIG_ZHENHUA" "$CONFIG_MAIN"
else
    echo "没有指定配置文件，使用当前配置文件启动 clash"
fi

# 启动 clash
echo "启动 clash..."
cd $CLASH_PATH
clash

