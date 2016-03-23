import re
from moviepy.editor import *
import os
from scipy.misc import imsave, imresize
import math
import cv2 as cv
import time
import random


class Generate_Images_for_3D:
	def __init__(self, size_of_images, duration, path_to_save, file_with_label, video_file):
		# size of image tuple (height, width)
		self.image_size = size_of_images
		# duration of one frame sequence
		self.duration = duration
		self.path_to_save = path_to_save
		# file with label
		# content of this file - 1000 smoke  fire [310.0, 253.0, 367.0, 156.99999999999997]
		# 1000 - frame number, after smoke and fire zero or more rectangles
		self.file = file_with_label
		self.video_name = video_file
		self.video = VideoFileClip(video_file)
		self.frame = 0
		self.dict = self.get_info_from_file()
		self.step = self.get_step_of_label()
		self.amount_sequence_fire = 0
		self.amount_sequence_smoke = 0
		self.amount_sequence_none = 0


	def create_directories(self):
		name = ""
		if self.video_name.rfind('/') == -1:
			name = self.video_name[:self.video_name.rfind('.')]
		else:
			name = self.video_name[self.video_name.rfind("/") + 1:self.video_name.rfind('.')]

		self.path_to_smoke = self.path_to_save + '/' + name + '/smoke/'
		self.path_to_fire = self.path_to_save + '/' + name + '/fire/'
		self.path_to_none= self.path_to_save + '/' + name + '/none/'
		if not os.path.exists(self.path_to_smoke):
			os.makedirs(self.path_to_smoke)
		else:
			return None
		if not os.path.exists(self.path_to_fire):
			os.makedirs(self.path_to_fire)
		if not os.path.exists(self.path_to_none):
			os.makedirs(self.path_to_none)
		return 1

	def get_info_from_file(self):
		dict = {}
		with open(self.file) as f:
			str = f.readline()
			while str != '':
				str_split = self.split_string(str)
				info = self.get_info_from_one_line(str_split)
				if info != None:
					dict[int(str_split[0])] = info
				str = f.readline()
		return dict

	def split_string(self, str):
		pattern = re.compile('\[|\]|,')
		return re.sub(pattern, ' ', str).split()

	def get_info_from_one_line(self, str):
		if not "fire" in str:
			return None
		smoke_ind = str.index("smoke")
		fire_ind = str.index("fire")
		dict = {}
		dict["smoke"] = []
		dict["fire"] = []
		if (fire_ind - smoke_ind != 1):
			for i in range(0, (fire_ind - smoke_ind) / 4):
				dict["smoke"].append([int(float(k)) for k in str[smoke_ind + 1 + 4 * i: smoke_ind + 1 + 4 + 4 * i]])
		if (len(str) - fire_ind != 1):
			for i in range(0, (len(str) - fire_ind) / 4):
				dict["fire"].append([int(float(k)) for k in str[fire_ind + 1 + 4 * i: fire_ind + 1 + 4 + 4 * i]])
		return dict

	def get_step_of_label(self):
		with open(self.file) as f:
			str = f.readline()
			step = -1
			while str != '':
				str_split = self.split_string(str)
				info = self.get_info_from_one_line(str_split)
				if info != None:
					if step == -1:
						step = int(str_split[0])
					else:
						return int(str_split[0]) - step
				str = f.readline()
		return None

	def label_coordinate_2_video_coordinate(self, rect):
		x0 = rect[0]
		x1 = rect[2]
		y0 = self.video.size[1] - rect[1]
		y1 = self.video.size[1] - rect[3]
		return min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)
	def generate_empty(self, amount):
		for i in range(0, amount):
			amount_of_attempt = 10
			while (amount_of_attempt != 0):
				center_x = random.randint(1 + self.image_size[0] / 2, self.video.size[0]- 1 - self.image_size[0] / 2)
				center_y = random.randint(1 + self.image_size[1] / 2, self.video.size[1]- 1 - self.image_size[1] / 2)
				rect = [center_x - self.image_size[0]/ 2, center_y - self.image_size[1] / 2,
					            center_x + self.image_size[0] /2, center_y + self.image_size[1] / 2]
				if not self.check_intersection(rect):
					break
				else:
					amount_of_attempt -= 1
			if amount_of_attempt > 0:
				self.cut_and_save([center_x - self.image_size[0] / 2, center_y - self.image_size[0] / 2,
				                  center_x + self.image_size[0] / 2, center_y + self.image_size[0] / 2 ], self.frame, "none")

	def check_intersection(self, rect):
		for type in ["fire", "smoke"]:
			for rect1 in self.dict[self.frame][type]:
				if rect1 == [0, 0, 0, 0]:
					continue
				x0, y0, x1, y1 = self.label_coordinate_2_video_coordinate(rect)
				rect_temp = [x0, y0, x1, y1]
				number1 = int(self.duration * self.video.fps) / self.step
				if self.intersectionTwoRectangle(rect, rect_temp):
					return True
		return False
	def main_loop(self):
		print self.video_name, self.video.duration
		random.seed()
		while (self.dict.get(self.frame, -1) != -1):
			self.generate_empty(1)
			for type in ["smoke"]:
				for rect in self.dict[self.frame][type]:
					if rect == [0, 0, 0, 0]:
						continue
					x0, y0, x1, y1 = self.label_coordinate_2_video_coordinate(rect)
					new_rect = [x0, y0, x1, y1]
					self.cut_and_save(new_rect, self.frame, "smoke")
			self.frame += self.step
			print self.frame

	def cut_and_save(self, center, start_frame, type):
		number = 0
		if type == "fire":
			path = self.path_to_fire
			number = self.amount_sequence_fire
			self.amount_sequence_fire += 1
		elif type == "smoke":
			path = self.path_to_smoke
			number = self.amount_sequence_smoke
			self.amount_sequence_smoke += 1
		else:
			path = self.path_to_none
			number = self.amount_sequence_none
			self.amount_sequence_none += 1
		if self.video.duration * self.video.fps < self.frame + 25:
			return
		for i in range(0, int(self.duration * self.video.fps)):
			frame = self.video.get_frame((start_frame + i) / float(self.video.fps))
			frame1 = frame[center[1]:center[3], center[0]:center[2]]
			if frame1.shape[0] == 0 or frame1.shape[1] == 0:
				if type == "smoke":
					self.amount_sequence_smoke -= 1
				if type == "none":
					self.amount_sequence_none -= 1
				return
			frame1 = imresize(frame1, (100, 100))
			imsave(path + "%06d.jpg" % (number * int(self.duration * self.video.fps) + i + 1), frame1)

	def intersectionTwoRectangle(self, rect1, rect2):
		isIntersect = not (rect1[2] < rect2[0] or rect1[3] < rect2[1] or rect2[2] < rect1[0] or rect2[3] < rect1[1])
		return isIntersect

