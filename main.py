import numpy as np
import cv2
import argparse as ap
import dlib
import get_points
import multiprocessing

source = 0

def run(source):
	bool_tracking = False
	points = []
	points_beta = []


	cap = cv2.VideoCapture(source)
	if not cap.isOpened():
		print "Video device or file couldn't be opened"
		exit()



	#cv2.namedWindow("Paused")
	while(True):
		# Capture frame-by-frame

		ret, frame = cap.read()
		if not ret:
			print "Unable to capture device"


		key = cv2.waitKey(100) & 0xFF
		if key == ord('q'):
			break

		if key == ord('p'):
			#print "press 'a' to add pedestrians"
			#print "press 'b' to add vehicles"




			while True:


				#if cv2.waitKey(1) & 0xFF == ord('a'):
				print "Adding vehicles"
				temp1=get_points.run(frame, multi=True)
				for x in temp1:
					points.append(x)

				#if cv2.waitKey(1) & 0xFF == ord('b'):
				print "Adding pedestrians"
				temp=get_points.run(frame, multi=True)
				for x in temp:
					points_beta.append(x)


				if points:
					tracker = [dlib.correlation_tracker() for _ in xrange(len(points))]
					# Provide the tracker the initial position of the object
					[tracker[i].start_track(frame, dlib.rectangle(*rect)) for i, rect in enumerate(points)]

				if points_beta:
					tracker_beta = [dlib.correlation_tracker() for _ in xrange(len(points_beta))]
					# Provide the tracker the initial position of the object
					[tracker_beta[i].start_track(frame, dlib.rectangle(*rect)) for i, rect in enumerate(points_beta)]

				print "press 'r' to see output "
				print "press 'q' to quit "


				if cv2.waitKey(-1) & 0xFF == ord('r'):
					break
				if cv2.waitKey(-1) & 0xFF == ord('q'):
					exit()

		if points or points_beta:


			if points:
				for i in xrange(len(tracker)):
					print "ALPHA"
					tracker[i].update(frame)
					# Get the position of th object, draw a
					# bounding box around it and display it.
					rect = tracker[i].get_position()
					pt1 = (int(rect.left()), int(rect.top()))
					pt2 = (int(rect.right()), int(rect.bottom()))
					cv2.rectangle(frame, pt1, pt2, (255, 255, 255), 1)
					#cv2.imshow("Image", frame)
					#print "Object {} tracked at [{}, {}] \r".format(i, pt1, pt2),

			if points_beta:
				for i in xrange(len(tracker_beta)):
					print "BETA"
					tracker_beta[i].update(frame)
					# Get the position of th object, draw a
					# bounding box around it and display it.
					rect = tracker_beta[i].get_position()
					pt1 = (int(rect.left()), int(rect.top()))
					pt2 = (int(rect.right()), int(rect.bottom()))
					cv2.rectangle(frame, pt1, pt2, (0, 0, 255), 1)
					#cv2.imshow("Image", frame)
					# print "Object {} tracked at [{}, {}] \r".format(i, pt1, pt2),

					#cv2.namedWindow("Image", cv2.WINDOW_NORMAL)


		cv2.imshow('frame', frame)
	# When everything done, release the capture
	cap.release()
	cv2.destroyAllWindows()


if __name__ == "__main__":
    # Parse command line arguments
	parser = ap.ArgumentParser()
	#group = parser.add_mutually_exclusive_group(required=True)
	parser.add_argument('-v', "--videoFile", help="Path to Video File")
	args = vars(parser.parse_args())

	if args["videoFile"]:
		source = args["videoFile"]

	run(source)


