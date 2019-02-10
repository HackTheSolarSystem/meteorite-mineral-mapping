from numba import cuda
from numba import *
import numpy as np
from PIL import Image
import json

@cuda.jit
def map_nonzero(inImage, outImage):
	for x in range(0, width):
		for y in range(0, height):
			if inImage[y,x] != 0:
				outImage[y,x] = 1
			else:
				outImage[y,x] = 0

@cuda.jit
def map_mask(inImage, maskImage, outImage):
	for x in range(0, width):
		for y in range(0, height):
			if maskImage[y,x] != 0:
				outImage[y,x] = inImage[y,x]
			else:
				outImage[y,x] = 0

@cuda.reduce
def sum_reduce(a, b):
	return a+b

with open("standards.json", 'r') as f:
	standards_dict = json.load(f)


width = 0
height = 0

elements = standards_dict["elements"]
minerals = standards_dict["minerals"]

element_dimages = {}

for element in elements:
	img = Image.open(elements[element])
	element_dimages[element] = cuda.to_device(img)
	width = img.width
	height = img.height

maskBuf = np.zeros((height, width), dtype = np.int32)
device_maskBuf = cuda.to_device(maskBuf)

for mineral in minerals:
	maskImg = Image.open(minerals[mineral]["maskFile"]);
	maskDImage = cuda.to_device(maskImg)

	map_nonzero(maskDImage, device_maskBuf)
	maskpixels = sum_reduce(np.ravel(device_maskBuf))
	minerals[mineral]["intensity"] = {}
	print(mineral)
	for element in elements:
		map_mask(element_dimages[element], maskDImage, device_maskBuf)
		elemTotalIntensity = sum_reduce(np.ravel(device_maskBuf))
		elemAverageIntensity = elemTotalIntensity / maskpixels
		minerals[mineral]["intensity"][element] = elemAverageIntensity
		print("\t" + element + ": " + str(elemAverageIntensity))