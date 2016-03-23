#import matplotlib
import numpy as np
#import matplotlib.pyplot as plt
from scipy.misc import imsave
#from pylab import savefig
import os
#import time
from skimage.morphology import opening, disk
from skimage.measure import label, regionprops
import cv2 as cv
import time
from multiprocessing import Pool

caffe_root = "../Documents/caffe_master/"
#import sys
#sys.path.insert(0, caffe_root + 'python')
#sys.path.append('/home/sasha/anaconda/lib/python2.7/site-packages/google/protobuf/internal')
import caffe

MODEL_FILE = 'deploy.prototxt'
PRETRAINED = 'model.caffemodel'

net = caffe.Net(MODEL_FILE, PRETRAINED, caffe.TEST)
caffe.set_mode_cpu()

transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_transpose('data', (2,0,1))
transformer.set_mean('data', np.load('mean1.npy').mean(1).mean(1)) # mean pixel
transformer.set_raw_scale('data', 255)  # the reference model operates on images in [0,255] range instead of [0,1]#
transformer.set_channel_swap('data', (2,1,0))  # the reference model has channels in BGR order instead of RGB
net.blobs['data'].reshape(1,3,32,32)
# while (1):
# 	start = time.time()
# 	net.blobs['data'].data[...] = transformer.preprocess('data', caffe.io.load_image("6.png"))
# 	out_cnn = net.forward()
# 	end = time.time()
# 	print end - start


from moviepy.editor import *

# list_dir = ["bucket11.mp4"]
# print list_dir
# global_path = '/media/sasha/Seagate/SmokeAndFire/all_video/'

# list_dir = [f for f in os.listdir(global_path) if '.avi' in f or '.mp4' in f or '.wmv' in f]
# global_path = '';
# list_dir = ['fire_pos14.avi']
global_path = '';
list_dir = []
f = open("video_with_fire.txt")
list_dir = f.read().splitlines()

step = 10
size = 5


def rgb2gray(rgb):
	return np.dot(rgb[...,:3], [0.299, 0.587, 0.144])
f = open('result.txt', 'w')

