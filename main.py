import numpy as np
import cv2
import argparse as ap
import dlib
import get_points
import get_line
import intersect
import xlwt



source=0

#Function to calculate the frames per second of the video.
# We do it manually by calculating Total_no_of_frames/Total_run_time
#Run_time of the video is a prerequisite
#Fps calculation is note needed when mode = False in run()

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
	#print "Total frames = "+str(frame_counter)
	return fps

#Algorithm to check intersection of line segments
#It checks iteratively intersection between a pair of points(Last location of the vehicle) and pairs of points of another List(Pedestrian path)
def check_intersection(array, new_pnt, last_point):

	intersect_counter = 0
	for first, second in zip(array, array[1:]):
		intersect_counter += 1
		if intersect.seg_intersect(first, second, new_pnt, last_point):
			return len(array) - intersect_counter


#When mode = True, the Post Encroachment Time is stored in excel sheet.
#When mode is false, only conflict times are detected and no data is stored.
#when mode is false, length parameter is irrelevant

def run(source, mode=False, length=500):

	if mode:
		print "runtime of the video in seconds is - "+str(length)+" seconds"

	#list of touples containing coordinates of the rectangle
	#bounding the object of interest

	points_ped = []
	points_veh = []

	# Variable so that the trajectories are  dynamically increased and decreased. Trajectory length is constant
	frame_var_ped = 100
	frame_var_veh = 100

	#Store trajectory coordinates
	coord_ped = []
	coord_veh = []


	#If first frame or not
	first_frame = True

	#Store the distance between reference lines


	# list of pedestrian id's whose path vehicle has encroached
	collided_objects = []



	if mode:
		distance = 100

		noOfConflicts = -1
		wb = xlwt.Workbook()
		ws = wb.add_sheet("My Sheet")
		fps = get_fps(source, length)

		ws.write(0, 0, "PET")
		ws.write(0, 1, "Sex")
		ws.write(0,2,"Speed")
		### <-- Lists to be stored with respect to vehicle --> ###


		#list to keep velocities of the vehicles
		velocity = []

		#bool to see if it's between the two reference lines
		vehicle_vel_bool = []

		#counter of frames which the vehicle spends between the reference lines
		vehicle_frame_counter = []

		#at which noOfConflict the vehicle has conflicts so that speed can be put
		#in the database
		which_conflict = []

		##Which assigned line the vehicle crosses first
		which_intersect = []

		###<--- Lists to be stored with respect to pedestrian -->###
		#Store sex of the pedestrian
		pedestrian_sex = []

	cap = cv2.VideoCapture(source)
	if not cap.isOpened():
		print "Video device or file couldn't be opened"
		exit()

	while(True):
		# Capture frame-by-frame

		ret, frame = cap.read()
		if not ret:
			print "Unable to capture device"

		#Resize window
		frame = cv2.resize(frame, (500, 350))

		#Make frame size fixed
		cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)

		#############################
		#If first frame, add two reference lines
		#Whose real tine distance is known
		###########################

		if first_frame:
			if mode:
				cv2.imshow('frame', frame)
				points = get_line.run(frame)

				l1 = np.empty((2, 2), np.int32)
				l1[0] = (points[0][0][0], points[0][0][1])
				l1[1] = (points[0][1][0], points[0][1][1])

				l2 = np.empty((2, 2), np.int32)
				l2[0] = (points[1][0][0], points[1][0][1])
				l2[1] = (points[1][1][0], points[1][1][1])

				lines = [l1, l2]

				print " press 'p' to pause video and add objects to track \n "
				print " press 'd' while the video plays to delete an object \n "
				print " press 'q' to quit \n "

				cv2.destroyWindow("Draw line here.")
			first_frame = False

		##############################################################################################################################
		#Delete pedestrians and vehicles that go to extremes of frame automatically
		##############################################################################################################################



		if points_ped or points_veh:
			key = cv2.waitKey(1) & 0xFF
		else:
			key = cv2.waitKey(70) & 0xFF

		#To delete already selected objects
		if key == ord('d'):
			print " a to delete a pedestrian "
			print " b to delete a vehicle "
			print " q to continue with the detection "

			while True:
				input = raw_input(" \n Press appropriate key: ")

				if input == 'a':
					input_a = -2

					while True:
						input_a = int(raw_input(" Enter id(on the terminal)  of the pedestrian to delete , -1 to move to other :"))
						if input_a == -1:
							break
						elif input_a < len(points_ped):
							if mode:
								del pedestrian_sex[input_a]
							del points_ped[input_a]
							del tracker_ped[input_a]
							del coord_ped[input_a]
						else:
							print " Enter a valid id! "
						pass


				elif input == 'b':
					while True:
						input_b = int(raw_input(" Enter id(on the terminal)  of the vehicle to delete , -1 to move to other :"))
						if input_b < 0:
							break
						elif input_b < len(points_veh):
							if mode:
								for x in which_conflict[input_b]:
									ws.write(x, 2, velocity[input_b])

								del velocity[input_b]
								del vehicle_vel_bool[input_b]
								del vehicle_frame_counter[input_b]
								del which_conflict[input_b]
								del which_intersect[input_b]



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

		#Pause to add objects to track
		if key == ord('p'):

			#Update the list of coordinates
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

				#Add Pedestrians to track
				print "\nAdd Pedestrians, if any\n"
				if mode:
					temp_ped, temp_sex = get_points.run(frame,mode,for_pedestrian=True)
					for x in temp_ped:
						points_ped.append(x)
					for y in temp_sex:
						pedestrian_sex.append(y)
					print pedestrian_sex


				else:
					temp_ped = get_points.run(frame, mode, for_pedestrian=True)
					for x in temp_ped:
						points_ped.append(x)

				#Add vehicles to track
				print "\nAdd vehicles, if any\n"
				temp_veh=get_points.run(frame,mode,for_pedestrian=False)

				'''Can be made more efficient '''
				for x in temp_veh:
					points_veh.append(x)
					collided_objects.append([])
					if mode:
						velocity.append(0)
						vehicle_vel_bool.append(0)
						vehicle_frame_counter.append(0)
						which_conflict.append([])
						which_intersect.append([-1])






				if points_ped:
					#initiate tracker
					tracker_ped = [dlib.correlation_tracker() for _ in xrange(len(points_ped))]
					# Provide the tracker the initial position of the object
					[tracker_ped[i].start_track(frame, dlib.rectangle(*rect)) for i, rect in enumerate(points_ped)]

				if points_veh:
					#initiate tracker
					tracker_veh = [dlib.correlation_tracker() for _ in xrange(len(points_veh))]
					# Provide the tracker the initial position of the object
					[tracker_veh[i].start_track(frame, dlib.rectangle(*rect)) for i, rect in enumerate(points_veh)]

				print "press 'r' to see output "
				print "press 'q' to quit "


				if cv2.waitKey(-1) & 0xFF == ord('r'):
					cv2.destroyWindow("Select objects to be tracked here.")
					cv2.destroyWindow("Objects to be tracked.")
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

					# Add trajectory of new objects
					if len(coord_ped)<(i+1):
						coord_ped.append(np.empty((0,2),np.uint32))

					#update trajectory
					coord_ped[i] = np.append(coord_ped[i],np.array([[(pt1[0]+pt2[0])/2,pt2[1]]]),axis = 0)
					#Keep the length of trajectory constant
					if len(coord_ped[i])>frame_var_ped:
						coord_ped[i] = np.delete(coord_ped[i], (0), axis=0)

					#draw trajectory
					cv2.polylines(frame, [coord_ped[i]], False, (255, 0, 0),2)


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

					# Add trajectory of new objects
					if len(coord_veh) < (i + 1):
						coord_veh.append(np.empty((0, 2), np.uint32))

					##update trajectory
					coord_veh[i] = np.append(coord_veh[i], np.array([[(pt1[0] + pt2[0]) / 2, pt2[1]]]), axis=0)
					if len(coord_veh[i]) > frame_var_veh:
						coord_veh[i] = np.delete(coord_veh[i], (0), axis=0)

					# draw trajectory
					cv2.polylines(frame, [coord_veh[i]], False, (0, 0, 255),2)
