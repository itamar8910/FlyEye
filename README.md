# FlyEye - Assisted Driving with a drone.

This repository contains the code for our Assisted Driving System, FlyEye. 
It has two parts:


+ app_code - The code of the android app the driver uses.

+ on_laptop - Runs on a laptop that's inside the car. Establishes the connection between computer and app, receives and processes the video feed from the drone, runs detection algorithms on the feed and sends results to the app.

# Prerequisites:
- You need a computer that runs Linux (We used Ubuntu 16.04.3 LTS).
- Hardware: A SYMA X5C drone, the TX5805 RF camera mounted on it, and the ImmersionRC Duo5800 RF video receiver.
- Python 3.5 or above.
- The following Python packages: numpy(linear algebra), h5py(binary dumps), pillow(for image loading), tensorflow-gpu,keras( Neural network frameworks).
To install with pip:

In the terminal:
```
pip install numpy h5py pillow
pip install tensorflow-gpu 
pip install keras 
```

- You need the network's weights and anchors. create a directory named 'model_data' inside on_laptop. 
In the terminal:
   ```
   wget http://pjreddie.com/media/files/tiny-yolo-voc.weights
   wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/tiny-yolo-voc.cfg
   ./yad2k.py tiny-yolo-voc.cfg tiny-yolo-voc.weights model_data/tiny-yolo-voc.h5
   ```
# To use:
1. Build the app and install the apk on your android device.
2. Open a hotspot connection on the android device and connect the computer to that connection.
3. Run the app.
4. Turn on the drone and connect the video receiver to your computer.
5. Run on_laptop/getdronefeed.py to receive the video feed from the RF camera and deinterlace it.
6. Run detection_main to establish a connection between your computer and the android app, and routinely send processed data to the app.
5. You should now see the video feed from the drone in the app.

## Detection algorithm:
The detection algorithm uses the YOLO(you only look once) neural network architecture to detect(classify & localize) objects of interest in an image.

Link the the original YOLO paper: https://pjreddie.com/media/files/papers/yolo.pdf

This project uses a port of YOLO from the Darknet framework to tensorflow & keras from the following repository: https://github.com/allanzelener/YAD2K

We use tiny-yolo and the pascal classes for real time detection.

   
