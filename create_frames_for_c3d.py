from moviepy.editor import *
from scipy.misc import imsave
import os
import time
from multiprocessing import Pool

count = 0
# for fold1 in os.listdir("."):
def create_for_one_video(fold):
	if os.path.isdir(fold):
		for fold1 in os.listdir(fold):
			if ".avi" in fold1:
				tim = time.time()
				filename = fold1[:fold1.rfind(".")]
				# print filename
				if not os.path.exists(fold + "/" + filename + "/"):
					os.makedirs(fold + "/" + filename + "/")
				if len(os.listdir(fold + "/" + filename + "/")) != 0:
					continue
				video = VideoFileClip(fold + "/" + fold1)
				for num in range(0, int(video.duration * video.fps)):
					imsave(fold + "/" + filename + "/%06d.jpg" % (num + 1), video.get_frame(num))
		print fold
total_list = []
path = "/home/sasha/Desktop/UCF-101/"
for fold in os.listdir(path):
	total_list.append(path + fold)
pool = Pool(4)
pool.map(create_for_one_video, total_list)
pool.close()
pool.join()
