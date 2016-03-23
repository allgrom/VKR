import os
import generate_images_for_3D
import time
from multiprocessing import Pool
path_to_data = "/home/sasha/Desktop/data/"
# folders = ['freelance1', 'freelance2', 'freelance3', 'freelance4']
folders = ['freelance1']
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
# path_to_save = '/home/sasha/Desktop/data_for_3d'
path_to_save = "video_with_label"
def generate_images_for_one_video(info):
	start = time.time()
	temp = generate_images_for_3D.Generate_Images_for_3D([100, 100], 2, path_to_save, info[1], info[0])
	print temp.step
	# temp.create_directories()
	if temp.create_directories() == None:
		print info[0]
		return
	temp.main_loop()
	print info[0],time.time() - start,temp.amount_sequence_fire,temp.amount_sequence_smoke,temp.amount_sequence_none
# for info in total_list:
# 	print info
# 	generate_images_for_one_video(info)
generate_images_for_one_video(["video_with_label/bucket11.mp4", "bucket11_label0.txt"])
# pool = Pool(4)
# pool.map(generate_images_for_one_video, total_list)
# pool.close()
# pool.join()