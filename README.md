# FlyEye - Assisted Driving with a drone.

This code is for communication between a computer that gets the feed from the drone and runs detections algorithms on it, and an app for the driver.


Tested on Ubuntu 16.04.3 LTS.


+ src - the code for the android app.

+ hotspot_sock_connection - runs on the computer. establishes the connection between computer and app, runs detection algorithms on the feed from the drone and send results to the app.

# To use:
1. Build the app and install the apk on the android device.
2. Open a hotspot connection on the android device and connect the computer to that connection.
3. Run the app.
4. Run sendImgSock.py
5. you can run displaywebcam to create a feed that'll be sent to the device.

## Detection algorithm:
The detection algorithm uses the YOLO(you only look once) neural network architecture to detect(classify & localize) objects of interest in an image.

Link the the original YOLO paper: https://pjreddie.com/media/files/papers/yolo.pdf

This project uses a port of YOLO from the Darknet framework to tensorflow & keras from the following repository: https://github.com/allanzelener/YAD2K

We use tiny-yolo and the pascal classes for real time detection.

## To use the detection algorithm on the feed:
1. install dependencies: numpy(linear algebra), h5py(binary dumps), pillow(for image loading), tensorflow-gpu,keras( Neural network frameworks).

To install with pip:

In the terminal:
```
pip install numpy h5py pillow
pip install tensorflow-gpu 
pip install keras 
```
2. cd into model_data
   download tiny-yolo's pre-trained weights and anchors.
   In the terminal:
   ```
   wget http://pjreddie.com/media/files/tiny-yolo-voc.weights
   wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/tiny-yolo-voc.cfg
   ./yad2k.py tiny-yolo-voc.cfg tiny-yolo-voc.weights model_data/tiny-yolo-voc.h5
   ```
3. Run yolodetect.py for testing.


*Optional: run sendImgSockWithDetection.py to send image after detection to the device.*
   