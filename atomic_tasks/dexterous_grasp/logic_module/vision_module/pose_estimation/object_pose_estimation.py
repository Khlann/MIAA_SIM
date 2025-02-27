import cv2
import numpy as np
class Estimation:
    def __init__(self):
        pass

    def process_mask_and_transform(self, mask, cam):
        # 求出mask的中心点,mask是一个二值图像,0表示背景,255表示前景
        # 求出mask的中心点
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
                    
        # x_3d , y_3d, z_3d = cam.xy2d2xy3d(cx, cy)
        P_O_C = np.array([x_3d, y_3d, z_3d])
        return P_O_C
        # print(f"cx:{cx},cy:{cy}")