from multiprocessing import Pool
path_to_data = "/home/sasha/Desktop/data/"
# folders = ['freelance1', 'freelance2', 'freelance3', 'freelance4']
folders = ['freelance3', 'freelance1', 'freelance2']
total_list_video = []
total_list_label = []
total_list = []
for folders in folders:
	for path, subdires, files in os.walk(path_to_data + folders):
		for one_file in files:
			if '.mp4' in one_file:
				temp = one_file[:one_file.rfind('.')] + '_label.txt'
				#print temp
				if os.path.exists(os.path.join(path, temp)):
					total_list_video.append(os.path.join(path, one_file))
					total_list_label.append(os.path.join(path, temp))
					total_list.append([os.path.join(path, one_file), os.path.join(path, temp)])

# path_to_save = "/home/sasha/Desktop/data_for_3d"
path_to_save = '/home/sasha/Desktop/data_for_3d_smoke'
def generate_images_for_one_video(info):
	start = time.time()
	temp = Generate_Images_for_3D([100, 100], 1, path_to_save, info[1], info[0])
	print temp.step
	# temp.create_directories()
	if temp.create_directories() == None:
		print info[0]
		return
	temp.main_loop()
	print info[0],time.time() - start,temp.amount_sequence_fire,temp.amount_sequence_smoke,temp.amount_sequence_none
# for info in total_list:
# 	if "bench" in info[0]:
# 		print info
# 		generate_images_for_one_video(info)
pool = Pool(9)
pool.map(generate_images_for_one_video, total_list)
pool.close()
pool.join()