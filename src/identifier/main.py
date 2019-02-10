import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
import sys
from scipy.misc import imread
import constants
import utils

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

# for each element name in calibration:
# load image of form targetname/targetname_32bt_elementname.tif
element_scans = {}
for element in calibration:
	img = imread(utils.get_image_path(targetObject, element))
	element_scans[element] = img

# load targetname/targetname_mask.tif
targetMask = imread(utils.get_target_mask(targetObject))

# create output image same size as mask, initialized to zero, formatted as uint8
tWidth = len(targetMask[0])
tHeight = len(targetMask)
outputImage = np.zeros((tHeight, tWidth), dtype = np.uint8)

mineral_dists = np.full((tHeight, tWidth), constants.infInt_32bt, dtype = np.int32)

#for each pixel in mask:
##if mask pixel is not zero:
###closestDist=maxval
###closest=-1 (indexed)
###for each mineral vector:
####compute distance from current pixel's color values to element vector
####if distance is less than closestDist, set closest and closestDist
###set ouput pixel to closestIndex
###set confidence output pixel to closestDist

for vector in calibratedVectors:
	bufImage = np.zeros((tHeight, tWidth), dtype = np.int32)
	vector["buf"] = bufImage
	vector["dbuf"] = bufImage
	for element in calibration:
		utils.calc_dist(targetMask, vector["dbuf"], element_scans[element], vector[element])

for vector in calibratedVectors:
	utils.compare_dist(targetMask, outputImage, mineral_dists, vector["index"], vector["dbuf"])

mapImage = Image.new("P", (tWidth, tHeight), 0)
mapImage.putpalette(constants.pallette)

mineralPixelCounts = {}
for mineral in mineralNames:
	mineralPixelCounts[mineral] = 0

d = ImageDraw.ImageDraw(mapImage)
for x in range(0, tWidth):
		for y in range(0, tHeight):
			color = outputImage[y,x]
			d.point((x,y), fill=int(color))
			if color != 0:
				mineralPixelCounts[mineralNames[color-1]] += 1

mapImage.save(targetObject + "_mineralmap.gif")

with open(targetObject + "_mineralcounts.json", "w") as outfile:
	json.dump(mineralPixelCounts, outfile)

Image.fromarray(mineral_dists, mode="I").save(targetObject + "_confidence.tif")

# legendImage = Image.new("P", (256, 256), 0)
# legendImage.putpalette(constants.pallette)
# dl = ImageDraw.ImageDraw(legendImage)
# for i in range(0, 7):
# 	dl.text((32, 32 * i + 4), mineralNames[i], fill=8, font=ImageFont.truetype(font="arial.ttf",size=18))
# 	(mineralnumSize, _) = dl.textsize(str(mineralPixelCounts[mineralNames[i]]) + "px", font=ImageFont.truetype(font="arial.ttf",size=18))
# 	dl.text((248 - mineralnumSize	, 32 * i + 4), str(mineralPixelCounts[mineralNames[i]]) + "px", fill=8, font=ImageFont.truetype(font="arial.ttf",size=18))
# 	dl.rectangle([(8, 32*i + 4),(24, 32*i + 20)], fill=i+1)