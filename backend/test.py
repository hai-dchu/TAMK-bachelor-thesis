
import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("yolo11n-pose.pt")
test_img = cv2.imread('./test.jpg') # np.zeros((640, 480, 3), dtype=np.uint8)  # Empty black image
test_result = model(test_img)
if test_result:
    print("YOLO model loaded successfully!")
else:
    print("Warning: YOLO model failed to load!")

frame_count = 0
frame_rate = 4

keypoints = []

def process_frame(img):
    global frame_count
    global frame_rate
    global keypoints
    processed_img = cv2.flip(img, 1)
    feed = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)

    # check if ears and shoulders are in the frame
    is_left_ear_in = False
    is_right_ear_in = False
    is_left_shoulder_in = False
    is_right_shoulder_in = False
    is_left_elbow_in = False
    is_right_elbow_in = False
    frame_count += 1
    if frame_count % frame_rate == 0:
        frame_count = 0
        results = model(feed, verbose=False)
        keypoints = results[0].keypoints.xy.cpu().numpy() if results[0].keypoints else []


    for kp in keypoints:
        if len(kp):
            is_left_ear_in = not (kp[3][0] == 0 and kp[3][1] == 0)
            is_right_ear_in = not (kp[4][0] == 0 and kp[4][1] == 0)
            is_left_shoulder_in = not (kp[5][0] == 0 and kp[5][1] == 0)
            is_right_shoulder_in = not (kp[6][0] == 0 and kp[6][1] == 0)
            is_left_elbow_in = not (kp[7][0] == 0 and kp[7][1] == 0)
            is_right_elbow_in = not (kp[8][0] == 0 and kp[8][1] == 0)
        for idx in range(len(kp)):            
            if idx is not None or idx in [5,6,7,8,9,10]:
                x,y = kp[idx]
                processed_img = cv2.circle(processed_img, (int(x), int(y)), 5, (0, 255, 0), -1)


        if is_left_ear_in and is_left_shoulder_in:
            color = (0,0,255)
            x1, y1 = kp[3]
            x2, y2 = kp[5]
            upleft = (int(x2), int(y1-100))
            downright = (int(x2+100), int(y1))
            if is_left_elbow_in:
                x_elbow, y_elbow = kp[7]
                if upleft[0] < x_elbow < downright[0] and upleft[1] < y_elbow < downright[1]: # elbow inside square
                    color = (0,255,0)
            processed_img = cv2.rectangle(processed_img, upleft, downright, color, 2)


        if is_right_ear_in and is_right_shoulder_in:
            color = (0,0,255)
            x1, y1 = kp[4]
            x2, y2 = kp[6]
            upleft = (int(x2-100), int(y1-100))
            downright = (int(x2), int(y1))
            if is_right_elbow_in:
                x_elbow, y_elbow = kp[8]
                if upleft[0] < x_elbow < downright[0] and upleft[1] < y_elbow < downright[1]: # elbow inside square
                    color = (0,255,0)
            processed_img = cv2.rectangle(processed_img, upleft, downright, color, 2)
    return processed_img

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if ret:
        cv2.imshow("test", process_frame(frame))
        if cv2.waitKey(1) == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()