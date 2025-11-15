import numpy as np
from ultralytics import YOLO
import os
import cv2
import uuid
from django.conf import settings


model_path = os.path.join(os.path.dirname(__file__), 'best.pt')
model = YOLO(model_path)

# def crop_detected_objects(image_path, output_folder):
#     results = model(image_path)[0]
#     orig = cv2.imread(image_path)

#     # 確保指定資料夾存在
#     os.makedirs(output_folder, exist_ok=True)

#     cropped_paths = []

#     for i, box in enumerate(results.boxes):
#         x1, y1, x2, y2 = map(int, box.xyxy[0])
#         cls_id = int(box.cls[0])
#         label = results.names[cls_id]

#         cropped = orig[y1:y2, x1:x2]

#         if cropped.shape[0] == 0 or cropped.shape[1] == 0:
#             continue

#         filename = f"{label}_{uuid.uuid4().hex[:8]}.jpg"
#         save_path = os.path.join(output_folder, filename)
#         cv2.imwrite(save_path, cropped)

#         # 這裡只回傳檔名，或讓 view 決定完整相對路徑
#         cropped_paths.append(filename)

#     return cropped_paths


def correct_full_image_perspective(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return img

    largest = max(contours, key=cv2.contourArea)
    rect = cv2.minAreaRect(largest)
    box = cv2.boxPoints(rect).astype(int)

    # 依照 minAreaRect 取 w,h
    w = int(rect[1][0])
    h = int(rect[1][1])
    if w == 0 or h == 0:
        return img

    # 對應原圖座標
    src_pts = np.float32(box)

    # 定義矯正後的區域座標
    dst_pts = np.float32([
        [0, 0],
        [w - 1, 0],
        [w - 1, h - 1],
        [0, h - 1]
    ])

    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    corrected = cv2.warpPerspective(img, M, (w, h))

    return corrected

def crop_detected_objects(image_path, output_folder):
    orig = cv2.imread(image_path)

    # 這裡改為整張圖矯正（關鍵）
    corrected = correct_full_image_perspective(orig)

    # 用矯正後的影像做 YOLO 偵測（非常重要）
    results = model(corrected)[0]

    os.makedirs(output_folder, exist_ok=True)
    cropped_paths = []

    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0])
        label = results.names[cls_id]

        cropped = corrected[y1:y2, x1:x2]
        if cropped.size == 0:
            continue

        filename = f"{label}_{uuid.uuid4().hex[:8]}.jpg"
        save_path = os.path.join(output_folder, filename)
        cv2.imwrite(save_path, cropped)

        cropped_paths.append(filename)

    return cropped_paths