#create background of first step * size frames - 10, 5 - 2 seconds
#for video_name in list_dir:
def special(video_name):
	if not os.path.exists(global_path + video_name[video_name.rfind('/') + 1:video_name.rfind('.')]):
		os.makedirs(global_path + video_name[video_name.rfind('/') + 1:video_name.rfind('.')])
		print video_name[video_name.rfind('/') + 1:video_name.rfind('.')]
	else:
		#continue
		return
	#main loop
	clipFilename = global_path + video_name
	f.write('\n')
	f.write(video_name)
	print clipFilename
	first_detect = True
	video = VideoFileClip(clipFilename)
	f.write(' %f ' %(video.duration))
	folder_name = global_path + video_name[video_name.rfind('/') + 1:video_name.rfind('.')] + "/"
	print folder_name
	mean_r = np.zeros((video.size[1], video.size[0], size))
	mean_g = np.zeros((video.size[1], video.size[0], size))
	mean_b = np.zeros((video.size[1], video.size[0], size))
	for i in range(0, size):
		mean_r[:,:,i] = video.get_frame(i * step / video.fps)[:,:,0]
		mean_b[:,:,i] = video.get_frame(i * step / video.fps)[:,:,1]
		mean_g[:,:,i] = video.get_frame(i * step / video.fps)[:,:,2]
	cell_size = 100
	length_size = 3
	amount_height = int(round((float(video.size[1]) / cell_size)))
	amount_width = int(round(float(video.size[0]) / cell_size))
	#detect = np.zeros((int(round((float(video.size[1]) / cell_size))), int(round(float(video.size[0]) / cell_size))))
	#detect = np.zeros((amount_height, amount_width, length_size))
	detect = []
	start = time.time()
	num_frame_in_background = 0
	for frame in range(size * step + step, int(video.duration * video.fps), step):
		print clipFilename, frame
		background = np.dstack((np.median(mean_r, axis = 2), np.median(mean_g, axis = 2), np.median(mean_b, axis = 2)))
		cur_image = video.get_frame(frame / video.fps)
		cur_image_copy = np.copy(cur_image)
		cur_image_with_rectangle = np.copy(cur_image)
		cur_image = rgb2gray(abs(cur_image - background))
		cur_image = (cur_image > 5) * 255
		cur_image = opening(cur_image, disk(2))
		image_label = label(cur_image)
		i = 0
		for region in regionprops(image_label):
			if region.area < 50:
				continue
			i = i + 1
			y, x, y_end, x_end = region.bbox
			x = (x + x_end) / 2 - 24
			y = (y + y_end) / 2 - 24
			x_end = x + 48
			y_end = y + 48
			if x_end > video.size[0] - 1:
				x_end = video.size[0] - 1
				x = x_end - 48
			if y_end > video.size[1] - 1:
				y_end = video.size[1] - 1
				y = y_end - 48
			if x < 0:
				x = 0
				x_end = x + 48
			if y < 0:
				y = 0
				y_end = y + 48
			#imsave(folder_name + str(frame) + "_" + str(i) + ".png", cur_image_copy[y:y_end, x:x_end, :].astype(float32))
	        #net.blobs['data'].data[...] = transformer.preprocess('data', caffe.io.load_image(folder_name + str(frame) + "_" + str(i) + ".png"))
	        #os.remove(folder_name + str(frame) + "_" + str(i) + ".png")
			temp = np.zeros((48, 48,3), dtype= 'f')
			temp[:,:,:] = cur_image_copy[y:y_end, x:x_end,:]/float(255)
			net.blobs['data'].data[...] = transformer.preprocess('data', temp)
			out_cnn = net.forward()
			res_cnn = int(format(out_cnn['prob'].argmax()))
			color = (0, 0, 0)
			if (res_cnn == 1):
				color = (255, 0, 0)
				for i, n in enumerate(detect):

					center_x = (x + x_end) / 2
					center_y = (y + y_end) / 2
					if (n[0][0] - cell_size <= center_y <= n[0][0] + cell_size) and (n[0][1] - cell_size <= center_x <= n[0][1] + cell_size) and n[2] != frame:
						n[1][0] = 1
						break
				else:
					detect.append((((y+y_end)/2, (x + x_end) /2), np.array([1, 0, 0, 0]), frame))
					cv.rectangle(cur_image_with_rectangle, ((x + x_end) /2 - cell_size, (y+y_end)/2 - cell_size), ((x + x_end) /2 + cell_size, (y+y_end)/2 + cell_size), (0,0, 255), 2)
			else:
				color = (0, 255, 0)

			cv.rectangle(cur_image_with_rectangle, (x, y), (x_end, y_end), color, 2)
		#print frame
		##print detect
		#print
		for i, n in enumerate(detect):
			if (np.sum(n[1]) == 3 or np.sum(n[1]) == 4):
				#print frame / video.fps
				if first_detect:
					f.write(' %f' % (frame / video.fps))
					first_detect = False
				cv.rectangle(cur_image_with_rectangle,(n[0][1] - cell_size, n[0][0] - cell_size), (n[0][1] + cell_size, n[0][0] + cell_size), (255, 0, 0), 2)
			if (n[1][0] == 0 and n[1][1] == 1 and n[1][2] == 1):
				continue
			if (n[1][0] == 0 and n[1][1] == 1 and n[1][2] == 0):
				del detect[i]
		for i, n in enumerate(detect):
			n[1][1:] = n[1][0:-1]
			n[1][0] = 0
		imsave(folder_name + str(frame) + ".png", cur_image_with_rectangle)
		mean_r[:,:,num_frame_in_background] = cur_image_copy[:,:,0]
		mean_g[:,:,num_frame_in_background] = cur_image_copy[:,:,1]
		mean_b[:,:,num_frame_in_background] = cur_image_copy[:,:,2]
		num_frame_in_background += 1
		num_frame_in_background = num_frame_in_background % size
	print video_name, time.time() - start
# special(list_dir[0])
pool = Pool(8)
pool.map(special, list_dir)
pool.close()
pool.join()