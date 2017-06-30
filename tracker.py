'''
############################################################
 Alok Kumar Bishoyi
 Indian Institute of Technology, Bombay

This code is a hack on dlib module and opencv to enable it for tracking multiiple objects
It has two modes. One is simply for tracking user defined objects of two categories
( referred here as vehicles and pedestrians)

The other mode is for analyzing the data obtained from the tracking for purposes of the project.


############################################################

'''
import numpy as np
import cv2
import argparse as ap
import dlib
import get_points
import get_line
import intersect
import xlwt


#Default open webcam if video source not specified
source=0


#Function to calculate the frames per second of the video.
#We do it manually by calculating Total_no_of_frames/Total_run_time
#Run_time of the video in seconds is a prerequisite
#Run time of the video is provided as flags if we wish to analyze the data (mode = True, in def run)
#Fps calculation is not needed when mode = False in run()

def get_fps(source, Videolength):
	cap = cv2.VideoCapture(source)
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

#Algorithm to check intersection of line segments
#It checks iteratively intersection between a pair of points(Last location of the vehicle) and pairs of points of another List(Pedestrian path)
def check_intersection(array, new_pnt, last_point):

	intersect_counter = 0
	for first, second in zip(array, array[1:]):
		intersect_counter += 1
		if intersect.seg_intersect(first, second, new_pnt, last_point):
			return len(array) - intersect_counter


#When mode = True, the Post Encroachment Time is stored in excel sheet.
#Various analysis of the video and the tracking is then done
#When mode is false, it only prints when trajectories of different types of object intersect.
#when mode is false, length parameter is irrelevant

def run(source, mode=False, length=500, dist=100):

	if mode:
		print "runtime of the video in seconds is - "+str(length)+" seconds"

	#list of touples containing coordinates of the rectangle
	#bounding the object of interest

	points_ped = []
	points_veh = []

	# Variable so that the trajectories are  dynamically increased and decreased. Trajectory length is constant
	frame_var_ped = 1000
	frame_var_veh = 1000

	#Store trajectory coordinates
	coord_ped = []
	coord_veh = []

	# list of pedestrian id's whose path vehicle has encroached
	collided_objects = []

	## For auto deletion of pedestrians and vehicles
	##if they wander in extremeties of the screen
	to_b_deleted_ped = []
	to_b_deleted_veh = []

	##To store all coordinates of points of conflict
	#to show later
	conflict_coord = []

	##Keep a list of every trajectory to display later
	trajectory_ped = []
	trajectory_veh = []

	# If first frame or not
	# In mode=True, we will have to do stuff in the first frame for analysis purpose
	first_frame = True

	if mode:


		# Distance between two reference lines that we will provide in first frame
		#The reference lines are two lines whose length we know in real-world
		#These lines will help in analysis accurately with real word distacnces/dimensions
		distance = dist

		#initialize no of conflict between trajectories
		noOfConflicts = -1

		#set up excel sheet for storing data
		wb = xlwt.Workbook()
		ws = wb.add_sheet("My Sheet")

		#Get fps of the source video.
		fps = get_fps(source, length)
		#fps = 25.02
		print "fps is - - " + str(fps)

		video = cv2.VideoCapture(source)

		frame_var_ped = 20 * fps
		frame_var_veh = 10 * fps

		#Initialize the columns of the sheet
		ws.write(0, 0, "PET")
		ws.write(0, 1, "Sex")
		ws.write(0,2,"Speed")
		ws.write(0,3,"Time")
		ws.write(0,4, "Coordinates")
		### <-- Lists/data to be stored with respect to vehicle --> ###

		#list to keep velocities of the vehicles
		velocity = []

		#bool to see if it's between the two reference lines
		vehicle_vel_bool = []

		#counter of frames which the vehicle spends between the reference lines
		vehicle_frame_counter = []

		#at which noOfConflict in the sheet, the desired vehicle has conflicts so that speed can be put
		#in the database in the same row
		which_conflict = []

		##Which assigned reference line the vehicle crosses first
		which_intersect = []

		###<--- Lists to be stored with respect to pedestrian -->###
		#Store sex of the pedestrian
		pedestrian_sex = []

	cap = cv2.VideoCapture(source)
	if not cap.isOpened():
		print "Video device or file couldn't be opened"
		exit()

	#variable to track how many frames has been processed
	time_counter = 0

	while(cap.isOpened()):
		# Capture frame-by-frame

		ret, frame = cap.read()
		if not ret:
			print "Unable to capture device or video ended.\nQuitting . . ."
			break

		#Resize window
		frame = cv2.resize(frame, (450, 350))
		height, width = frame.shape[:2]

		#Make frame size fixed
		cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)
		cv2.moveWindow('frame', 916, 418)


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

				print " press 'p' while the video plays to pause\n        and add objects to track  "
				print " press 'd' while the video plays to delete\n        an object  "
				print " press 'q' to quit \n "

				cv2.destroyWindow("Draw line here.")
			first_frame = False

		# Delete pedestrians and vehicles that go to extremes of frame automatically
