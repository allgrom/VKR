import re
from moviepy.editor import *
import os
from scipy.misc import imsave
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

	def main_loop(self):
		print self.video_name, self.video.duration
		random.seed()
		while (self.dict.get(self.frame, -1) != -1):
			# print self.frame
			for j in range(0, 1):
				p = True
				temp_count = 10
				while (p and temp_count != 0):
					# print "hey"
					center_x = random.randint(1 + self.image_size[0] / 2, self.video.size[0]- 1 - self.image_size[0] / 2)
					center_y = random.randint(1 + self.image_size[1] / 2, self.video.size[1]- 1 - self.image_size[1] / 2)
					# print center_x, center_y
					new_rect1 = [center_x - self.image_size[0]/ 2, center_y - self.image_size[1] / 2,
					            center_x + self.image_size[0] /2, center_y + self.image_size[1] / 2]
					check = 1
					for rect in self.dict[self.frame]["fire"]:
						if rect == [0, 0, 0, 0]:
							break
						x0, y0, x1, y1 = self.label_coordinate_2_video_coordinate(rect)
						rect_temp = [x0, y0, x1, y1]
						number1 = int(self.duration * self.video.fps) / self.step
						if self.intersectionTwoRectangle(new_rect1, rect_temp):
							check = 0
							break
						for i in range(1, number1 + 1):
							if self.dict.get(self.frame + i * self.step, -1) == -1:
								check = 0
								p = False
								break
							for new_rect in self.dict[self.frame + i * self.step]["fire"]:
								x0, y0, x1, y1 = self.label_coordinate_2_video_coordinate(new_rect)
								rect_temp = [x0, y0, x1, y1]
								if self.intersectionTwoRectangle(rect_temp, new_rect1):
									check = 0
									break
							if check == 0:
								break
					for rect in self.dict[self.frame]["smoke"]:
						if rect == [0, 0, 0, 0]:
							break
						x0, y0, x1, y1 = self.label_coordinate_2_video_coordinate(rect)
						rect_temp = [x0, y0, x1, y1]
						number1 = int(self.duration * self.video.fps) / self.step
						if self.intersectionTwoRectangle(new_rect1, rect_temp):
							check = 0
							break
						for i in range(1, number1 + 1):
							if self.dict.get(self.frame + i * self.step, -1) == -1:
								check = 0
								p = False
								break
							for new_rect in self.dict[self.frame + i * self.step]["smoke"]:
								x0, y0, x1, y1 = self.label_coordinate_2_video_coordinate(new_rect)
								rect_temp = [x0, y0, x1, y1]
								if self.intersectionTwoRectangle(rect_temp, new_rect1):
									check = 0
									break
							if check == 0:
								break
					if check == 1:
						self.cut_and_save([center_x, center_y], self.frame, "none" )
						p = False
					temp_count -= 1
			for rect in self.dict[self.frame]["fire"]:
				if rect == [0, 0, 0, 0]:
					break
				x0, y0, x1, y1 = self.label_coordinate_2_video_coordinate(rect)
				if (x1 - x0 <= self.image_size[0] and y1 - y0 <= self.image_size[1]):
					# print "one", self.frame
					center_x = x0 + (x1 - x0) / 2
					center_y = y0 + (y1 - y0) / 2
					# print center_x, center_y
					number = int(self.duration * self.video.fps) / self.step
					# print number
					temp_x = 0
					temp_y = 0
					check = 1
					diff_x = self.image_size[0] / 2 - (x1 - center_x)
					diff_y = self.image_size[1] / 2 - (y1 - center_y)
					for i in range(1, number + 1):
						if self.dict.get(self.frame + i * self.step, -1) == -1:
							check = 0
							break
						for new_rect in self.dict[self.frame + i * self.step]["fire"]:
							new_x0, new_y0, new_x1, new_y1 = self.label_coordinate_2_video_coordinate(new_rect)
							new_x = new_x0 + (new_x1 - new_x0) / 2
							new_y = new_y0 + (new_y1 - new_y0) / 2
							# print new_x, new_y
							if not self.intersectionTwoRectangle([x0, y0, x1, y1], [new_x0, new_y0, new_x1, new_y1]):
								continue
							temp_x += new_x - center_x
							temp_y += new_y - center_y
							break
						else:
							check = 0
						if (check == 0):
							break
					# print temp_x, temp_y

					if (check == 1):
						center_x = center_x + temp_x if abs(temp_x) < diff_x else center_x + diff_x
						center_y = center_y + temp_y if abs(temp_y) < diff_y else center_y + diff_y
						center = self.check_boundaries([center_x, center_y])
						self.cut_and_save(center, self.frame, "fire")
				else:
					# print "second", self.frame
					amount_x = int(math.ceil((x1 - x0) / float(self.image_size[0])))
					amount_y = int(math.ceil((y1 - y0) / float(self.image_size[1])))
					# print x0, y0, x1, y1
					if x1- x0 <= self.image_size[0]:
						amount_x = 0
						diff_x = 0
					else:
						diff_x = (amount_x * self.image_size[0] - (x1 - x0)) / (amount_x -  1)
					if y1 - y0 <= self.image_size[1]:
						amount_y = 0
						diff_y = 0
					else:
						diff_y = (amount_y * self.image_size[1] - (y1 - y0)) / (amount_y - 1)
					# print diff_x, diff_y
					check = 1
					print amount_x, amount_y, "fire"
					print x1 -x0, y1-y0
					for i in range(0, int(amount_x)):
						for j in range(0, int(amount_y)):
							center_x = x0 + i * self.image_size[0] - i * diff_x + self.image_size[0] / 2
							center_y = y0 + j * self.image_size[1] - j * diff_y + self.image_size[1] / 2
							# print center_x, center_y
							x0_temp = center_x - self.image_size[0] / 2
							x1_temp = center_x + self.image_size[0] / 2
							y0_temp = center_y - self.image_size[1] / 2
							y1_temp = center_y + self.image_size[1] / 2
							rect = [x0_temp, y0_temp, x1_temp, y1_temp]
							number = int(self.duration * self.video.fps) / self.step
							for k in range(1, number + 1):
								if self.dict.get(self.frame + i * self.step, -1) == -1:
									check = 0
									break
								for new_rect in self.dict[self.frame + i * self.step]["fire"]:
									new_x0, new_y0, new_x1, new_y1 = self.label_coordinate_2_video_coordinate(new_rect)
									new_x = (new_x1 - new_x0) / 2
									new_y = (new_y1 - new_y0) / 2
									if self.intersectionTwoRectangle(rect, [new_x0, new_y0, new_x1, new_y1]):
										break
								else:
									check = 0
								if (check == 0):
									break
							if (check == 1):
								center = self.check_boundaries([center_x, center_y])
								self.cut_and_save(center, self.frame, "fire")
			for rect in self.dict[self.frame]["smoke"]:
				if rect == [0, 0, 0, 0]:
					break
				print rect
				x0, y0, x1, y1 = self.label_coordinate_2_video_coordinate(rect)
				if (x1 - x0 <= self.image_size[0] and y1 - y0 <= self.image_size[1]):
					# print "one", self.frame
					center_x = x0 + (x1 - x0) / 2
					center_y = y0 + (y1 - y0) / 2
					# print center_x, center_y
					number = int(self.duration * self.video.fps) / self.step
					# print number
					temp_x = 0
					temp_y = 0
					check = 1
					diff_x = self.image_size[0] / 2 - (x1 - center_x)
					diff_y = self.image_size[1] / 2 - (y1 - center_y)
					for i in range(1, number + 1):
						if self.dict.get(self.frame + i * self.step, -1) == -1:
							check = 0
							break
						for new_rect in self.dict[self.frame + i * self.step]["smoke"]:
							new_x0, new_y0, new_x1, new_y1 = self.label_coordinate_2_video_coordinate(new_rect)
							new_x = new_x0 + (new_x1 - new_x0) / 2
							new_y = new_y0 + (new_y1 - new_y0) / 2
							# print new_x, new_y
							if not self.intersectionTwoRectangle([x0, y0, x1, y1], [new_x0, new_y0, new_x1, new_y1]):
								continue
							temp_x += new_x - center_x
							temp_y += new_y - center_y
							break
						else:
							check = 0
						if (check == 0):
							break
					# print temp_x, temp_y

					if (check == 1):
						center_x = center_x + temp_x if abs(temp_x) < diff_x else center_x + diff_x
						center_y = center_y + temp_y if abs(temp_y) < diff_y else center_y + diff_y
						center = self.check_boundaries([center_x, center_y])
						self.cut_and_save(center, self.frame, "smoke")
				else:
					# print "second", self.frame
					amount_x = int(math.ceil((x1 - x0) / float(self.image_size[0])))
					amount_y = int(math.ceil((y1 - y0) / float(self.image_size[1])))
					# print x0, y0, x1, y1
					if x1- x0 <= self.image_size[0]:
						amount_x = 0
						diff_x = 0
					else:
						diff_x = (amount_x * self.image_size[0] - (x1 - x0)) / (amount_x -  1)
					if y1 - y0 <= self.image_size[1]:
						amount_y = 0
						diff_y = 0
					else:
						diff_y = (amount_y * self.image_size[1] - (y1 - y0)) / (amount_y - 1)
					# print diff_x, diff_y
					check = 1
					print amount_x, amount_y, "smoke"
					print x1 -x0, y1-y0
					for i in range(0, int(amount_x)):
						for j in range(0, int(amount_y)):
							center_x = x0 + i * self.image_size[0] - i * diff_x + self.image_size[0] / 2
							center_y = y0 + j * self.image_size[1] - j * diff_y + self.image_size[1] / 2
							# print center_x, center_y
							x0_temp = center_x - self.image_size[0] / 2
							x1_temp = center_x + self.image_size[0] / 2
							y0_temp = center_y - self.image_size[1] / 2
							y1_temp = center_y + self.image_size[1] / 2
							rect = [x0_temp, y0_temp, x1_temp, y1_temp]
							number = int(self.duration * self.video.fps) / self.step
							for k in range(1, number + 1):
								if self.dict.get(self.frame + i * self.step, -1) == -1:
									check = 0
									break
								for new_rect in self.dict[self.frame + i * self.step]["smoke"]:
									new_x0, new_y0, new_x1, new_y1 = self.label_coordinate_2_video_coordinate(new_rect)
									new_x = (new_x1 - new_x0) / 2
									new_y = (new_y1 - new_y0) / 2
									if self.intersectionTwoRectangle(rect, [new_x0, new_y0, new_x1, new_y1]):
										break
								else:
									check = 0
								if (check == 0):
									break
							if (check == 1):
								center = self.check_boundaries([center_x, center_y])
								self.cut_and_save(center, self.frame, "smoke")

			number = (self.duration * self.video.fps) / self.step
			# if int(number) == 0:
			# 	self.frame += self.step
			# else:
			# 	self.frame += self.step * int(math.ceil(number))
			self.frame += self.step
			print self.frame



	def check_boundaries(self, center):
		if center[0] + self.image_size[0] / 2  > self.video.size[0] - 1:
			center[0] = self.video.size[0] -  1 - self.image_size[0]  / 2
		if center[0] - self.image_size[0] / 2 < 0:
			center[0] = self.image_size[0] / 2
		if center[1] + self.image_size[1] / 2 > self.video.size[1] - 1:
			center[1] = self.video.size[1] / 2 - 1 - self.image_size[1]
		if center[1] - self.image_size[1] / 2 < 0:
			center[1] = self.image_size[1] / 2
		return center

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
		for i in range(0, int(self.duration * self.video.fps)):
			frame = self.video.get_frame((start_frame + i) / float(self.video.fps))
			# imsave(path + type + str(number) + '_' + str(start_frame) + "_" + str(i) + ".png",
			imsave(path + "%06d.jpg" % (number * int(self.duration * self.video.fps) + i + 1),
				   frame[center[1] - self.image_size[1] / 2 :center[1] + self.image_size[1] / 2,
				   center[0] - self.image_size[0] / 2 : center[0] + self.image_size[0] / 2, :])

	def intersectionTwoRectangle(self, rect1, rect2):
		isIntersect = not (rect1[2] < rect2[0] or rect1[3] < rect2[1] or rect2[2] < rect1[0] or rect2[3] < rect1[1])
		return isIntersect



if __name__ == "__main__":
	start = time.time()
	test = Generate_Images_for_3D([50, 50], 2, "test", "bucket11_label.txt", "bucket11.mp4")
	test.main_loop()
	print time.time() - start
	print test.amount_sequence_fire
	print test.amount_sequence_smoke