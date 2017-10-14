import base64
import json
import os
import random
import socket               # Import socket module
import time
# import argparse
# import imghdr

from PIL import Image, ImageDraw, ImageFont
import colorsys
import cv2
from keras import backend as K
from keras.models import load_model
import numpy as np
from yad2k.models.keras_yolo import yolo_eval, yolo_head
from alert_system import is_dangerous
# import tensorflow as tf

# YOLO port to tensorflow is based on https://github.com/allanzelener/YAD2K

s = socket.socket()         # Create a socket object
host = '192.168.43.1'
port = 8888                # Reserve a port for your service.


model_path = 'model_data/tiny-yolo-voc.h5'
anchors_path = 'model_data/tiny-yolo-voc_anchors.txt'
classes_tags_path = 'model_data/pascal_classes.txt'
intersection_of_union_threshold = .5
score_threshold = .3

tf_session = K.get_session()

with open(classes_tags_path) as f:
	class_tags = f.readlines()
class_tags = [c.strip() for c in class_tags]

with open(anchors_path) as f:
	anchors = f.readline()
	anchors = [float(x) for x in anchors.split(',')]
	anchors = np.array(anchors).reshape(-1, 2)

yolo_model_keras = load_model(model_path)

# Verify model, anchors, and classes are compatible
num_of_classes = len(class_tags)
num_of_anchors = len(anchors)
model_output_channels = yolo_model_keras.layers[-1].output_shape[-1]

model_image_size = yolo_model_keras.layers[0].input_shape[1:3]
is_fixed_size = model_image_size != (None, None)

# Generate colors for drawing bounding boxes.
hsv_tuples = [(x / len(class_tags), 1., 1.) for x in range(len(class_tags))]
colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
colors = list(
	map(
		lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
		colors))
random.seed(10101)  # Fixed seed for consistent colors across runs.
random.shuffle(colors)  # Shuffle colors to decorrelate adjacent classes.
random.seed(None)  # Reset seed to default.

# Generate output tensor targets for filtered bounding boxes.
yolo_outputs = yolo_head(yolo_model_keras.output, anchors, len(class_tags))
input_image_shape = K.placeholder(shape=(2, ))
boxes, scores, classes = yolo_eval(
	yolo_outputs,
	input_image_shape,
	score_threshold=score_threshold,
	iou_threshold=intersection_of_union_threshold)


def detect_img(img_path, out_path):
	try:
		image = Image.open(os.path.join("", img_path))
	except Exception:
		print("Image load exception")
		return
	if is_fixed_size:  
		try:
			resized_image = image.resize(
				tuple(reversed(model_image_size)), Image.BICUBIC)
			image_data = np.array(resized_image, dtype='float32')
		except Exception:
			print("Image Exception")
			return
	else:
		new_image_size = (
			image.width - (image.width % 32),
			image.height - (image.height % 32))
		resized_image = image.resize(new_image_size, Image.BICUBIC)
		image_data = np.array(resized_image, dtype='float32')
		print(image_data.shape)

	image.save(out_path, quality=90)

	image_data /= 255.
	image_data = np.expand_dims(image_data, 0)  # Add batch dimension.
	out_boxes, out_scores, out_classes = tf_session.run(
		[boxes, scores, classes],
		feed_dict={
			yolo_model_keras.input: image_data,
			input_image_shape: [image.size[1], image.size[0]],
			K.learning_phase(): 0
		})
	print('Found {} boxes for {}'.format(len(out_boxes), img_path))
	font = ImageFont.truetype(
		font='font/FiraMono-Medium.otf',
		size=np.floor(3e-2 * image.size[1] + 0.5).astype('int32'))
	thickness = (image.size[0] + image.size[1]) // 300
	detections = [] # init detections list of bounding boxes
	for i, c in reversed(list(enumerate(out_classes))): # iterate bounding box predictions
		predicted_class = class_tags[c]
		box = out_boxes[i]
		score = out_scores[i]

		label = '{} {:.2f}'.format(predicted_class, score)

		draw = ImageDraw.Draw(image)
		label_size = draw.textsize(label, font)

		top, left, bottom, right = box
		top = max(0, np.floor(top + 0.5).astype('int32'))
		left = max(0, np.floor(left + 0.5).astype('int32'))
		bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
		right = min(image.size[0], np.floor(right + 0.5).astype('int32'))
		print("bounding box: " , label, (left, top), (right, bottom))

		detections.append([predicted_class, '{:.2f}'.format(score) ,top, (right-left),(bottom-top)]) # append bounding box data to detections list
		if top - label_size[1] >= 0:
			text_origin = np.array([left, top - label_size[1]])
		else:
			text_origin = np.array([left, top + 1])

		for i in range(thickness):
			draw.rectangle(
				[left + i, top + i, right - i, bottom - i],
				outline=colors[c])
		draw.rectangle(
			[tuple(text_origin), tuple(text_origin + label_size)],
			fill=colors[c])
		draw.text(text_origin, label, fill=(0, 0, 0), font=font)
		del draw

	image.save(out_path, quality=90)
	return detections


print("connecting with server")
s.connect((host, port))
print("successfully connected with server")


def get_collision_data(detections):
	collision_danger = is_dangerous(detections)
	return collision_danger if collision_danger else []


while(True):
	print("detecting")
	detections = detect_img("frame.jpg","frameout.jpg")

	with open("frame.jpg", "rb") as image_file:
		encoded_string = base64.b64encode(image_file.read())
		if len(encoded_string) == 0:
			continue

		s.sendall(b"" + encoded_string) # send a frame from video feed to mobile, encoded in b64
		print("sent byte array of length", len(encoded_string))
		s.recv(1024) # receive OK from mobile
		b = bytearray()
		collision_data = get_collision_data(detections)
		b.extend(map(ord, "detections:" + json.dumps([collision_data, detections]))) # send detection data to mobile
		s.sendall(b)
		s.recv(1024) # receive OK from mobile


s.close()                   # close the socket when done
tf_session.close()
