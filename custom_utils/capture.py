import os
import cv2
import uuid


def capture_character(frame, x1, y1, x2, y2, foldername, filename):
    # base_path = "../characters"
    base_path = os.path.join('../characters', foldername)
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    roi = frame[y1:y2, x1:x2]
    path = os.path.join(base_path, filename)
    cv2.imwrite(path, roi)
