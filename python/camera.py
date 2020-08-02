import cv2
import time

capture=cv2.VideoCapture(1)
while True:
    ret, frame = capture.read()
    if ret:
        # cv2.imwrite('camera.jpg',frame)
        cv2.imshow('frame',frame)
        # cv2.waitKey(4000)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.imwrite('camera123.jpg',frame)
            break
capture.release()
cv2.destroyAllWindows()

# while True:
#     stime = time.time()
#     ret, frame = capture.read()
#     if ret:
#         cv2.imshow('frame', frame)
#         cv2.imwrite('test23.png',frame)
#         break
#     #     print('FPS {:.1f}'.format(1 / (time.time() - stime)))
#     # if cv2.waitKey(1) & 0xFF == ord('q'):
#     #     break

# capture.release()
# cv2.destroyAllWindows()