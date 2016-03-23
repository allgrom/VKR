import os
import re
def check_fire_file(file_name):
	f = open(file_name)
	str = f.readline()
	while str != '':
		t1 = re.split('[,\s\[\]]', str)
		t = [x for i,x in enumerate(t1) if x != '']
		fire_ind = -1
		if 'fire' in t:
			fire_ind = t.index("fire")
		else:
			str = f.readline()
			continue
		if len(t) - fire_ind > 1 and t[fire_ind + 1] != 0 and t[fire_ind + 2] != 0 and t[fire_ind + 3] != 0 and t[fire_ind + 4] != 0:
			return True
		str = f.readline()
	return False


path_to_data = '/home/sasha/Desktop/data/'

list_with_folders = ['freelance1/', 'freelance2/', 'freelance3/']
total_list = []
for folders in list_with_folders:
	for path, sudires, files in os.walk(path_to_data + folders):
		for one_file in files:
			if '.txt' in one_file:
				total_list.append(os.path.join(path, one_file))

print total_list

print check_fire_file('bucket11_label.txt')

f = open('video_with_fire.txt', 'w')
for video in total_list:
	if check_fire_file(video):
		temp = video.replace("_label.txt", ".mp4")
		f.write(temp)
		f.write('\n')
f.close()