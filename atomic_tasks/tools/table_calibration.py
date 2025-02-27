
# from dexterous_grasp.device_module.cameras import D435i
import cv2
import numpy as np

raw_crop_point = [(649, 19), (1675, 23), (1652, 877), (644, 850)]
crop_point = [(647, 24), (1673, 28), (1650, 882), (642, 855)]

# Config
# 这里记录每一个任务的ee_base
# task1

# task2
battery_put = []
usb_put = []
# task3
red_botton = []
label_take = []
label_put = []
# task4
screwdriver_put = []
plugin_put = []

# 这里记录T_table_new_table
T_table_new_table = [
    
]
def draw_line(point1,point2,image):
    start_point = point1
    end_point = point2
    arrow_color = tuple(np.random.randint(0, 256, size=3).tolist())
    thickness =2
    line_type = cv2.LINE_AA
    cv2.arrowedLine(image,start_point,end_point,arrow_color,thickness,line_type)

def calculate_transform_2d(raw_points, new_points):
    # 将元组转换为 numpy 数组
    raw_points = np.array(raw_points)
    new_points = np.array(new_points)
    # 计算向量
    r_line_vector = np.array([raw_points[1] - raw_points[0], raw_points[1] - raw_points[2]])
    n_line_vector = np.array([new_points[1] - raw_points[0], new_points[1] - new_points[2]])
    # 添加第三维度
    r_line_vector = np.hstack((r_line_vector, np.zeros((2, 1))))
    n_line_vector = np.hstack((n_line_vector, np.zeros((2, 1))))

    # 构建 4x4 矩阵
    def build_matrix(vectors, origin):
        matrix = np.eye(4)
        # 使用两个向量的叉乘来确保正交
        z_axis = np.cross(vectors[0], vectors[1])
        z_axis = z_axis / np.linalg.norm(z_axis)  # 归一化
        y_axis = vectors[1] / np.linalg.norm(vectors[1])  # 归一化
        x_axis = np.cross(y_axis, z_axis)  # 确保正交
        matrix[0:3, 0] = x_axis
        matrix[0:3, 1] = y_axis
        matrix[0:3, 2] = z_axis
        matrix[0:3, 3] = origin
        return matrix

    raw_origin = raw_points[1]
    new_origin = new_points[1]

    raw_origin = np.append(raw_origin, 0)
    new_origin = np.append(new_origin, 0)

    raw_matrix = build_matrix(r_line_vector, raw_origin)
    new_matrix = build_matrix(n_line_vector, new_origin)

    # 计算变换矩阵
    transform_matrix = np.linalg.inv(raw_matrix) @ new_matrix
    return transform_matrix

def T_obj_2_base(ee_base,tcp_ee):
    t_obj_2_base = ee_base@tcp_ee
    return t_obj_2_base

def main():
    # 生成一张1920x1080的图像，颜色为白色
    width, height = 1920, 1080
    color = (255, 255, 255)  # 白色
    image = np.full((height, width, 3), color, dtype=np.uint8)

    # 通过crop_point前两个点画箭头
    draw_line(raw_crop_point[0],raw_crop_point[1],image)
    draw_line(crop_point[0],crop_point[1],image)

    # 展示图像
    cv2.imshow("image",image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 建立坐标系
    # r_line_vector = [[raw_crop_point[1]-raw_crop_point[0]],[raw_crop_point[2]-raw_crop_point[1]]]
    # n_line_vector = [[crop_point[1]-raw_crop_point[0]],[crop_point[2]-crop_point[1]]]

    table_transform = calculate_transform_2d(raw_crop_point,crop_point)

    print(table_transform)




if __name__ == "__main__":
    main()
    # cam = D435i()
    # 生成一张1920,1080的图

    pass
if __name__ == "__main__":
    pass