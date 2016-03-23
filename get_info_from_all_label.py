import numpy as np
import re
import pylab
import os
class Label_info:
	def __init__(self, path_to_all_labels):
		self.path_to_data = path_to_all_labels
		self.info_fire_height = np.zeros((720))
		self.info_fire_width = np.zeros((1280))
		self.info_smoke_height = np.zeros((720))
		self.info_smoke_width = np.zeros((1280))
	def main_loop(self):
		count = 0
		for label in self.path_to_data:
			print count
			count += 1
			frame = 0
			step = self.get_step_of_label(label)
			dict = self.get_info_from_file(label)
			while dict.get(frame, -1) != -1:
				for type in ['fire', 'smoke']:
					for rect in dict[frame][type]:
						if rect == [0, 0, 0, 0]:
							continue
						width = abs(rect[2] - rect[0])
						height = abs(rect[3] - rect[1])
						if type == 'fire':
							self.info_fire_height[height] += 1
							self.info_fire_width[width] += 1
						else:
							self.info_smoke_height[height] += 1
							self.info_smoke_width[width] += 1
				frame += step
		height_fire = np.arange(720)
		width_smoke = np.arange(1280)
		height_smoke = np.arange(720)
		width_fire = np.arange(1280)
		f = pylab.figure()
		ax = f.add_axes([0.1,0.1, 0.8, 0.8])
		ax.bar(height_fire, self.info_fire_height)
		f.savefig("fire_height.png")
		f = pylab.figure()
		ax = f.add_axes([0.1,0.1, 0.8, 0.8])
		ax.bar(width_fire, self.info_fire_width)
		f.savefig("fire_width.png")
		f = pylab.figure()
		ax = f.add_axes([0.1,0.1, 0.8, 0.8])
		ax.bar(height_smoke, self.info_smoke_height)
		f.savefig("smoke_height.png")
		f = pylab.figure()
		ax = f.add_axes([0.1,0.1, 0.8, 0.8])
		ax.bar(width_smoke, self.info_smoke_width)
		f.savefig("smoke_width.png")


	def get_step_of_label(self, file):
		with open(file) as f:
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
	def get_info_from_file(self,file):
		dict = {}
		with open(file) as f:
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
t = Label_info(total_list_label)
t.main_loop()
