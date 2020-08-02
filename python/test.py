import yaml
import numpy as np
import cv2
import time

fn_yaml = "../datasets/new.yml"
fn_out = "../datasets/output.avi"


## Parking Stream
with open(fn_yaml, 'r') as stream:
    parking_data = yaml.load(stream)
parking_contours = []
parking_bounding_rects = []
parking_mask = []
for park in parking_data:
    points = np.array(park['points'])
    # print(points)
    rect = cv2.boundingRect(points)
    points_shifted = points.copy()
    points_shifted[:,0] = points[:,0] - rect[0] # shift contour to roi
    points_shifted[:,1] = points[:,1] - rect[1]
    parking_contours.append(points)
    parking_bounding_rects.append(rect)
    mask = cv2.drawContours(np.zeros((rect[3], rect[2]), dtype=np.uint8), [points_shifted], contourIdx=-1,
                            color=255, thickness=-1, lineType=cv2.LINE_8)
    mask = mask==255
    parking_mask.append(mask)
    # print(park['points'])

parking_status = [False]*len(parking_data)
parking_buffer = [None]*len(parking_data)

for ind, park in enumerate(parking_data):
    points = np.array(park['points'])
    rect = parking_bounding_rects[ind]
    # roi_gray = frame_gray[rect[1]:(rect[1]+rect[3]),rect[0]:(rect[0]+rect[2])]
    # print(rect,'\n')


    # print(park['points']) # shift contour to roi
    # points[:,1] = points[:,1] - rect[1]
new_pts = cv2.boundingRect(np.array(parking_data[0]['points']))
print(new_pts)