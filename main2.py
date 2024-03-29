from ultralytics import YOLO
import cv2
import numpy as np
from sort import *
from util import get_car, read_license_plate, write_csv

results = {}
license_plate_texts = set()

mot_tracker = Sort()

# load models
coco_model = YOLO('yolov8n.pt')
license_plate_detector = YOLO('license_plate_detector.pt')

# load video
cap = cv2.VideoCapture('sample.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)
desired_fps = 1
desired_frame_rate = int(fps / desired_fps)

vehicles = [2, 3, 5, 7]

# Get total number of frames in the video
frame_nmr = -1
while cap.isOpened():
    frame_nmr += 1
    ret, frame = cap.read()
    if not ret:
        break  # Break the loop if there are no more frames to read
    if frame_nmr % desired_frame_rate != 0:
        continue
    results[frame_nmr] = {}
    # detect vehicles
    detections = coco_model(frame)[0]
    detections_ = []
    for detection in detections.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = detection
        if int(class_id) in vehicles:
            detections_.append([x1, y1, x2, y2, score])

    # track vehicles
    track_ids = mot_tracker.update(np.asarray(detections_))
    adjusted_frame_nmr = len(results) + 1
    results[adjusted_frame_nmr] = {}

    # detect license plates
    license_plates = license_plate_detector(frame)[0]
    for license_plate in license_plates.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = license_plate

        # assign license plate to car
        xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)

        if car_id != -1:

            # crop license plate
            license_plate_crop = frame[int(y1):int(y2), int(x1): int(x2), :]

            # process license plate
            license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
            _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)

            # read license plate number
            license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)



            if license_plate_text is not None:
                if license_plate_text not in license_plate_texts:
                    license_plate_texts.add(license_plate_text)
                    results[adjusted_frame_nmr][car_id] = {'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},
                                                  'license_plate': {'bbox': [x1, y1, x2, y2],
                                                                    'text': license_plate_text,
                                                                    'bbox_score': score,
                                                                    'text_score': license_plate_text_score
                                                                    }
                                                  }
                    write_csv(results, 'test.csv')
                    print("the average license_plate texts are: {}".format(license_plate_texts))
                else:
                    print("Duplicate license_plate_text found: {}".format(license_plate_text))


    if cv2.waitKey(1) == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()

print("the license_plate texts are: {}".format(license_plate_texts))
