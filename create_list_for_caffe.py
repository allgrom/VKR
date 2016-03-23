import os
path_to_data = "/home/sasha/Desktop/data/"
folders = ['freelance1', 'freelance2', 'freelance3', 'freelance4']
from random import shuffle
# folders = ['freelance4']
total_list = []
for folders in folders:
	for path, subdires, files in os.walk(path_to_data + folders):
		for one_file in files:
			if '.mp4' in one_file:
				temp = one_file[:one_file.rfind('.')] + '_label.txt'
				#print temp
				if os.path.exists(os.path.join(path, temp)):
					total_list.append(os.path.join(path, one_file))
smoke = 0
fire = 0
none = 0
for video in total_list:
	folder = video[:video.rfind('.')]
	smoke += len(os.listdir(folder + '/smoke'))
	fire += len(os.listdir(folder + '/fire'))
	none += len(os.listdir(folder + '/none'))
print smoke
print fire
print none

def add_all_files_to_list(path_to_dir, list):
	for files in os.listdir(path_to_dir):
		list.append(path_to_dir + files)

smoke_train = []
smoke_test = []
fire_train = []
fire_test = []
none_train = []
none_test = []
for video in total_list:
	folder = video[:video.rfind('.')]
	if len(smoke_train) < 4 * len(smoke_test):
		add_all_files_to_list(folder + '/smoke/', smoke_train)
	else:
		add_all_files_to_list(folder + '/smoke/', smoke_test)
	if len(fire_train) < 4 * len(fire_test):
		add_all_files_to_list(folder + '/fire/', fire_train)
	else:
		add_all_files_to_list(folder + '/fire/', fire_test)
	if len(none_train) < 4 * len(none_test) and 'freelance4' in folder:
		add_all_files_to_list(folder + '/none/', none_train)
		continue
	if len(none_train) >= 4 * len(none_test) and 'freelance4' in folder:
		add_all_files_to_list(folder + '/none/', none_test)
		continue
print len(smoke_train)
print len(smoke_test)
print len(fire_test)
print len(fire_train)
print len(none_train)
print len(none_test)

k = (smoke + fire) / float(none)
shuffle(none_train)
shuffle(none_test)

# none_train = none_train[:int(2 * k * len(none_train))]
# none_test = none_test[:int(2 * k * len(none_test))]
none_train = none_train[:len(smoke_train)]
none_test = none_test[:len(smoke_test)]
print len(none_train)
print len(none_test)

f = open("train.txt", 'w')
f_test = open('test.txt', 'w')
for files in smoke_train:
	f.write(files.replace('home/', '') + " 1\n")
for files in fire_train:
	f.write(files.replace('home/', '') + " 2\n")
for files in none_train:
	f.write(files.replace('home/', '') + " 0\n")
for files in smoke_test:
	f_test.write(files.replace('home/', '') + " 1\n")
for files in fire_test:
	f_test.write(files.replace('home/', '') + " 2\n")
for files in none_test:
	f_test.write(files.replace('home/', '') + " 0\n")