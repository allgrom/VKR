from moviepy.editor import *
from scipy.misc import imsave,imread
import cv2 as cv
import numpy as np
video = VideoFileClip("bucket11.mp4")
t = video.get_frame(1)
imsave("temp.jpg", t.astype(np.uint8))
imsave("temp1.png", t.astype(np.uint8))
print t[0,0,:]

print cv.imread("temp.jpg")[0,0,:]
print cv.imread("temp.jpg", cv.IMREAD_UNCHANGED)[0,0,:]
p = imread("temp.jpg")
print p.dtype