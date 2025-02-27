import pyrealsense2 as rs
import numpy as np
import cv2
import re
# 配置RealSense管道
pipeline = rs.pipeline()
config = rs.config()

config.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 30)
# 开始流
pipeline.start(config)

# 用于保存点击的点
points = []

# 鼠标点击事件回调函数
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
            print(f"Point {len(points)}: ({x}, {y})")
        if len(points) == 4:
            print("4 points have been selected:", points)

# 创建窗口并设置鼠标回调
cv2.namedWindow('RealSense')
cv2.setMouseCallback('RealSense', mouse_callback)

try:
    while True:
        # 等待一组新的帧
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        color_image = np.asanyarray(color_frame.get_data())
        
        # 显示图像
        cv2.imshow('RealSense', color_image)
        
        # 按下q键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if len(points) == 4:
            break
finally:
    # 停止流
    pipeline.stop()
    cv2.destroyAllWindows()


# 利用上面的4个点，画一个四边形
mask = np.zeros((color_image.shape[0], color_image.shape[1]), dtype=np.uint8)
pts = np.array(points, np.int32)
pts = pts.reshape((-1, 1, 2))
cv2.polylines(mask, [pts], isClosed=True, color=(255, 255, 255), thickness=2)
cv2.fillPoly(mask, [pts], color=(255, 255, 255))

# 显示mask
cv2.imshow('mask', mask)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 将points保存在config中
config_path = "dexterous_grasp/config/vision_module_variant.py"


new_point_str = f"crop_point = {points}"

crop_point_regex = r"crop_point\s*=\s*\[\(.*?\)\]"

with open(config_path, "r") as file:
    config_content = file.read()

updated_config_content = re.sub(crop_point_regex, new_point_str, config_content, flags=re.DOTALL)

with open(config_path, "w") as file:
    file.write(updated_config_content)  