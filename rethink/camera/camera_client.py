import socket
import numpy as np
import cv2


def receive_data(sock):
    data_size_bytes = sock.recv(4)
    data_size = int.from_bytes(data_size_bytes, byteorder='big')
    data = b''
    while len(data) < data_size:
        packet = sock.recv(min(4096, data_size - len(data)))
        if not packet:
            break
        data += packet
    return data


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', 8080)
    client_socket.connect(server_address)
    print('已连接到服务器')
    try:
        while True:
            # 接收深度图像数据
            depth_image_bytes = receive_data(client_socket)
            if not depth_image_bytes:
                break
            depth_image = np.frombuffer(depth_image_bytes, dtype=np.uint16)
            depth_image = depth_image.reshape((480, 640))

            # 接收RGB图像数据
            color_image_bytes = receive_data(client_socket)
            if not color_image_bytes:
                break
            color_image = np.frombuffer(color_image_bytes, dtype=np.uint8)
            color_image = color_image.reshape((480, 640, 3))

            # 归一化深度图像用于显示
            depth_image_vis = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            depth_image_vis = cv2.cvtColor(depth_image_vis, cv2.COLOR_GRAY2BGR)

            # 水平拼接彩色图像和深度图像
            combined_image = np.hstack((color_image, depth_image_vis))
            cv2.imshow('Received RGB and Depth Image', combined_image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            print('接收到的深度图像形状:', depth_image.shape)
            print('接收到的RGB图像形状:', color_image.shape)
    except Exception as e:
        print('错误:', e)
    finally:
        client_socket.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()