#############################################################################################################################
		
		if to_b_deleted_ped:
			for x in to_b_deleted_ped:
				if mode:
					# try:
					del pedestrian_sex[x]
					##Delete list of collided vehicles mapped with vehicles
					for i in collided_objects:
						try:
							i.remove(x)
						except ValueError:
							pass

					trajectory_ped.append(coord_ped[x])

				del points_ped[x]
				del tracker_ped[x]
				del coord_ped[x]

			# Clear the record so that delete list can be refreshed
			to_b_deleted_ped = []

		if to_b_deleted_veh:
			for z in to_b_deleted_veh:
				if mode:
					for x in which_conflict[z]:
						ws.write(x, 2, velocity[z])

					del velocity[z]
					del vehicle_vel_bool[z]
					del vehicle_frame_counter[z]
					del which_conflict[z]
					del which_intersect[z]
					del collided_objects[z]

					trajectory_veh.append(coord_veh[z])

				del points_veh[z]
				del tracker_veh[z]
				del coord_veh[z]

			# Clear the record so that the delete list can be refreshed
			to_b_deleted_veh = []



		################################################################################################################################



		if points_ped or points_veh:
			key = cv2.waitKey(1) & 0xFF
		else:
			key = cv2.waitKey(30) & 0xFF

		#To delete already selected objects
		if key == ord('d'):
			if mode:
				print "\n press 'a' to delete a pedestrian "
				print " press 'b' to delete a vehicle "
				print " press 'r' to resume with tracking \n"
			else:
				print "\n press 'a' to delete an object of type-A "
				print " press 'b' to delete an object of type-B  "
				print " press 'r' to resume with tracking \n"


			while True:
				#input = raw_input(" \n Press appropriate key: ")
				k = cv2.waitKey(10) & 0xFF

				if k == ord('a'):
					input_a = -2

					while True:

						if mode:
							input_a = int(raw_input(" Enter id(on the terminal)  of the pedestrian to delete , -1 to move to other options :"))
						else:
							input_a = int(raw_input(
								" Enter id(on the terminal)  of the type-A object to delete , -1 to move to other options :"))

						if input_a == -1:

							if mode:
								print "\n press 'a' to delete a pedestrian "
								print " press 'b' to delete a vehicle "
								print " press 'r' to resume with tracking "
								break
							else:
								print "\n press 'a' to delete an object of type-A "
								print " press 'b' to delete an object of type-B "
								print " press 'r' to resume with tracking "
								break

						elif input_a < len(points_ped):
							if mode:
								del pedestrian_sex[input_a]
								for i in collided_objects:
									try:
										i.remove(input_a)
									except ValueError:
										pass

								trajectory_ped.append(coord_ped[input_a])
							del points_ped[input_a]
							del tracker_ped[input_a]
							del coord_ped[input_a]
							print" Object deleted successfully"
						else:
							print " Enter a valid id! "
						pass


				elif k == ord('b'):
					while True:

						if mode:
							input_b = int(raw_input(" Enter id(on the terminal)  of the vehicle to delete , -1 to move to other :"))
						else:
							input_b = int(raw_input(
								" Enter id(on the terminal)  of type-B object to delete , -1 to move to other :"))

						if input_b < 0:

							if mode:
								print "\n press 'a' to delete a pedestrian "
								print " press 'b' to delete a vehicle "
								print " press 'r' to resume with tracking "
								break
							else:
								print "\n press 'a' to delete an object of type-A "
								print " press 'b' to delete an object of type-B "
								print " press 'r' to resume with tracking "
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
								del collided_objects[input_b]

								trajectory_veh.append(coord_veh[input_b])

							del points_veh[input_b]
							del tracker_veh[input_b]
							del coord_veh[input_b]
							print" Object deleted successfully"

						else:
							print " Enter a valid id! "
						pass



				elif k == ord('r'):

					break




		if key == ord('q'):
			print"\nQuitting . . \n"
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
				if mode:
					print "\nAdd Pedestrians . . \nDrag rectangles across the frame to assign objects\n"
				else:
					print "\nAdd type-A objects . . \nDrag rectangles across the frame to assign objects\n"

				if mode:
					temp_ped, temp_sex = get_points.run(frame,mode,for_pedestrian=True)

					if temp_ped == "QUIT":
						cv2.destroyWindow("Select objects to be tracked here.")
						cv2.destroyWindow("Objects to be tracked.")
						break
					else:
						for x in temp_ped:
							points_ped.append(x)
						for y in temp_sex:
							pedestrian_sex.append(y)
				else:
					temp_ped = get_points.run(frame, mode, for_pedestrian=True)
					if temp_ped=="QUIT":
							cv2.destroyWindow("Select objects to be tracked here.")
							cv2.destroyWindow("Objects to be tracked.")
							break
					else:
						for x in temp_ped:
							points_ped.append(x)

				#Add vehicles to track
				if mode:
					print "\nAdd vehicles, if any\nDrag rectangles across the frame to assign objects\n"
				else:
					print "\nAdd type-B objects if any . . \nDrag rectangles across the frame to assign objects\n"

				temp_veh=get_points.run(frame,mode,for_pedestrian=False)

				'''Can be made more efficient '''
				if temp_veh == "QUIT":
					cv2.destroyWindow("Select objects to be tracked here.")
					cv2.destroyWindow("Objects to be tracked.")
					break
				else:
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
					print "\nResumed\n"
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

					if mode:
						cv2.putText(frame, "ped"+str(i) , (int((pt1[0]+pt2[0])/2),int(pt1[1]+2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
					else:
						cv2.putText(frame, "A" + str(i), (int((pt1[0] + pt2[0]) / 2), int(pt1[1] + 2)),
									cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
					# Add trajectory of new objects
					if len(coord_ped)<(i+1):
						coord_ped.append(np.empty((0,2),np.uint32))

					#update trajectory
					coord_ped[i] = np.append(coord_ped[i],np.array([[(pt1[0]+pt2[0])/2,pt2[1]]]),axis = 0)
					#Keep the length of trajectory constant
					if len(coord_ped[i])>frame_var_ped:
						coord_ped[i] = np.delete(coord_ped[i], (0), axis=0)

					##Autodelete if the object goes to some extreme of the image
					if (not (width*.05<coord_ped[i][-1][0]< width*.95)) or (not (height*.05<coord_ped[i][-1][1]< height*.95)):
						to_b_deleted_ped.append(i)
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
					if mode:
						cv2.putText(frame, "veh"+str(i), (int((pt1[0] + pt2[0]) / 2), int(pt1[1] - 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 255), 1)
					else:
						cv2.putText(frame, "B" + str(i), (int((pt1[0] + pt2[0]) / 2), int(pt1[1] - 2)),
									cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)


					# Add trajectory of new objects
					if len(coord_veh) < (i + 1):
						coord_veh.append(np.empty((0, 2), np.uint32))

					##update trajectory
					coord_veh[i] = np.append(coord_veh[i], np.array([[(pt1[0] + pt2[0]) / 2, pt2[1]]]), axis=0)
					if len(coord_veh[i]) > frame_var_veh:
						coord_veh[i] = np.delete(coord_veh[i], (0), axis=0)

					# draw trajectory
					cv2.polylines(frame, [coord_veh[i]], False, (0, 0, 255),2)

					##Autodelete if the object goes to some extreme of the image
					if (not (width*.05<coord_veh[i][-1][0]< width*.95)) or (not (height*.05<coord_veh[i][-1][1]< height*.95)):
						to_b_deleted_veh.append(i)


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

									##Add the coordinates of the collision region to database
									conflict_coord.append(coord_veh[i][-1])

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
										#Store in database
										ws.write(noOfConflicts+1, 0, str(required_value/fps))
										ws.write(noOfConflicts+1, 1, str(pedestrian_sex[index]))
									 	ws.write(noOfConflicts+1, 3, str(time_counter/fps))
										ws.write(noOfConflicts+1, 4, str(coord_veh[i][-1]))
								index+=1


		if mode:
			#Draw reference lines
			cv2.polylines(frame, np.int32([l1]), False, (255, 0, 0))
			cv2.polylines(frame, np.int32([l2]), False, (0, 255, 0))

			#Update Counter for getting time
			time_counter += 1
			cv2.putText(frame, str(time_counter / fps), (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 3)


		cv2.imshow('frame', frame)
	# When everything done, release the capture

	cap.release()

	if mode:
		#print conflict_coord
		###Save the sheet
		wb.save("PET_Values.xls")

		###Show all the conflict points in a new window consisting of the first frame of the object
		cap = cv2.VideoCapture(source)

		if (cap.isOpened()):
			ret, frame = cap.read()

		frame = cv2.resize(frame, (450, 350))

		im_veh = frame.copy()
		im_ped = frame.copy()
		#Draw trajectories

		for trajectories in trajectory_veh:
			cv2.polylines(im_veh, [trajectories], False, (0, 0, 255), 1)

		for trajectories in trajectory_ped:
			cv2.polylines(im_ped, [trajectories],False, (255,0,255), 1)

		##Draw circles
		for x in conflict_coord:
			cv2.circle(frame, (x[0], x[1]), 6, (255, 255, 255), -1)
			cv2.circle(frame, (x[0], x[1]), 6, (0, 0, 255), 1)


		while (1):
			cv2.imshow('Conflict Points', frame)
			cv2.imshow('Vehicle trajectories', im_veh)
			cv2.imshow('Pedestrian trajectories' , im_ped)


			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

		cap.release()
		cv2.destroyAllWindows()


if __name__ == "__main__":
    # Parse command line arguments
	parser = ap.ArgumentParser()
	#group = parser.add_mutually_exclusive_group(required=True)
	parser.add_argument('-v', "--videoFile", help="Path to Video File", type=str)
	parser.add_argument('-l', "--videoLen", help="Length of the video in seconds",type=float)
	parser.add_argument('-m', "--WriteMode", help="If yes, writes output to a excel file" ,type=bool)
	parser.add_argument('-d', "--distance", help="distance between two reference lines in real world",type = float)

	args = vars(parser.parse_args())

	distance = 100

	if args["videoFile"]:
		source =(args["videoFile"])

	if args["distance"]:
		distance = (args["distance"])

	if args["videoLen"]:
		length = args["videoLen"]

		run(source, True, length, distance)

	else:
		run(source)