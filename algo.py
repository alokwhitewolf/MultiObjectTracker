''' Sample script to test the logic of detection of path pf two objects
    This script when run, opens up a black window. Right clicking on it two provide points to draw a line in blue
    Left click to provide points for a red line.

    Whenever the blue line crosses the red , we get get flagged
'''



import cv2
import numpy as np
import itertools
import intersect

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

        if rpnts.size>2:
            check(lpnts, rpnts[-1], rpnts[-2])



#check if the new point crosses a line
def check(array, new_pnt, last_point):
        counter = 0
        for first, second in zip(array, array[1:]):
        #if line_value(first[0],first[1])*line_value(second[0],second[1]) <= 0:
         #   print"*"
            counter += 1
            if intersect.seg_intersect(first, second,new_pnt, last_point):
                print "-------"
                break


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

