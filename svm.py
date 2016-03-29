from sklearn.svm import LinearSVC
from sklearn.externals import joblib
import numpy as np
import cPickle
name = "/home/sasha/Desktop/output/bench11/none/000001.fc6"
asdf = 22634
ar = np.zeros((asdf, 2), dtype = np.float32)
res = np.zeros((asdf), dtype = np.uint8)
def read_info(filename):
	f = open(filename)
	a = np.fromfile (f,dtype = np.int32, count = 5)
	t = a[0] * a[1] * a[2] * a[3] * a[4]
	a = np.fromfile(f, dtype = np.float32, count = t)
	f.close()
	return a
f = open("/home/sasha/c3d-test/examples/my_train/res12_add_smoke2/train_for_c3d1.txt")
for i in range(0, asdf):
	t1 = f.readline().split()
	t = t1[0].replace("data_for_3d_smoke_200_200","output") + "%06d.prob" % (int(t1[1]))
	ar[i,:] = read_info(t)
	res[i] = int(t1[2])
print "hey"
temp = LinearSVC()
temp.fit(ar, res)
print "heh"
joblib.dump(temp, "classify_prob.pkl")
