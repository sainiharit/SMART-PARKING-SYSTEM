import yaml
import numpy as np
import cv2
import time


import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Fetch the service account key JSON file contents
cred = credentials.Certificate('/home/vishnoitanuj/Downloads/service-account-file.json')
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://new-agent-twlwex.firebaseio.com/'
})
ref = db.reference('/slots')

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

parking_status = [False]*len(parking_data)
parking_buffer = [None]*len(parking_data)

 ## Parking Configuration
config = {
    'park_sec_to_wait' : 1,
    'min_area_motion_contour' : 60,
    'save_video':False,
}
## Camera Detection
cap=cv2.VideoCapture(1)
video_cur_frame = 0.0

video_info = {'fps':    cap.get(cv2.CAP_PROP_FPS),
              'width':  int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
              'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
              'fourcc': cap.get(cv2.CAP_PROP_FOURCC),
              'num_of_frames': int(cap.get(cv2.CAP_PROP_FPS))}

print(video_info['num_of_frames'])

if config['save_video']:
    fourcc = cv2.VideoWriter_fourcc('D','I','V','X')# options: ('P','I','M','1'), ('D','I','V','X'), ('M','J','P','G'), ('X','V','I','D')
    out = cv2.VideoWriter(fn_out, -1, 25.0, #video_info['fps'], 
                          (video_info['width'], video_info['height']))
dict1 = {
    '0': {
        'occupied': 1,
    },
    '1': {
        'occupied': 1,
    },
    '2':{
        'occupied': 1,
    },
    '3': {
        'occupied': 1,
    },
    '4': {
        'occupied': 1,
    },
    '5': {
        'occupied': 1,
    },
}
ref.update(dict1)
stime=time.time()

while True:
    spot = 0
    occupied = 0
    video_cur_pos = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0 # Current position of the video file in seconds
    
    ret,frame=cap.read()

    if ret == False:
        print("Capture Error")
        break
    video_cur_frame = video_cur_frame + 1.0
    frame_blur = cv2.GaussianBlur(frame.copy(), (5,5),3)
    frame_gray = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2GRAY)
    frame_out = frame.copy()

    for ind, park in enumerate(parking_data):
        points = np.array(park['points'])
        rect = parking_bounding_rects[ind]
        roi_gray = frame_gray[rect[1]:(rect[1]+rect[3]),rect[0]:(rect[0]+rect[2])]
        # print(rect,'\n')


        points[:,0] = points[:,0] - rect[0]  # shift contour to roi
        points[:,1] = points[:,1] - rect[1]
        # print(time.time()-stime)
        status = np.std(roi_gray) < 22 and np.mean(roi_gray) > 53
        # If detected a change in parking status, save the current time
        if status != parking_status[ind] and parking_buffer[ind]==None:
            parking_buffer[ind] = video_cur_pos
            
        elif status != parking_status[ind] and parking_buffer[ind]!=None:
            if video_cur_pos - parking_buffer[ind] > config['park_sec_to_wait']:
                parking_status[ind] = status
                parking_buffer[ind] = None
                
                if time.time()-stime > 3:
                    print("parking status changed")
                    print(park['id'])
                    flag=str(park['id'])
                    # dict1[flag]['user']=dict1[flag]['user']
                    ref2 = ref.child(flag)
                    if(dict1[flag]['occupied']==0):
                        ref2.update({
                            'occupied':1
                        })
                        dict1[flag]['occupied']=1
                    else:
                        ref2.update({
                            'occupied':0
                        })
                        dict1[flag]['occupied']=0
                    # ref.update(dict1)
        
        # If status is still same and counter is open
        elif status == parking_status[ind] and parking_buffer[ind]!=None:
            parking_buffer[ind] = None
        
        # Parking Overlay
        points = np.array(park['points'])
        if parking_status[ind]:
            color = (0,255,0)
            spot = spot + 1
        else:
            color = (0,0,255)
            occupied = occupied+1
            # print(ind,parking_status[ind])
        
        cv2.drawContours(frame_out, [points], contourIdx=-1,
                        color=color, thickness=2, lineType=cv2.LINE_8)
        moments = cv2.moments(points)
        centroid = (int(moments['m10']/moments['m00'])-3, int(moments['m01']/moments['m00'])+3)
        cv2.putText(frame_out, str(park['id']), (centroid[0]+1, centroid[1]+1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1, cv2.LINE_AA)
        cv2.putText(frame_out, str(park['id']), (centroid[0]-1, centroid[1]-1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1, cv2.LINE_AA)
        cv2.putText(frame_out, str(park['id']), (centroid[0]+1, centroid[1]-1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1, cv2.LINE_AA)
        cv2.putText(frame_out, str(park['id']), (centroid[0]-1, centroid[1]+1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1, cv2.LINE_AA)
        cv2.putText(frame_out, str(park['id']), centroid, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1, cv2.LINE_AA)
        # print('occupied: ', occupied)
        # print('spot: ', spot)

        cv2.rectangle(frame_out, (1, 5), (280, 90),(255,255,255), 85) 
        str_on_frame = "Frames: %d/%d" % (video_cur_frame, video_info['num_of_frames'])
        cv2.putText(frame_out, str_on_frame, (5,30), cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
                    0.7, (0,128,255), 2, cv2.LINE_AA)
        str_on_frame = "Spot: %d Occupied: %d" % (spot, occupied)
        cv2.putText(frame_out, str_on_frame, (5,90), cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
                            0.7, (0,128,255), 2, cv2.LINE_AA)
        # write the output frame
    if config['save_video']:
        if video_cur_frame % 35 == 0: # take every 30 frames
            out.write(frame_out)
    
    # Display Video
    cv2.imshow('Parking',frame_out)
    cv2.waitKey(40)
    k = cv2.waitKey(1)
    if k == ord('q'):
        break

cap.release()
if config['save_video']: out.release()
cv2.destroyAllWindows()
