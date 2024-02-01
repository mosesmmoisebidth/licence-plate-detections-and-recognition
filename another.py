import numpy as np
import cv2 as cv
video_file = "behinds.mp4";

cap = cv.VideoCapture(video_file)
frame_nmr = -1
while cap.isOpened():
    ret, frame = cap.read()
    frame_nmr += 1
    if not ret:
        break
    frame = cv.resize(frame, (900, 900))
    cv.imshow("frame", frame)
    if cv.waitKey(1) == ord('q'):
        break
cv.destroyAllWindows()
print("the frame_number is: {}".format(frame_nmr))