import numpy as np
import cv2
import argparse as ap
import dlib
import get_points
import intersect
import xlwt


source=0

def get_fps(source, Videolength):
	cap = cv2.VideoCapture("docs/video/traffic2")
	frame_counter = 0
	print "Calculating Frames per second . . . "

	while (True):
		# Capture frame-by-frame

		ret, frame = cap.read()
		if not ret:
			break

		frame_counter += 1

	cap.release()
	cv2.destroyAllWindows()
	fps = float(frame_counter/Videolength)
	print "\nFPS is " +str(fps)+"\n"
	return fps


def check_intersection(array, new_pnt, last_point):

	counter = 0
	for first, second in zip(array, array[1:]):
		counter += 1
		if intersect.seg_intersect(first, second, new_pnt, last_point):
			return len(array) - counter



def run(source, mode=False, length=500):
	print length
	bool_tracking = False
	points_ped = []
	points_veh = []

	frame_var = 10

	coord_ped = []
	coord_veh = []

	if mode:
		noOfConflicts = -1
		wb = xlwt.Workbook()
		ws = wb.add_sheet("My Sheet")
		fps = get_fps(source, length)

	cap = cv2.VideoCapture(source)
	if not cap.isOpened():
		print "Video device or file couldn't be opened"
		exit()
	print " press 'p' to pause video and add objects to track \n press 'd' while the video plays to delete an object \n press 'q' to quit \n "
	while(True):
		# Capture frame-by-frame

		ret, frame = cap.read()
		if not ret:
			print "Unable to capture device"

		#Resize window
		#frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		frame = cv2.resize(frame, (480, 320))

		key = cv2.waitKey(50) & 0xFF

		if key == ord('d'):
			print " a to delete a pedestrian "
			print " b to delete a vehicle "
			print " q to continue with the detection "

			while True:
				input = raw_input(" \n Press appropriate key: ")

				if input == 'a':
					while True:
						input_a = int(raw_input(" Enter id of the pedestrian to delete , -1 to move to other :"))
						if input_a < 0:
							break
						elif input_a < len(points_ped):
							del points_ped[input_a]
							del tracker_ped[input_a]
							del coord_ped[input_a]
						else:
							print " Enter a valid id! "
						pass


				elif input == 'b':
					while True:
						input_b = int(raw_input(" Enter id of the vehicle to delete , -1 to move to other :"))
						if input_b < 0:
							break
						elif input_b < len(points_veh):
							del points_veh[input_b]
							del tracker_veh[input_b]
							del coord_veh[input_b]
						else:
							print " Enter a valid id! "
						pass



				elif input == 'q':
					break

				else:
					print "\n Choose a correct key !"


		if key == ord('q'):
			break

		if key == ord('p'):

			if points_ped:

				points_ped = []
				for i in xrange(len(tracker_ped)):

					rect = tracker_ped[i].get_position()
					points_ped.append((int(rect.left()),int(rect.top()),int(rect.right()),int(rect.bottom())))

			if points_veh:

				points_veh = []
				for i in xrange(len(tracker_veh)):
					rect = tracker_veh[i].get_position()
					points_veh.append((int(rect.left()),int(rect.top()),int(rect.right()),int(rect.bottom())))

			while True:

				print "\nAdd Pedestrians, if any\n"
				temp_ped=get_points.run(frame)
				for x in temp_ped:
					points_ped.append(x)


				#if cv2.waitKey(1) & 0xFF == ord('b'):
				print "\nAdd vehicles, if any\n"
				temp_veh=get_points.run(frame)
				for x in temp_veh:
					points_veh.append(x)


				if points_ped:
					tracker_ped = [dlib.correlation_tracker() for _ in xrange(len(points_ped))]
					# Provide the tracker the initial position of the object
					[tracker_ped[i].start_track(frame, dlib.rectangle(*rect)) for i, rect in enumerate(points_ped)]

				if points_veh:
					tracker_veh = [dlib.correlation_tracker() for _ in xrange(len(points_veh))]
					# Provide the tracker the initial position of the object
					[tracker_veh[i].start_track(frame, dlib.rectangle(*rect)) for i, rect in enumerate(points_veh)]

				print "press 'r' to see output "
				print "press 'q' to quit "


				if cv2.waitKey(-1) & 0xFF == ord('r'):
					break
				if cv2.waitKey(-1) & 0xFF == ord('q'):
					exit()

		if points_ped or points_veh:

			if points_ped:
				for i in xrange(len(tracker_ped)):

					tracker_ped[i].update(frame)
					# Get the position of th object, draw a
					# bounding box around it and display it.
					rect = tracker_ped[i].get_position()
					pt1 = (int(rect.left()), int(rect.top()))
					pt2 = (int(rect.right()), int(rect.bottom()))
					cv2.rectangle(frame, pt1, pt2, (255, 0, 0), 2)
					cv2.putText(frame, "ped"+str(i) , (int((pt1[0]+pt2[0])/2),int(pt1[1]+2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

					#Update coordinate
					if len(coord_ped)<(i+1):
						coord_ped.append(np.empty((0,2),np.uint32))

					coord_ped[i] = np.append(coord_ped[i],np.array([[(pt1[0]+pt2[0])/2,pt2[1]]]),axis = 0)
					#if len(coord[i])>10:
						#coord[i] = np.delete(coord[i], (0), axis=0)

					#print "i = "+str(i)+" and point list = "+str(coord[i])
					cv2.polylines(frame, [coord_ped[i]], False, (255, 0, 0),2)
					#print "Object {} tracked at [{}, {}] \r".format(i, pt1, pt2),

			if points_veh:
				for i in xrange(len(tracker_veh)):

					tracker_veh[i].update(frame)
					# Get the position of th object, draw a
					# bounding box around it and display it.
					rect = tracker_veh[i].get_position()
					pt1 = (int(rect.left()), int(rect.top()))
					pt2 = (int(rect.right()), int(rect.bottom()))
					cv2.rectangle(frame, pt1, pt2, (0, 0, 255), 2)
					cv2.putText(frame, "veh"+str(i), (int((pt1[0] + pt2[0]) / 2), int(pt1[1] - 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 1)

					if len(coord_veh) < (i + 1):
						coord_veh.append(np.empty((0, 2), np.uint32))

					#
					coord_veh[i] = np.append(coord_veh[i], np.array([[(pt1[0] + pt2[0]) / 2, pt2[1]]]), axis=0)
					#if len(coord_beta[i]) > 5:
						#coord_beta[i] = np.delete(coord_beta[i], (0), axis=0)

					# print "i = "+str(i)+" and point list = "+str(coord[i])
					cv2.polylines(frame, [coord_veh[i]], False, (0, 0, 255),2)

					#print "len of coord_beta[i] is "+str(len(coord_beta[i]))
					if len(coord_veh[i])>2:
						for x in coord_ped:

							if not check_intersection(x, coord_veh[i][-1], coord_veh[i][-2]) is None:
								print "Path conflict detected"
								noOfConflicts += 1

								required_value =  check_intersection(x, coord_veh[i][-1], coord_veh[i][-2])
								ws.write(noOfConflicts, 0, str(required_value*fps))

					# print "Object {} tracked at [{}, {}] \r".format(i, pt1, pt2)

		cv2.imshow('frame', frame)
	# When everything done, release the capture

	cap.release()
	cv2.destroyAllWindows()
	wb.save("myworkbook.xls")


if __name__ == "__main__":
    # Parse command line arguments
	parser = ap.ArgumentParser()
	#group = parser.add_mutually_exclusive_group(required=True)
	parser.add_argument('-v', "--videoFile", help="Path to Video File", type=str)
	parser.add_argument('-l', "--videoLen", help="Length of the video in seconds",type=float)
	parser.add_argument('-m', "--WriteMode", help="If yes, writes output to a excel file" ,type=bool)
	args = vars(parser.parse_args())

	if args["videoFile"]:
		source =(args["videoFile"])

	if args["videoLen"] and args["WriteMode"]==True:
		length = args["videoLen"]

		run(source, length)






