import os
from scipy.misc import imread, imsave
import numpy as np
f = open("/home/sasha/c3d-test/examples/my_train/res11_move_in_b/train_for_c3d1.txt", 'r')
path_to_save = '/home/sasha/Desktop/data_for_3d_smoke_ground_with_move/'
t = f.readline().split()
def rgb2gray(rgb):
	return np.dot(rgb[...,:3], [0.299, 0.587, 0.144])
while t != []:
	if not (os.path.exists(t[0] + "%06d.jpg" % int(t[1])) and
		os.path.exists(t[0] + "%06d.jpg" % (int(t[1]) + 5)) and
		os.path.exists(t[0] + "%06d.jpg" % (int(t[1]) + 10)) and
		os.path.exists(t[0] + "%06d.jpg" % (int(t[1]) + 15))):
		print t[0], t[1], t[2]
	new = t[0].replace("data_for_3d_smoke", "data_for_3d_smoke_ground")
	a = np.zeros((100, 100, 3))
	mean_r = np.zeros((100, 100, 4))
	mean_g = np.zeros((100, 100, 4))
	mean_b = np.zeros((100, 100, 4))
	for i in range(0, 4):
		# print a[1,1,:]
		# a += imread(t[0] + "%06d.jpg" % (int(t[1]) + i * 5))
		mean_r[:,:,i] = imread(t[0] + "%06d.jpg" % (int(t[1]) + i * 5))[:,:,0]
		mean_g[:,:,i] = imread(t[0] + "%06d.jpg" % (int(t[1]) + i * 5))[:,:,1]
		mean_b[:,:,i] = imread(t[0] + "%06d.jpg" % (int(t[1]) + i * 5))[:,:,2]
	# a /= 4
	temp = np.dstack((np.median(mean_r, axis = 2), np.median(mean_g, axis = 2), np.median(mean_b, axis = 2)))
	# imsave(new + "background.jpg", temp)
	if not os.path.exists(new[:new.rfind('/')]):
		os.makedirs(new[:new.rfind('/')])
	for j in range(0, 4):
		py = np.zeros((100, 100, 3))
		py = imread(t[0] + "%06d.jpg" % (int(t[1]) + j * 5))
		imsave(new + "%06d.jpg" % (int(t[1]) + j * 5), np.abs(py - temp))
		# imsave("temp.jpg", t)
	t = f.readline().split()



