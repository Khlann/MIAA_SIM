import socket
import multiprocessing
import pyrealsense2 as rs
import numpy as np


def send_data(sock, data):
    data_size = len(data)
    sock.sendall(data_size.to_bytes(4, byteorder='big'))
    sock.sendall(data)


def tcp_server_process(queue):
    # 创建TCP/IP套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = ('127.0.0.1', 8080)
    server_socket.bind(server_address)
    server_socket.listen(1)
    print('等待客户端连接...')

    while True:
        client_socket, client_address = server_socket.accept()
        print('客户端已连接:', client_address)
        try:
            while True:
                if not queue.empty():
                    depth_image_bytes, color_image_bytes = queue.get()
                    send_data(client_socket, depth_image_bytes)
                    send_data(client_socket, color_image_bytes)
        except Exception as e:
            print('错误:', e)
        finally:
            client_socket.close()


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

            depth_image_bytes = depth_image.tobytes()
            color_image_bytes = color_image.tobytes()
            queue.put((depth_image_bytes, color_image_bytes))
    finally:
        pipeline.stop()


if __name__ == "__main__":
    # 创建进程间通信的队列
    queue = multiprocessing.Queue()

    # 创建并启动TCP服务器进程
    tcp_server = multiprocessing.Process(target=tcp_server_process, args=(queue,))
    tcp_server.start()

    # 创建并启动相机数据获取进程
    camera = multiprocessing.Process(target=camera_process, args=(queue,))
    camera.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        # 当按下Ctrl + C时，关闭相机进程和服务器进程
        camera.terminate()
        tcp_server.terminate()
        camera.join()
        tcp_server.join()