''' Sample script to test the logic of finding the velocity of a moving object between two lines if frame rate is known
    This script when run, opens up a black window.Two lines are visible, one green other blue

    left clicking on the screen gives points for a polyline of red color. This script checks for how many frames/clicks
    the red polyline spent between intersecting our two lines
'''

import cv2
import numpy as np
import intersect
import get_line

left_click = np.empty((0, 2), np.int32)

lpnts = np.empty((0, 2), np.int32)

which_intersect = 0
mode = 0
counter = 0

img = np.zeros((512, 512, 3), np.uint8)



def get_points(event, x, y, flags, param):
    global lpnts, mode, counter, which_intersect

    if event == cv2.EVENT_LBUTTONDOWN:
        lpnts = np.append(lpnts, np.array([[x, y]]), axis=0)
        cv2.polylines(img, [lpnts], False, (0, 0, 255))
        if lpnts.size > 2:
            if mode == 0:

                #check(l1, lpnts[-1], lpnts[-2])
                if check(l1, lpnts[-1], lpnts[-2]):
                    which_intersect = 0
                    mode = 1
                #check(l2, lpnts[-1], lpnts[-2])
                if check(l2, lpnts[-1], lpnts[-2]):
                    which_intersect = 1
                    mode = 1

            elif mode == 1:

                counter += 1
                if check(lines[(which_intersect + 1) % 2], lpnts[-1], lpnts[-2]):
                    mode = 3
                    print counter


# check if the new point crosses a line
def check(array, new_pnt, last_point):
    for first, second in zip(array, array[1:]):

        if intersect.seg_intersect(first, second, new_pnt, last_point):
            return True


points = get_line.run(img)

l1 = np.empty((2, 2), np.int32)
l1[0] = (points[0][0][0], points[0][0][1])
l1[1] = (points[0][1][0], points[0][1][1])

l2 = np.empty((2, 2), np.int32)
l2[0] = (points[1][0][0], points[1][0][1])
l2[1] = (points[1][1][0], points[1][1][1])

# print l2
lines = [l1, l2]
# print lines
cv2.destroyWindow("Draw line here.")

cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback('image', get_points)

cv2.polylines(img, np.int32([l1]), False, (255, 0, 0))
cv2.polylines(img, np.int32([l2]), False, (0, 255, 0))

while (1):
    cv2.imshow('image', img)
    k = cv2.waitKey(2000) & 0xFF


    if k == 27:
        break
    cv2.moveWindow('image', 1000, 0)

cv2.destroyAllWindows()

