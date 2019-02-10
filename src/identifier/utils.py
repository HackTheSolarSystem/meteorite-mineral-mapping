def get_image_path(targetObject, element):
  return targetObject + "/" + targetObject + "_32bt_" + element + ".tif"

def get_target_mask(targetObject):
  return targetObject + "/" + targetObject + "_mask.tif"

def compare_dist(maskImage, indexImage, distImage, cmpIndex, cmpDists):
  tWidth = len(maskImage[0])
  tHeight = len(maskImage)
  for x in range(0, tWidth):
		for y in range(0, tHeight):
			if maskImage[y,x] != 0:
				if cmpDists[y,x] < distImage[y,x]:
					indexImage[y,x] = cmpIndex
					distImage[y,x] = cmpDists[y,x]

def calc_dist(maskImage, bufImage, elemImage, testValue):
  tWidth = len(maskImage[0])
  tHeight = len(maskImage)
  for x in range(0, tWidth):
		for y in range(0, tHeight):
			if maskImage[y,x] != 0:
				diff = abs(elemImage[y,x] - testValue)
				bufImage[y,x] += diff * diff
			else:
				bufImage[y,x] = 0

def map_mask(maskImage, inImage, outImage):
  tWidth = len(maskImage[0])
  tHeight = len(maskImage)
  for x in range(0, tWidth):
		for y in range(0, tHeight):
			if maskImage[y,x] != 0:
				outImage[y,x] = inImage[y,x]
			else:
				outImage[y,x] = 0
