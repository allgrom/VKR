from moviepy.editor import *
import os
import re
import cv2 as cv
from scipy.misc import imsave
import shutil
import time
class Draw_Label_on_Video:
	def __init__(self, path_to_label, path_to_video, path_to_save):
		self.path_to_label = path_to_label
		self.path_to_video = path_to_video
		self.save = path_to_save
		self.temp_dir = "temp_for_draw/"
	def make_temp_dir(self):
		if not os.path.exists(self.temp_dir):
			os.makedirs(self.temp_dir)

	def get_info_from_file(self):
		dict = {}
		with open(self.path_to_label) as f:
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
		with open(self.path_to_label) as f:
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

	# def draw_label(self):
	# 	while (self.dict.get(self.frame, -1) != -1):
	# 		for i in range(0, self.step):
	# 			frame = self.video.get_frame((self.frame + i) / float(self.video.fps))
	# 			for rect in self.dict[self.frame]["fire"]:
	# 				if rect == [0, 0, 0, 0]:
	# 					continue
	# 				x0, y0, x1, y1 = self.label_coordinate_2_video_coordinate(rect)
	# 				cv.rectangle(frame, (x0, y0), (x1, y1), color=(255, 0, 0), thickness= 2)
	# 			for rect in self.dict[self.frame]["smoke"]:
	# 				if rect == [0, 0, 0, 0]:
	# 					continue
	# 				x0, y0, x1, y1 = self.label_coordinate_2_video_coordinate(rect)
	# 				cv.rectangle(frame, (x0, y0), (x1, y1), color=(0, 0, 255), thickness= 2)
	# 			imsave(self.temp_dir + "%06d.png" % (self.image), frame)
	# 			self.image += 1
	# 		self.frame += self.step
	def draw_label(self):
		while (self.dict.get(self.frame, -1) != -1):
			list_with_rectangles = []
			for rect in self.dict[self.frame]["fire"]:
				if rect == [0, 0, 0, 0]:
					continue
				x0, y0, x1, y1 = self.label_coordinate_2_video_coordinate(rect)
				list_with_rectangles.append([(x0, y0), (x1, y1), (255, 0, 0), 2])
			for rect in self.dict[self.frame]["smoke"]:
				if rect == [0, 0, 0, 0]:
					continue
				x0, y0, x1, y1 = self.label_coordinate_2_video_coordinate(rect)
				list_with_rectangles.append([(x0, y0), (x1, y1), (0, 0, 255), 2])
			for i in range(0, self.step):
				frame = self.video.get_frame((self.frame + i) / float(self.video.fps))
				for info in list_with_rectangles:
					cv.rectangle(frame, info[0], info[1], info[2], info[3])
				imsave(self.temp_dir + "%06d.png" % (self.image), frame)
				self.image += 1
			if self.image % 750 == 0:
				print self.image
			self.frame += self.step

	def main_loop(self):
		self.dict = self.get_info_from_file()
		self.step = self.get_step_of_label()
		self.make_temp_dir()
		self.frame = 0
		self.image = 0
		self.video = VideoFileClip(self.path_to_video)
		print self.video.duration * self.video.fps
		self.draw_label()
		self.create_video()
		shutil.rmtree(self.temp_dir)
	def create_video(self):
		myClip = ImageSequenceClip(self.temp_dir, fps = self.video.fps)
		index = self.path_to_video.rfind("/")
		ext = self.path_to_video[self.path_to_video.rfind("."):]
		if (index == -1):
			name = self.path_to_video[:self.path_to_video.rfind(".")] + "_label" + ext
		else:
			name = self.path_to_video[self.path_to_video.rfind("/") + 1 : self.path_to_video.rfind(".")] + "_label" + ext
		myClip.write_videofile(self.save + name)
if __name__ == "__main__":

	# Label = Draw_Label_on_Video("bucket11_label.txt", "bucket11.mp4", "")
	# Label.main_loop()
	# exit()
	path_to_data = "/home/sasha/Desktop/data/"
	# folders = ['freelance1', 'freelance2', 'freelance3', 'freelance4']
	folders = [ 'freelance2']
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
	print len(total_list)
	print total_list
	for info in total_list:
		start = time.time()
		print info[0]
		Label = Draw_Label_on_Video(info[1], info[0], "video_with_label/")
		Label.main_loop()
		print time.time() - start
