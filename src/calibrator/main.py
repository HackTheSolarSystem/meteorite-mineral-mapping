from numba import cuda
from numba import *
import numpy as np
from PIL import Image
import json

with open("standards.json", 'r') as f:
	standards_dict = json.load(f)

elem_names = []
elem_images = []
elem_dimages = []

width = 0
height = 0

elements = standards_dict["elements"]

for element in elements:
	img = Image.open(elements[element])
	elem_names.append(element)
	elem_images.append(img)
	elem_dimages.append(cuda.to_device(img))
	width = img.width
	height = img.height


maskBuf = np.zeros((height, width), dtype = np.int32)
device_maskBuf = cuda.to_device(maskBuf)

@cuda.jit
def map_nonzero(inImage, outImage):
	for x in range(0, width):
		for y in range(0, height):
			if inImage[y,x] != 0:
				outImage[y,x] = 1
			else:
				outImage[y,x] = 0

@cuda.reduce
def sum_reduce(a, b):
	return a+b

testmin = standards_dict["minerals"]["iron"]
testMinMaskImage = Image.open(testmin["maskFile"])

dTestMin = cuda.to_device(testMinMaskImage)

map_nonzero(dTestMin, device_maskBuf)
maskpixels = sum_reduce(np.ravel(device_maskBuf))

print(maskpixels)