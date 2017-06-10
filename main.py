import numpy as np
import cv2
import argparse as ap

source = 0

def run(source):
	cap = cv2.VideoCapture(source)
	if not cap.isOpened():
		print "Video device or file couldn't be opened"
		exit()

	cv2.namedWindow("Paused")

	while(True):
		# Capture frame-by-frame
		ret, frame = cap.read()
		if not ret:
			print "Unable to capture device"

		# Our operations on the frame come here
		#gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		# Display the resulting frame

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

		if cv2.waitKey(10) & 0xFF == ord('p'):

			while True:

				key2 = cv2.waitKey(1) or 0xff
				cv2.imshow('Paused', frame)

				if key2 == ord('p'):
					break
			pass








		cv2.imshow('frame', frame)
	# When everything done, release the capture



	cap.release()
	cv2.destroyAllWindows()



#if __name__=="__main__":
if __name__ == "__main__":
    # Parse command line arguments
	parser = ap.ArgumentParser()
	#group = parser.add_mutually_exclusive_group(required=True)
	parser.add_argument('-v', "--videoFile", help="Path to Video File")
	args = vars(parser.parse_args())

	if args["videoFile"]:
		source = args["videoFile"]

	run(source)


