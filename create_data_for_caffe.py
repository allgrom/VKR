import subprocess
import os

import numpy as np
import sys
import caffe


def create_lmdb_train():
	f = open('create_train.sh', 'w')

	path_to_data = "/home"
	path_to_test_data = '/home/sasha/caffe/train_lmdb'
	f.write('GLOG_logtostderr=1 /home/sasha/caffe/build/tools/convert_imageset --resize_height=32 --resize_width=32 --shuffle '
	        '%s train.txt %s' %(path_to_data, path_to_test_data))
	f.close()
	os.chmod('create_train.sh', 0744)
	# subprocess.Popen(['sh', './create_test.sh'])
	output = subprocess.Popen(["sh", "./create_train.sh"], stdout=subprocess.PIPE).communicate()[0]
	print output
def create_lmdb_test():
	f = open('create_test.sh', 'w')

	path_to_data = "/home"
	path_to_test_data = '/home/sasha/caffe/test_lmdb'
	f.write('GLOG_logtostderr=1 /home/sasha/caffe/build/tools/convert_imageset --resize_height=32 --resize_width=32 --shuffle '
	        '%s test.txt %s' %(path_to_data, path_to_test_data))
	f.close()
	os.chmod('create_test.sh', 0744)
	# subprocess.Popen(['sh', './create_test.sh'])
	output = subprocess.Popen(["sh", "./create_test.sh"], stdout=subprocess.PIPE).communicate()[0]
	print output
def create_mean():
	file_name = 'create_image_mean.sh'
	f = open(file_name, 'w')
	path_to_lmdb = '/home/sasha/caffe/train_lmdb'
	path_to_mean = '/home/sasha/caffe/mean.binaryproto'
	f.write('/home/sasha/caffe/build/tools/compute_image_mean %s %s' %(path_to_lmdb, path_to_mean))
	f.close()
	os.chmod(file_name, 0744)
	output = subprocess.Popen(["sh", './' + file_name], stdout=subprocess.PIPE).communicate()[0]
	print output
def convert():
	blob = caffe.proto.caffe_pb2.BlobProto()
	path_to_mean = '/home/sasha/caffe/mean.binaryproto'
	path_to_res = '/home/sasha/caffe/mean.npy'
	data = open(path_to_mean , 'rb' ).read()
	blob.ParseFromString(data)
	arr = np.array( caffe.io.blobproto_to_array(blob) )
	out = arr[0]
	np.save( path_to_res , out)
create_lmdb_train()
create_lmdb_test()
create_mean()
convert()