from numba import cuda
from numba import *
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
import sys

targetObject = sys.argv[1]

#load calibration JSON from standard
with open("calibration.json", 'r') as f:
	calibration = json.load(f)
#load target minerals JSON
with open("test-minerals.json") as f:
	testMinerals = json.load(f)


#multiply each element weight in target minerals by element scalars in calibration json
#store as calibratedWeights
calibratedVectors = []
mineralNames = []

mineralIndex = 0
for mineral in testMinerals:
	mineralIndex += 1
	testMineral = testMinerals[mineral]
	mineralNames.append(mineral)
	for vector in testMineral["elements"]:
		calibratedVector = { "name" : mineral, "index" : mineralIndex}
		for element in calibration:
			if element in vector.keys():
				calibratedVector[element] = calibration[element] * vector[element]
			else:
				calibratedVector[element] = 0
		calibratedVectors.append(calibratedVector)

#for each element name in calibration:
##load image of form targetname/targetname_32bt_elementname.tif
element_scans = {}
for element in calibration:
	img = Image.open(targetObject + "/" + targetObject + "_32bt_" + element + ".tif")
	element_scans[element] = cuda.to_device(img)


#load targetname/targetname_mask.tif
targetMask = Image.open(targetObject + "/" + targetObject + "_mask.tif")
dTargetMask = cuda.to_device(targetMask)

#create output image same size as mask, initialized to zero, formatted as uint8
tWidth = targetMask.width
tHeight = targetMask.height
outputImage = np.zeros((tHeight, tWidth), dtype = np.uint8)
device_outputImage = cuda.to_device(outputImage)

mineral_dists = np.full((tHeight, tWidth), 2147483647, dtype = np.int32)
d_mineral_dists = cuda.to_device(mineral_dists)
#for each pixel in mask:
##if mask pixel is not zero:
###closestDist=maxval
###closest=-1 (indexed)
###for each mineral vector:
####compute distance from current pixel's color values to element vector
####if distance is less than closestDist, set closest and closestDist
###set ouput pixel to closestIndex
###set confidence output pixel to closestDist

@cuda.jit
def calc_dist(maskImage, bufImage, elemImage, testValue):
	for x in range(0, tWidth):
		for y in range(0, tHeight):
			if maskImage[y,x] != 0:
				diff = abs(elemImage[y,x] - testValue)
				bufImage[y,x] += diff * diff
			else:
				bufImage[y,x] = 0


for vector in calibratedVectors:
	bufImage = np.zeros((tHeight, tWidth), dtype = np.int32)
	vector["buf"] = bufImage
	vector["dbuf"] = cuda.to_device(bufImage)
	for element in calibration:
		calc_dist(dTargetMask, vector["dbuf"], element_scans[element], vector[element])
	#vector["dbuf"].to_host()
	#Image.fromarray(vector["buf"]).save("test/" + vector["name"] + "_" + targetObject + ".tif")

@cuda.jit
def compare_dist(maskImage, indexImage, distImage, cmpIndex, cmpDists):
	for x in range(0, tWidth):
		for y in range(0, tHeight):
			if maskImage[y,x] != 0:
				if cmpDists[y,x] < distImage[y,x]:
					indexImage[y,x] = cmpIndex
					distImage[y,x] = cmpDists[y,x]

for vector in calibratedVectors:
	compare_dist(dTargetMask, device_outputImage, d_mineral_dists, vector["index"], vector["dbuf"])

device_outputImage.to_host()



mapImage = Image.new("P", (tWidth, tHeight), 0)
mapImage.putpalette([
    0, 0, 0, # black background
    255, 0, 0, # index 1 is red
    255, 153, 0, # index 2 is orange
    255, 255, 0, # index 3 is yellow
    0, 255, 0, # green
    0, 0, 255, # blue
    152, 0, 255, # indigo
    255, 0, 152 # violet
])

d = ImageDraw.ImageDraw(mapImage)
for x in range(0, tWidth):
		for y in range(0, tHeight):
			color = outputImage[y,x]
			d.point((x,y), fill=int(color))

mapImage.save(targetObject + "_mineralmap.gif")


@cuda.jit
def map_mask(inImage, maskImage, outImage):
	for x in range(0, tWidth):
		for y in range(0, tHeight):
			if maskImage[y,x] != 0:
				outImage[y,x] = inImage[y,x]
			else:
				outImage[y,x] = 0

map_mask(d_mineral_dists, dTargetMask, d_mineral_dists)

d_mineral_dists.to_host()
Image.fromarray(mineral_dists, mode="I").save(targetObject + "_confidence.tif")

legendImage = Image.new("P", (tWidth, tHeight), 0)
legendImage.putpalette([
    0, 0, 0, # black background
    255, 0, 0, # index 1 is red
    255, 153, 0, # index 2 is orange
    255, 255, 0, # index 3 is yellow
    0, 255, 0, # green
    0, 0, 255, # blue
    152, 0, 255, # indigo
    255, 0, 152, # violet
    255, 255, 255
])
dl = ImageDraw.ImageDraw(legendImage)
for i in range(0, 7):
	dl.text((32, 32 * i), mineralNames[i], fill=8, font=ImageFont.truetype(font="arial.ttf",size=18))
	dl.rectangle([(8, 32*i),(24, 32*i + 16)], fill=i+1)

legendImage.save(targetObject + "_legend.gif")