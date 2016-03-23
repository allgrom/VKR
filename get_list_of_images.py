import os
path_to_data = "/home/sasha/Desktop/data/"
folders = ['freelance1', 'freelance2', 'freelance3', 'freelance4']
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
