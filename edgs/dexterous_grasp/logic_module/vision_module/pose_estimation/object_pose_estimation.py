import cv2
import numpy as np

class Estimation:
    def __init__(self):
        pass
  
    def get_rotation_angle(self, mask):
        _, binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

        try:
            if len(mask[0][0]) == 3:
                binary = cv2.cvtColor(binary, cv2.COLOR_BGR2GRAY)
        except:
            pass
        # 查找轮廓
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 找到最大轮廓
        max_contour = max(contours, key=cv2.contourArea)

        # 计算最大外接多边形
        epsilon = 0.01 * cv2.arcLength(max_contour, True)
        approx = cv2.approxPolyDP(max_contour, epsilon, True)

        # 找到最长斜边
        max_length = 0
        longest_edge = None
        for i in range(len(approx)):
            p1 = approx[i][0]
            p2 = approx[(i + 1) % len(approx)][0]
            length = np.linalg.norm(p1 - p2)
            if length > max_length:
                max_length = length
                longest_edge = (p1, p2)

        # 显示最长斜边
        cv2.line(mask, tuple(longest_edge[0]), tuple(longest_edge[1]), (0, 0, 255), 2)

        # 计算斜边与 x 轴的夹角
        dx = longest_edge[1][0] - longest_edge[0][0]
        dy = longest_edge[1][1] - longest_edge[0][1]
        angle = np.arctan2(dy, dx) * 180 / np.pi

        print(f"最长斜边与 x 轴的夹角: {angle} 度")
        # Visulaization
        # 绘制表示夹角的箭头
        start_point = tuple(longest_edge[0])
        end_point = tuple(longest_edge[1])
        # 沿着 x 轴正方向画一条辅助线
        x_axis_end = (start_point[0] + 100, start_point[1])
        cv2.line(mask, start_point, x_axis_end, (255, 0, 0), 2)  # 蓝色辅助线
        # 画表示夹角的箭头
        cv2.arrowedLine(mask, start_point, end_point, (0, 255, 0), 2)

        # 显示结果
        cv2.imshow('Max Enclosing Polygon with Longest Edge', mask)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        # angle 转为弧度
        angle = np.radians(angle)
        if angle < 0:
            angle = np.pi + angle
        # angle = abs(angle)

        # angle = np.pi/2 - angle
        # angle = abs(angle)
        angle_1 = angle- np.pi/2
        angle_2 = angle + np.pi/2
        if angle_1 > 0 and angle_1 < np.pi:
            angle = angle_1
        elif angle_2 > 0 and angle_2 < np.pi:
            angle = angle_2
        # angle = angle_1 if angle> 0 else angle_2
# 
        return angle

    def process_mask_and_transform(self, mask, cam):
        # 求rotation
        angle = self.get_rotation_angle(mask)
        try:
            if len(mask[0][0]) == 3:
                mask = mask[:, :, 0]
        except:
            print("mask is not a 3 channel image")

        mask = mask.astype(np.uint8)
        M = cv2.moments(mask)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        x_3d_list = []
        y_3d_list = []
        z_3d_list = []
        for i in range(cx-5, cx+5):
            for j in range(cy-5, cy+5):
                if mask[j, i] == 255:
                    x_3d, y_3d, z_3d = x_3d, y_3d, z_3d = cam.xy2d2xy3d(i, j)
                    if z_3d > 0:
                        x_3d_list.append(x_3d)
                        y_3d_list.append(y_3d)
                        z_3d_list.append(z_3d)
        x_3d = np.mean(x_3d_list)
        y_3d = np.mean(y_3d_list)
        z_3d = np.mean(z_3d_list)
                    
        P_O_C = np.array([x_3d, y_3d, z_3d])
        return P_O_C , angle