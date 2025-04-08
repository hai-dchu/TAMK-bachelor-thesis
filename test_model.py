import cv2
import numpy as np
from ultralytics import YOLO

import time

model = YOLO('yolo11n-pose.pt')

test_img = np.zeros((640, 480, 3), dtype=np.uint8)  # Empty black image
test_result = model(test_img)
if test_result:
    print("YOLO model loaded successfully!")
else:
    print("Warning: YOLO model failed to load!")


cap = cv2.VideoCapture(0)


dif = []

while True:
    ret, frame = cap.read()


    if ret:
        start = time.time_ns() // 1000000
        results = model(frame)
        keypoints = results[0].keypoints.xy.cpu().numpy() if results[0].keypoints else []
        for kp in keypoints:
            for x, y in kp:
                cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 0), -1)
        dif.append(time.time_ns() // 1000000 - start)

        cv2.imshow("frame", frame)
    
    if cv2.waitKey(1) == ord('q') or len(dif) == 200:
        break

import matplotlib.pyplot as plt

plt.plot(np.array(dif))
plt.show()
    