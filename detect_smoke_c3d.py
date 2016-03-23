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

model_def_file = '/home/sasha/C3d_python/examples/c3d_train_ucf101/deploy.prototxt'
model_file = '/home/sasha/C3d_python/examples/c3d_train_ucf101/conv3d_ucf101_iter_5000'
mean_file = '/home/sasha/C3d_python/examples/c3d_train_ucf101/mean.binaryproto'
net = caffe.Net(model_def_file, model_file)
print net.blobs['prob'].data.shape[1]

# caffe init
gpu_id = 0
net.set_device(gpu_id)
net.set_mode_gpu()
net.set_phase_test()

blob = caffe.proto.caffe_pb2.BlobProto()
data = open(mean_file,'rb').read()
blob.ParseFromString(data)
image_mean = np.array(caffe.io.blobproto_to_array(blob))
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
global_path = '';
# list_dir = ['fire_pos14.avi']

step = 10
size = 5

from c3d_classify import c3d_classify
def rgb2gray(rgb):
	return np.dot(rgb[...,:3], [0.299, 0.587, 0.144])

#create background of first step * size frames - 10, 5 - 2 seconds
#for video_name in list_dir:
def special(video_name):
	if not os.path.exists(global_path + video_name[video_name.rfind('/') + 1:video_name.rfind('.')]):
		os.makedirs(global_path + video_name[video_name.rfind('/') + 1:video_name.rfind('.')])
		print video_name[video_name.rfind('/') + 1:video_name.rfind('.')]
	#main loop
	first_detect = True
	video = VideoFileClip(video_name)
	folder_name = global_path + video_name[video_name.rfind('/') + 1:video_name.rfind('.')] + "/"
	print folder_name
	mean_r = np.zeros((video.size[1], video.size[0], size))
	mean_g = np.zeros((video.size[1], video.size[0], size))
	mean_b = np.zeros((video.size[1], video.size[0], size))
	for i in range(0, size):
		mean_r[:,:,i] = video.get_frame(i * step / video.fps)[:,:,0]
		mean_b[:,:,i] = video.get_frame(i * step / video.fps)[:,:,1]
		mean_g[:,:,i] = video.get_frame(i * step / video.fps)[:,:,2]
	cell_size = 300
	#detect = np.zeros((int(round((float(video.size[1]) / cell_size))), int(round(float(video.size[0]) / cell_size))))
	#detect = np.zeros((amount_height, amount_width, length_size))
	detect = []
	start = time.time()
	num_frame_in_background = 0
	for frame in range(size * step + step, int(video.duration * video.fps), step):
		print  frame
		background = np.dstack((np.median(mean_r, axis = 2), np.median(mean_g, axis = 2), np.median(mean_b, axis = 2)))
		cur_image = video.get_frame(frame / video.fps)
		cur_image_copy = np.copy(cur_image)
		cur_image_with_rectangle = np.copy(cur_image)
		cur_image = rgb2gray(abs(cur_image - background))
		cur_image = (cur_image > 5) * 255
		cur_image = opening(cur_image, disk(2))
		image_label = label(cur_image)
		i = 0
		asdf = 0
		for region in regionprops(image_label):
			if region.area < 50:
				continue
			i = i + 1
			print i
			y, x, y_end, x_end = region.bbox
			x = (x + x_end) / 2 - 50
			y = (y + y_end) / 2 - 50
			x_end = x + 100
			y_end = y + 100
			if x_end > video.size[0] - 1:
				x_end = video.size[0] - 1
				x = x_end - 100
			if y_end > video.size[1] - 1:
				y_end = video.size[1] - 1
				y = y_end - 100
			if x < 0:
				x = 0
				x_end = x + 100
			if y < 0:
				y = 0
				y_end = y + 100
			frame_info = np.zeros((100, 100, 3, 4), dtype = np.uint8)
			mean_r1 = np.zeros((100, 100, 4))
			mean_g1 = np.zeros((100, 100, 4))
			mean_b1 = np.zeros((100, 100, 4))
			temp1 = np.zeros(())
			for j in range(0, 4):
				temp1 = video.get_frame((frame + j * 5) / float(video.fps))
				# imsave(folder_name + str(i) + ".jpg", temp1[y:y_end, x:x_end, :])
				frame_info[:,:,:,j] = temp1[y:y_end, x:x_end,:]
				mean_r1[:,:,j] = temp1[y:y_end,x:x_end,0]
				mean_g1[:,:,j] = temp1[y:y_end,x:x_end,1]
				mean_b1[:,:,j] = temp1[y:y_end,x:x_end,2]

			temp22 = np.dstack((np.median(mean_r1, axis = 2), np.median(mean_g1, axis = 2), np.median(mean_b1, axis = 2)))
			# for j in range(0, 4):
			# 	temp1 = video.get_frame((frame + j * 5) / float(video.fps))
			# 	imsave(folder_name + "%06d" % (50 * asdf + j * 5 + 1) + ".jpg", np.abs(temp1[y:y_end, x:x_end, :] - temp22))
			# asdf+=1
			for j in range(0, 4):
				frame_info[:,:,:,j] = np.abs(frame_info[:,:,:,j] - temp22)
				for k in range(0,100):
					for m in range(0,100):
						print frame_info[k,m,:,j]
				print frame_info[0,0,:,j]
				frame_info[:,:,:,j] = frame_info[:,:,[2, 1, 0],j].astype(np.uint8)
				print frame_info[10,10,:,j]

				imsave(global_path + "temp.jpg",frame_info[:,:,:,j])
				frame_info[:,:,:,j] = cv.imread(global_path + "temp.jpg",cv.IMREAD_UNCHANGED)
				for k in range(0,100):
					for m in range(0,100):
						print frame_info[k,m,:,j]
				exit()
			prediction = c3d_classify(
				images= frame_info,
				image_mean=image_mean,
				net=net,
				prob_layer='prob'
				)
			print prediction
			res_cnn = int(prediction.argmax())
			color = (0, 0, 0)
			if (res_cnn == 0):
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
		print frame
		##print detect
		#print
		for i, n in enumerate(detect):
			if (np.sum(n[1]) == 3 or np.sum(n[1]) == 4):
				#print frame / video.fps
				if first_detect:
					# f.write(' %f' % (frame / video.fps))
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
special("/home/sasha/Desktop/data/freelance3/boiler11.mp4")
