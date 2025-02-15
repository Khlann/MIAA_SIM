import pyrealsense2 as rs
import numpy as np
import multiprocessing
import cv2


def camera_process(queue):
    # 配置并启动相机
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipeline.start(config)

    try:
        while True:
            # 获取相机帧
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # 归一化深度图像用于显示
            depth_image_vis = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            depth_image_vis = cv2.cvtColor(depth_image_vis, cv2.COLOR_GRAY2BGR)

            # 水平拼接彩色图像和深度图像
            combined_image = np.hstack((color_image, depth_image_vis))
            cv2.imshow('RGB and Depth Image', combined_image)

            # 将数据转换为字节并放入队列
            depth_image_bytes = depth_image.tobytes()
            color_image_bytes = color_image.tobytes()
            queue.put((depth_image_bytes, color_image_bytes))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # 创建进程间通信的队列，要与tcp_server.py中的队列名称一致
    queue = multiprocessing.Queue()

    # 创建并启动相机数据获取进程
    camera = multiprocessing.Process(target=camera_process, args=(queue,))
    camera.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        # 当按下Ctrl+C时，关闭相机进程
        camera.terminate()
        camera.join()