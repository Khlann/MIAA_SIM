import cv2

# 创建指定类型的ArUco字典，这里以4x4大小，50个标记的字典为例，你也可以选择其他类型
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL) 

# 指定要生成的ArUco标记的id 
marker_id = 998
# 设置生成的ArUco标记图像的尺寸（单位：像素）
size_of_marker = 400 

# 生成ArUco标记图像
img = cv2.aruco.generateImageMarker(dictionary, marker_id, size_of_marker) 

# 保存生成的ArUco标记图像
cv2.imwrite(f"marker_image_{marker_id}.png", img) 

# 显示生成的ArUco标记图像（可选操作）
cv2.imshow("marker", img) 
cv2.waitKey(0) 
cv2.destroyAllWindows() 