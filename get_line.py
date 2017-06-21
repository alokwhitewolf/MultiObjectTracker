# Import the required modules
import cv2
import numpy as np

trigger = 0

def run(im):
    im_disp = im.copy()
    window_name = "Draw line here."
    cv2.namedWindow(window_name,cv2.WINDOW_AUTOSIZE)

    print " Drag across the screen to set lines.\n Do it twice"
    print " After drawing the lines press 'q' to quit"

    l1 = np.empty((2, 2), np.uint32)
    l2 = np.empty((2, 2), np.uint32)

    list = [l1,l2]

    mouse_down = False



    def callback(event, x, y, flags, param):
        global trigger, mouse_down

        if trigger<2:
            if event == cv2.EVENT_LBUTTONDOWN:
                mouse_down = True
                list[trigger][0] = (x, y)

            if event == cv2.EVENT_LBUTTONUP and mouse_down:
                mouse_down = False
                list[trigger][1] = (x,y)
                cv2.line(im_disp, (list[trigger][0][0], list[trigger][0][1]),
                         (list[trigger][1][0], list[trigger][1][1]), (255, 0, 0), 2)

                trigger += 1
        else:
            pass




    cv2.setMouseCallback(window_name, callback)

    while True:
        cv2.imshow(window_name,im_disp)
        key = cv2.waitKey(10) & 0xFF

        if key == ord('q'):
            # Press key `q` to quit the program
            return list
            exit()

