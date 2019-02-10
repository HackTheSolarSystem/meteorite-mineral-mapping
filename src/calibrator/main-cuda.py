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

with open("standard/standards.json", 'r') as f:
	standards_dict = json.load(f)


width = 0
height = 0

elements = standards_dict["elements"]
minerals = standards_dict["minerals"]

element_slopes = {}
element_samples = {}

element_dimages = {}

for element in elements:
	img = Image.open("standard/"+elements[element])
	element_dimages[element] = cuda.to_device(img)
	element_slopes[element] = 0
	element_samples[element] = 0
	width = img.width
	height = img.height

maskBuf = np.zeros((height, width), dtype = np.int32)
device_maskBuf = cuda.to_device(maskBuf)

for mineral in minerals:
	maskImg = Image.open("standard/"+minerals[mineral]["maskFile"]);
	maskDImage = cuda.to_device(maskImg)

	map_nonzero(maskDImage, device_maskBuf)
	maskpixels = sum_reduce(np.ravel(device_maskBuf))
	minerals[mineral]["intensity"] = {}
	print(mineral)
	mineralElements = minerals[mineral]["elements"]
	for element in mineralElements:
		if element in elements.keys():
			expectedWeight = mineralElements[element]
			map_mask(element_dimages[element], maskDImage, device_maskBuf)
			elemTotalIntensity = sum_reduce(np.ravel(device_maskBuf))
			elemAverageIntensity = elemTotalIntensity / maskpixels
			minerals[mineral]["intensity"][element] = elemAverageIntensity
			print("\t" + element + ": " + str(elemAverageIntensity))
			elemSlope = elemAverageIntensity / expectedWeight
			#element_slopes[element] = (element_slopes[element] * element_samples[element] + elemSlope) / (element_samples[element] + 1)
			element_slopes[element] += elemSlope
			element_samples[element] += 1


for element in element_slopes:
	if(element_slopes[element] != 0):
		element_slopes[element] = element_slopes[element] / element_samples[element]

with open("calibration.json", "w") as outfile:
	json.dump(element_slopes, outfile)