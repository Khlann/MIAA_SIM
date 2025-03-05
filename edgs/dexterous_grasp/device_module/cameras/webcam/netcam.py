"""
实现了一个基于RealSense相机的图像捕获API。
该API提供了一个端点，用于捕获图像并将其返回给客户端。
客户端可以通过发送GET请求来获取图像数据。
API使用Flask框架实现，并使用RealSense SDK来捕获图像。
"""
import cv2
import numpy as np
import pyrealsense2 as rs
from flask import Flask, jsonify
from flask_restx import Api, Resource, fields

app = Flask(__name__)
api = Api(app, version='1.0', title='RealSense Camera Capture API', description='API for capturing images from a RealSense camera')

ns = api.namespace('capture', description='RealSense camera capture operations')

camera_model = api.model('CameraImage', {
    'image': fields.String(description='The captured image in JPEG format')
})

@ns.route('/')
class CameraCapture(Resource):
    @ns.doc('capture_image')
    @ns.marshal_with(camera_model)
    def get(self):
        try:
            # 配置RealSense相机管道
            pipeline = rs.pipeline()
            config = rs.config()
            config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

            # 启动相机管道
            pipeline.start(config)

            try:
                # 等待一帧数据
                frames = pipeline.wait_for_frames()
                color_frame = frames.get_color_frame()

                if not color_frame:
                    return jsonify({"error": "无法获取图像"}), 500

                # 将图像数据转换为numpy数组
                frame = np.asanyarray(color_frame.get_data())

                # 将图像编码为JPEG格式
                _, img_encoded = cv2.imencode('.jpg', frame)
                img_bytes = img_encoded.tobytes()

            finally:
                # 停止相机管道
                pipeline.stop()

            # 返回图像数据
            return {'image': img_bytes}, 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)