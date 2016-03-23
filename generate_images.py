import re
import numpy as np
from moviepy.editor import *
from scipy.misc import imsave
from skimage.morphology import opening, disk
from skimage.measure import label, regionprops
import cv2 as cv
import os
import time
from multiprocessing import Pool
step = 10
size = 5
global_smoke = 0
global_fire = 0
global_none = 0
def generate_images_from_one_video(filename):
	print filename
	#filename = "printer11.mp4"
	filename1 = filename[:filename.rfind(".")] + "_label.txt"
	filename_smoke = filename[:filename.rfind(".")] + "/smoke/"
	filename_fire = filename[:filename.rfind(".")] + "/fire/"
	filename_none = filename[:filename.rfind(".")] + "/none/"
	filename_temp = filename[:filename.rfind(".")] + "/temp/"
	if not os.path.exists(filename_smoke):
		os.makedirs(filename_smoke)
	else:
		return None
	if not os.path.exists(filename_fire):
		os.makedirs(filename_fire)
	if not os.path.exists(filename_none):
		os.makedirs(filename_none)
	if not os.path.exists(filename_temp):
		os.makedirs(filename_temp)
	video = VideoFileClip(filename)
	def bbox(list):
		return min(list[0], list[2]), min(list[1], list[3]), max(list[0], list[2]), max(list[1], list[3])
	def intersectionTwoRectangle(rect1, rect2):
		isIntersect = not(rect1[2] < rect2[0] or rect1[3] < rect2[1] or rect2[2] < rect1[0] or rect2[3] < rect1[1])
		x0 = y0 =  x1 =  y1 = 0
		if isIntersect:
			x0 = max(rect1[0], rect2[0])
			y0 = max(rect1[1], rect2[1])
			x1 = min(rect1[2], rect2[2])
			y1 = min(rect1[3], rect2[3])
		return isIntersect, abs((x1 - x0) * (y1 - y0)), x0, y0, x1, y1
	def rgb2gray(rgb):
		return np.dot(rgb[...,:3], [0.299, 0.587, 0.144])

	f = open(filename1, "r")
	f.readline()
	f.readline()
	f.readline()
	f.readline()
	img0 = video.get_frame(0)
	mean_r = np.zeros((video.size[1], video.size[0], size))
	mean_g = np.zeros((video.size[1], video.size[0], size))
	mean_b = np.zeros((video.size[1], video.size[0], size))
	print mean_r.shape
	start_time = time.time()
	example_smoke = 0
	example_fire = 0
	example_none = 0
	for frame in range(0, int(video.duration * video.fps), step):
		mean_r[:,:,(frame / step) % size] = video.get_frame(frame/ video.fps)[:,:,0]
		mean_g[:,:,(frame / step) % size] = video.get_frame(frame /video.fps)[:,:,1]
		mean_b[:,:,(frame / step) % size] = video.get_frame(frame / video.fps)[:,:,2]
		if frame == 0:
			continue
		if (frame % ( size * step) == 0):
			temp = np.dstack((np.median(mean_r, axis = 2), np.median(mean_g, axis = 2), np.median(mean_b, axis = 2)))
			#imsave("background/mean" + str(frame) +".png", temp)
			#imsave("background/mean" + str(frame) + "_.png", video.get_frame(frame / video.fps ))
			temp_image = video.get_frame(frame / video.fps)
			temp_image1 = np.copy(temp_image)
			#print type(temp_image)
			#print temp_image.shape
			temp1 = rgb2gray(abs(video.get_frame(frame / video.fps) - temp))
			#imsave("background/mean" + str(frame) + "__.png",temp1)
			temp1 = (temp1 > 5) * 255
			temp1 = opening(temp1, disk(2))
			x1 = label(temp1)
			i = 0
			f.readline()
			string = f.readline()
			if string == "":
				continue
			n = re.split('[,\s\[\]]', string)
			a = [x for i,x in enumerate(n) if x != '']
			smoke_ind = a.index("smoke")
			fire_ind =  a.index("fire")
			dict = {}
			dict["smoke"] = []
			dict["fire"] = []
			if (a[2] != "fire"):
				for i in range(0, (fire_ind - smoke_ind) / 4):
					dict["smoke"].append([int(float(k)) for k in a[2 + 4 * i: 2 + 4 + 4 * i]])
			if (len(a) - fire_ind != 1):
				for i in range(0, (len(a) - fire_ind) / 4):
					dict["fire"].append([int(float(k)) for k in a[fire_ind + 1 + 4 * i: fire_ind + 1 + 4 + 4 * i]])
			numberOfFrame = float(a[0])
			#print numberOfFrame
			#print frame
			for region in regionprops(x1):
				if region.area < 50:
					continue
				i += 1
				y, x, y_end, x_end = region.bbox
				x = (x + x_end) / 2 - 24
				y = (y + y_end) / 2 - 24
				x_end = x + 48
				y_end = y + 48
				if x_end > video.size[0] - 1:
					x_end = video.size[0] - 1;
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
				color = (0, 0, 0)
				for rect in dict["fire"]:
					x0 = rect[0]
					x1 = rect[2]
					y0 = video.size[1] - rect[1]
					y1 = video.size[1] - rect[3]
					x0, y0, x1, y1 = bbox([x0, y0, x1, y1])
					cv.rectangle(temp_image, (x0, y0), (x1, y1), (0, 0, 255), 3)
					[t, square, x4, y4, x5, y5] = intersectionTwoRectangle([x0, y0, x1, y1], [x, y, x_end, y_end])
					#print t
					if t and square / float((x_end - x) * (y_end - y)) > 0.75:
						imsave(filename_fire + str(example_fire) + ".png", temp_image1[y:y_end, x:x_end, :])
						example_fire += 1
						color = (0, 0, 139)
						break
				if (color == (0, 0, 0)):
					for rect in dict["smoke"]:
						x0 = rect[0]
						x1 = rect[2]
						y0 = video.size[1] - rect[1]
						y1 = video.size[1] - rect[3]
						x0, y0, x1, y1 = bbox([x0, y0, x1, y1])
						cv.rectangle(temp_image, (x0, y0), (x1, y1), (255, 0, 0), 3)
						[t, square, x4, y4, x5, y5] = intersectionTwoRectangle([x0, y0, x1, y1], [x, y, x_end, y_end])
						#print t
						if t and square / float((x_end - x) * (y_end - y)) > 0.75:
							imsave(filename_smoke + str(example_smoke) + ".png", temp_image1[y:y_end, x:x_end, :])
							example_smoke += 1
							color = (255, 69, 0)
							break
				if (color == (0, 0, 0)):
					imsave(filename_none + str(example_none) + ".png", temp_image1[y:y_end, x:x_end, :])
					example_none += 1
					color = (0, 255, 0)
			#cv.rectangle(temp_image, (x, y), (x_end, y_end), color, 1)
			#print i
			#imsave("background/mean" + str(frame) +"____.png",temp1)
			#imsave("background/mean" + str(frame) +"_____.png", temp_image)
			imsave(filename_temp + str(frame) + ".png", temp_image)
			imsave(filename_temp + str(frame) + "_.png", temp_image1)
	print filename,"time", time.time() - start_time
	print filename, "fire", example_fire
	print filename, "smoke", example_smoke
	print filename, "none", example_none

path_to_data = '/home/sasha/Desktop/data/'

list_with_folders = ['freelance1/', 'freelance2/', 'freelance3/', 'freelance4/']
total_list = []
for folders in list_with_folders:
	for path, subdires, files in os.walk(path_to_data + folders):
		for one_file in files:
			if '.mp4' in one_file:
				temp = one_file[:one_file.rfind('.')] + '_label.txt'
				#print temp
				if os.path.exists(os.path.join(path, temp)):
					total_list.append(os.path.join(path, one_file))

print len(total_list)
pool = Pool(8)
pool.map(generate_images_from_one_video, total_list)
pool.close()
pool.join()
# generate_images_from_one_video('/home/sasha/Desktop/data/freelance3/bench11.mp4')
