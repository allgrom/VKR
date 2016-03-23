import os
from random import shuffle
length = 4
sampling_rate = 4
size = 50

label = 0
# path_to_save = '/media/sasha/Seagate/data_for_3d'
path_to_save = '/home/sasha/Desktop/data_for_3d'
total_fire_train = 0
total_fire_test = 0
total_none_train = 0
total_none_test = 0
total_smoke_test = 0
total_smoke_train = 0
none_train = []
fire_train = []
none_test = []
fire_test = []
smoke_test = []
smoke_train = []
t = os.listdir(path_to_save)
shuffle(t)
count12 = 0
glob_size = 1000000
print len(t)
for video in t:
	# if "yard" in video:
	# 	continue
	if not ("bucket" in video or "door" in video or "fire" in video
	        or "roomfire" in video or "roomsmoke" in video) or  "officebucket" in video:
		continue
	count12 += 1
	print video
	# if not "bucket11" in video:
	# 	continue
	# print video
	# print len(os.listdir(path_to_save + '/' + video + '/fire'))
	number = len(os.listdir(path_to_save + '/' + video + '/fire')) / size
	count = size / (length * sampling_rate)
	if (len(fire_train) < glob_size):
		if (len(fire_train) > 4 * len(fire_test)):
			for number1 in range(0, number):
				for number2 in range(0, count):
					# f.write("%s/%s/fire/ %d %d\n" % (path_to_save, video, number1 * size + 1 + number2 * sampling_rate * length,0))
					fire_test.append([path_to_save, video, number1 * size + 1 + number2 * sampling_rate * length, 0])
					total_fire_test += 1
		else:
			for number1 in range(0, number):
				for number2 in range(0, count):
					# f.write("%s/%s/fire/ %d %d\n" % (path_to_save, video, number1 * size + 1 + number2 * sampling_rate * length,0))
					fire_train.append([path_to_save, video, number1 * size + 1 + number2 * sampling_rate * length, 0])
					total_fire_train += 1
	number = len(os.listdir(path_to_save + '/' + video + '/none')) / size
	if (len(none_train) < glob_size):
		if (len(none_train) > 4 * len(none_test)):
			for number1 in range(0, number):
				for number2 in range(0, count):
					# f.write("%s/%s/fire/ %d %d\n" % (path_to_save, video, number1 * size + 1 + number2 * sampling_rate * length,0))
					none_test.append([path_to_save, video, number1 * size + 1 + number2 * sampling_rate * length, 1])
					total_none_test += 1
		else:
			for number1 in range(0, number):
				for number2 in range(0, count):
					# f.write("%s/%s/fire/ %d %d\n" % (path_to_save, video, number1 * size + 1 + number2 * sampling_rate * length,0))
					none_train.append([path_to_save, video, number1 * size + 1 + number2 * sampling_rate * length, 1])
					total_none_train += 1
	number = len(os.listdir(path_to_save + '/' + video + '/smoke')) / size

	if (len(smoke_train) < glob_size):
		if (len(smoke_train) > 4 * len(smoke_test)):
			for number1 in range(0, number):
				for number2 in range(0, count):
					# f.write("%s/%s/fire/ %d %d\n" % (path_to_save, video, number1 * size + 1 + number2 * sampling_rate * length,0))
					smoke_test.append([path_to_save, video, number1 * size + 1 + number2 * sampling_rate * length, 2])
					total_smoke_test += 1
		else:
			for number1 in range(0, number):
				for number2 in range(0, count):
					# f.write("%s/%s/fire/ %d %d\n" % (path_to_save, video, number1 * size + 1 + number2 * sampling_rate * length,0))
					smoke_train.append([path_to_save, video, number1 * size + 1 + number2 * sampling_rate * length, 2])
					total_smoke_train += 1
print total_fire_train
print total_fire_test
print total_none_train
print total_none_test

print total_smoke_train
print total_smoke_test
print total_fire_train + total_none_train + total_smoke_train
print count12
f = open("/home/sasha/train_for_c3d1.txt", 'w')
f1 = open('/home/sasha/test_for_c3d1.txt', 'w')
for info in fire_test:
	f1.write("%s/%s/fire/ %d %d\n" % (info[0], info[1],info[2], info[3]))

for info in none_test:
	f1.write("%s/%s/none/ %d %d\n" % (info[0], info[1],info[2], info[3]))

for info in fire_train:
	f.write("%s/%s/fire/ %d %d\n" % (info[0], info[1],info[2], info[3]))

for info in none_train:
	f.write("%s/%s/none/ %d %d\n" % (info[0], info[1],info[2], info[3]))
for info in smoke_train:
	f.write("%s/%s/smoke/ %d %d\n" % (info[0], info[1],info[2], info[3]))
for info in smoke_test:
	f1.write("%s/%s/smoke/ %d %d\n" % (info[0], info[1],info[2], info[3]))


