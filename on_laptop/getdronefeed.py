# import numpy as np
import cv2

cap = cv2.VideoCapture(1)
while(True):
	# Capture frame-by-frame
	ret, frame = cap.read()
	frame[1:-1:2] = frame[0:-2:2]/2 + frame[2::2]/2  # deinterlace image
	cv2.imwrite('frame.jpg', frame)

	# Display the resulting frame
	cv2.imshow('frame', frame)
	key = cv2.waitKey(1)
	if key & 0xFF == ord('q') or key & 0xFF == 27:
		break

# When everything's done, release the capture
cap.release()
cv2.destroyAllWindows()
