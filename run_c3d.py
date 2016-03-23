#!/usr/bin/env python

'''
A sample script to run c3d classifications on multiple videos
'''

import os
import numpy as np
import sys
sys.path.append("/home/sasha/C3d_python/python")
import caffe
from c3d_classify import c3d_classify

# UCF101 categories

def main():

	# model
	model_def_file = '/home/sasha/C3d_python/examples/c3d_train_ucf101/deploy.prototxt'
	model_file = '/home/sasha/C3d_python/examples/c3d_train_ucf101/conv3d_ucf101_iter_5000'
	mean_file = '/home/sasha/C3d_python/examples/c3d_train_ucf101/mean.binaryproto'
	net = caffe.Net(model_def_file, model_file)
	print net.blobs['prob'].data.shape[1]

	# caffe init
	gpu_id = 0
	net.set_device(gpu_id)
	net.set_mode_gpu()
	net.set_phase_test()

	blob = caffe.proto.caffe_pb2.BlobProto()
	data = open(mean_file,'rb').read()
	blob.ParseFromString(data)
	image_mean = np.array(caffe.io.blobproto_to_array(blob))

	f = open("/home/sasha/C3d_python/examples/c3d_train_ucf101/test.txt")
	str = f.readline()
	info = str.split()
	print info
	count = 0
	count_true = 0
	rgb = (100,100, 3, 4)
	while info != []:
		prediction = c3d_classify(
				vid_name=info[0],
				image_mean=image_mean,
				net=net,
				start_frame=int(info[1]),
				prob_layer='prob'
				)
		print prediction
		result = int(prediction.argmax())
		count +=1
		if (count % 100 == 0):
			print count
		if result == int(info[2]):
			count_true += 1
		str = f.readline()
		info = str.split()
	print float(count_true) / count * 100

if __name__ == "__main__":
	main()