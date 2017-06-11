import cv2
import numpy as np

left_click = np.empty((0,2), np.uint32)
left_click_bool = False
right_click = np.empty((0,2), np.uint32)

lpnts = np.empty((0,2), np.uint32)
rpnts = np.empty((0,2), np.uint32)
# mouse callback function
def get_points(event,x,y,flags,param):
    global lpnts,rpnts

    if event == cv2.EVENT_LBUTTONDOWN:
        lpnts = np.append(lpnts, np.array([[x, y]]), axis=0)
        cv2.polylines(img, [lpnts], False, (0, 0, 255))

    if event == cv2.EVENT_RBUTTONDOWN:
        rpnts = np.append(rpnts, np.array([[x, y]]), axis=0)
        cv2.polylines(img, [rpnts], False, (255, 0, 0))



'''
    elif event == cv2.EVENT_RBUTTONDOWN:
        if drawing == True:
            if mode == True:
                cv2.rectangle(img,(ix,iy),(x,y),(0,255,0),-1)
            else:
                cv2.circle(img,(x,y),5,(0,0,255),-1)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if mode == True:
            cv2.rectangle(img,(ix,iy),(x,y),(0,255,0),-1)
        else:
            cv2.circle(img,(x,y),5,(0,0,255),-1)
'''
img = np.zeros((512,512,3), np.uint8)
cv2.namedWindow('image')
cv2.setMouseCallback('image',get_points)

while(1):
    cv2.imshow('image',img)
    k = cv2.waitKey(1) & 0xFF
    if k == ord('m'):
        mode = not mode
    elif k == 27:
        break

