import numpy as np
import caffe
import cv2 as cv
import time
from c3d_classify import c3d_classify

test_file = '/home/sasha/C3d_python/examples/c3d_train_ucf101/test_for_c3d1.txt'
model_def_file = '/home/sasha/C3d_python/examples/c3d_train_ucf101/deploy.prototxt'
model_file = '/home/sasha/C3d_python/examples/c3d_train_ucf101/conv3d_ucf101_iter_3000'
mean_file = '/home/sasha/C3d_python/examples/c3d_train_ucf101/mean.binaryproto'
net = caffe.Net(model_def_file, model_file)

gpu_id = 0
net.set_device(gpu_id)
net.set_mode_gpu()
net.set_phase_test()

blob = caffe.proto.caffe_pb2.BlobProto()
data = open(mean_file,'rb').read()
blob.ParseFromString(data)
image_mean = np.array(caffe.io.blobproto_to_array(blob))

f = open(test_file, 'r')
str1 = f.readline()
str1 = str1.split()
frame_info = np.zeros((100, 100, 3, 4), dtype = np.uint8)
false = 0
total = 0
while str1 != []:
	for j in range(0, 4):
		frame_info[:,:,:,j] = cv.imread(str1[0] + "/%06d.jpg" %(int(str1[1]) + j *5), cv.IMREAD_UNCHANGED)
	prediction = c3d_classify(
				images= frame_info,
				image_mean=image_mean,
				net=net,
				prob_layer='prob'
				)
	res_cnn = int(prediction.argmax())
	if (res_cnn != int(str1[2])):
		false += 1
	total += 1
	if total %200 == 0:
		print total
	str1 = f.readline().split()
print total
print false / float(total)