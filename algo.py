import cv2
import numpy as np
import itertools

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
        print "l--"+str(lpnts)+"---size-"+str(lpnts[ (lpnts.size/2)-1 ][0])

        for first, second in zip(lpnts, lpnts[1:]):

            print first, second


    if event == cv2.EVENT_RBUTTONDOWN:
        rpnts = np.append(rpnts, np.array([[x, y]]), axis=0)
        cv2.polylines(img, [rpnts], False, (255, 0, 0))


#check if the new point crosses a line
def check(array, new_pnt, last_point):

    a_x1 = new_pnt[0]
    a_y1 = new_pnt[1]

    a_x2 = last_point[0]
    a_y2 = last_point[1]

    def line_value(bx1, by1):
        #if not (bx1-a_x1)*(a_y2-a_y1)==0:
        return ((by1 - a_y1)*(a_x2-a_x1))/((bx1-a_x1)*(a_y2-a_y1))


    for first, second in zip(array, array[1:]):
        if line_value(first[0],first[1])*line_value(second[0],second[1]) <= 0:
            print"*"



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

