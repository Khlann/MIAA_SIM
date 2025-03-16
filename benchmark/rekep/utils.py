import cv2
def project_keypoints_to_img(keypoints_2d,color_image):
    for keypoint_count, keypoint in enumerate(keypoints_2d):
        displayed_text = f"{keypoint_count+1}"
        text_length = len(displayed_text)
        box_width = 30 + 10 * (text_length-1)
        box_height = 30
        cv2.rectangle(color_image, (keypoint[1] - box_width // 2, keypoint[0] - box_height // 2), (keypoint[1] + box_width // 2, keypoint[0] + box_height // 2), (255, 255, 255), -1)
        cv2.rectangle(color_image, (keypoint[1] - box_width // 2, keypoint[0] - box_height // 2), (keypoint[1] + box_width // 2, keypoint[0] + box_height // 2), (0, 0, 0), 2)
        org = (keypoint[1] - 7 * (text_length), keypoint[0] + 7)
        color = (255, 0, 0)
        cv2.putText(color_image, str(keypoint_count), org, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.imwrite('keypoints.png', color_image)