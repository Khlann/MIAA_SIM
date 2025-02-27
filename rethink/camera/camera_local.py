import pyrealsense2 as rs
import numpy as np
import multiprocessing
import cv2


def camera_process(queue):
    # 配置并启动相机
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 30)

    # 创建对齐对象，将深度帧对齐到彩色帧
    align_to = rs.stream.color
    align = rs.align(align_to)

    pipeline.start(config)

    try:
        while True:
            # 获取相机帧
            frames = pipeline.wait_for_frames()

            # 对帧进行对齐
            aligned_frames = align.process(frames)

            # 获取对齐后的深度帧和彩色帧
            aligned_depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()

            if not aligned_depth_frame or not color_frame:
                continue

            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # 归一化深度图像用于显示
            depth_image_vis = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            depth_image_vis = cv2.cvtColor(depth_image_vis, cv2.COLOR_GRAY2BGR)

            # 调整彩色图像大小以匹配深度图像的大小（可选）
            color_image = cv2.resize(color_image, (depth_image.shape[1], depth_image.shape[0]))

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