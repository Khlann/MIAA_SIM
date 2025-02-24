import json
import os

# 初始深度序列
depth_sequence = [1, 2, 3, 4, 5, 6, 7, 8]
state_file = "depth_sequence_state.json"

def get_next_depth_value():
    """
    获取深度序列的下一个值，循环利用，并持久化状态。
    """
    global depth_sequence
    # 加载状态
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            current_sequence = json.load(f)
    else:
        current_sequence = depth_sequence.copy()

    # 获取第一个值并更新序列
    if current_sequence:
        value = current_sequence.pop(0)
    else:
        # 如果序列为空，恢复初始序列
        current_sequence = depth_sequence.copy()
        value = current_sequence.pop(0)

    # 保存更新后的状态
    with open(state_file, "w") as f:
        json.dump(current_sequence, f)

    return value