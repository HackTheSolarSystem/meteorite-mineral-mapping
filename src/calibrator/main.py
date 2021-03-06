import numpy as np
import json
from scipy.misc import imread

# util
def get_image_path(filename):
  return "standard/" + filename

with open(get_image_path("standards.json"), 'r') as f:
	standards_dict = json.load(f)

elements = standards_dict["elements"]
minerals = standards_dict["minerals"]

element_slopes = {}
element_samples = {}
element_images = {}

for element in elements:
  img = imread(get_image_path(elements[element]))
  element_images[element] = img
  element_slopes[element] = 0
  element_samples[element] = 0
  width = len(img[0])
  height = len(img)

maskBuf = np.zeros((height, width), dtype = np.int32)

for mineral in minerals:
  maskImage = imread(get_image_path(minerals[mineral]["maskFile"]))

  for x in range(0, len(maskImage[0])):
    for y in range(0, len(maskImage)):
      if maskImage[y, x] != 0:
        maskBuf[y, x] = 1
      else:
			  maskBuf[y, x] = 0

  maskpixels = reduce((lambda x, y: x + y), np.ravel(maskBuf))
  minerals[mineral]["intensity"] = {}

  print(mineral)
  mineralElements = minerals[mineral]["elements"]
  
  for element in mineralElements:
    if element in elements.keys():
      expectedWeight = mineralElements[element]
      
      for x in range(0, width):
        for y in range(0, height):
          if maskImage[y, x] != 0:
            maskBuf[y, x] = element_images[element][y, x]
          else:
            maskBuf[y, x] = 0
      elemTotalIntensity = reduce((lambda x, y: x + y), np.ravel(maskBuf))
      elemAverageIntensity = elemTotalIntensity / float(maskpixels)
      minerals[mineral]["intensity"][element] = elemAverageIntensity
      print("\t" + element + ": " + str(elemAverageIntensity))
      elemSlope = elemAverageIntensity / expectedWeight
      element_slopes[element] = (element_slopes[element] * element_samples[element] + elemSlope) / (element_samples[element] + 1)
      element_samples[element] += 1

with open("calibration.json", "w") as outfile:
	json.dump(element_slopes, outfile)