###########################################################################################################
					##Condition for finding velocity

					if mode:
						if len(coord_veh[i])>2:
							if vehicle_vel_bool[i] == 0:


								if not check_intersection(l1, coord_veh[i][-1], coord_veh[i][-2]) is None:
									which_intersect[i][0] = 0
									vehicle_vel_bool[i] = 1

								if not check_intersection(l2, coord_veh[i][-1], coord_veh[i][-2]) is None:
									which_intersect[i][0] = 1
									vehicle_vel_bool[i] = 1
									print "Second Line"

							elif vehicle_vel_bool[i] == 1:

								vehicle_frame_counter[i] += 1
								print vehicle_frame_counter[i]
								if not check_intersection(lines[(which_intersect[i][0] + 1) % 2], coord_veh[i][-1], coord_veh[i][-2]) is None:
									vehicle_vel_bool[i] = 3
									velocity[i] = (distance*fps)/vehicle_frame_counter[i]

################################################################################################################
					##Check for conflict
					if len(coord_veh[i])>2:
						for x in coord_ped:
							index = 0

							#See if already conflict occured
							if not index in collided_objects[i]:

								#Check for conflict
								if not check_intersection(x, coord_veh[i][-1], coord_veh[i][-2]) is None:
									print "Path conflict detected"

									#update collidion in collided_objects
									collided_objects[i].append(index)
									if mode:
										#Also keep a track record
										noOfConflicts += 1

										#Store the no of conflict to later put velocity in databe
										#while deleting the vehicle
										which_conflict[i].append(noOfConflicts+1)

										#Find how many frames, behind the conflict occurs
										required_value =  check_intersection(x, coord_veh[i][-1], coord_veh[i][-2])
										ws.write(noOfConflicts+1, 0, str(required_value/fps))
										ws.write(noOfConflicts+1, 1, str(pedestrian_sex[index]))


								index+=1


		if mode:
			cv2.polylines(frame, np.int32([l1]), False, (255, 0, 0))
			cv2.polylines(frame, np.int32([l2]), False, (0, 255, 0))


		cv2.imshow('frame', frame)
	# When everything done, release the capture

	cap.release()


	if mode:
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

	if args["videoLen"]:
		length = args["videoLen"]

		run(source, True, length)

	else:
		run(source)