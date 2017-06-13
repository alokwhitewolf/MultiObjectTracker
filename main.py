import numpy as np
import cv2
import argparse as ap
import dlib
import get_points

source = 0

def run(source):
	bool_tracking = False
	points = []
	points_beta = []

	frame_var = 10

	coord = []
	Empty = np.empty((0,2), np.uint32)

	cap = cv2.VideoCapture(source)
	if not cap.isOpened():
		print "Video device or file couldn't be opened"
		exit()

	while(True):
		# Capture frame-by-frame

		ret, frame = cap.read()
		if not ret:
			print "Unable to capture device"


		key = cv2.waitKey(100) & 0xFF
		if key == ord('q'):
			break

		if key == ord('p'):

			if points:

				points = []
				for i in xrange(len(tracker)):

					rect = tracker[i].get_position()
					points.append((int(rect.left()),int(rect.top()),int(rect.right()),int(rect.bottom())))

			if points_beta:

				points = []
				for i in xrange(len(tracker_beta)):
					rect = tracker_beta.get_position()
					points_beta.append((int(rect.left()),int(rect.top()),int(rect.right()),int(rect.bottom())))

			while True:

				print "Adding vehicles"
				temp1=get_points.run(frame)
				for x in temp1:
					points.append(x)


				#if cv2.waitKey(1) & 0xFF == ord('b'):
				print "Adding pedestrians"
				temp=get_points.run(frame)
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

					tracker[i].update(frame)
					# Get the position of th object, draw a
					# bounding box around it and display it.
					rect = tracker[i].get_position()
					pt1 = (int(rect.left()), int(rect.top()))
					pt2 = (int(rect.right()), int(rect.bottom()))
					cv2.rectangle(frame, pt1, pt2, (255, 0, 0), 1)
					cv2.putText(frame, str(i) , (int((pt1[0]+pt2[0])/2),int(pt1[1]+2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

					#Update coordinate
					if len(coord)<(i+1):
						coord.append(np.empty((0,2),np.uint32))
					 #
					coord[i] = np.append(coord[i],np.array([[(pt1[0]+pt2[0])/2,pt2[1]]]),axis = 0)
					#print "i = "+str(i)+" and point list = "+str(coord[i])
					cv2.polylines(frame, [coord[i]], False, (0, 0, 255))
					#print "Object {} tracked at [{}, {}] \r".format(i, pt1, pt2),

			if points_beta:
				for i in xrange(len(tracker_beta)):

					tracker_beta[i].update(frame)
					# Get the position of th object, draw a
					# bounding box around it and display it.
					rect = tracker_beta[i].get_position()
					pt1 = (int(rect.left()), int(rect.top()))
					pt2 = (int(rect.right()), int(rect.bottom()))
					cv2.rectangle(frame, pt1, pt2, (0, 0, 255), 1)
					cv2.putText(frame, str(i), (int((pt1[0] + pt2[0]) / 2), int(pt1[1] - 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 1)


					# print "Object {} tracked at [{}, {}] \r".format(i, pt1, pt2),
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


