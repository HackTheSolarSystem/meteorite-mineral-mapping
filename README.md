# meteorite-mineral-mapping

HackTheSolarSystem [challenge](https://github.com/amnh/HackTheSolarSystem/wiki/Meteorite-Mineral-Mapping)

## Team

- [Xiaoyun Yang](https://github.com/xiaoyunyang)
- [Clyde Shaffer](https://github.com/clydeshaffer)

## Solution

Calibration

```
yarn calibrator
```

## Approach

### Step 1. Calibration

First, we want to create the `Calibrator`, which correlate the gray scale intensity value to the weight% for each element.

To do that, we will use 8 standards. Standards are minerals with known exact compositions. For each standard, we want to apply mask for the standard onto the elements which are in the standard's chemical composition to get the number representing the element's gray scale intensity. Then we correlate the element's gray scale intensity number to the standard's weight% for the element.

We are given a mask for each standard. We are also given 10 elements gray scale tifs. We created [this file](src/calibrator/standards.json), which identified the elements and weight% for each standard and the name of the mask file which will be used by the `Calibrator`.

### Step 2. Create Mineral Baselines

These are the minerals we are interested in finding in our samples.

- [Kamacite](http://webmineral.com/data/Kamacite.shtml#.XF-73c9Ki-w) (Fe9Ni1)
- [Taenite](http://webmineral.com/data/Tetrataenite.shtml#.XF-4l89Ki-w) (Fe,Ni)
- [Millerite](http://webmineral.com/data/Millerite.shtml#.XF-4rs9Ki-w) (NiS)
- [Troilite](http://webmineral.com/data/Troilite.shtml#.XF-5MM9Ki-w) (FeS)
- [Pentlandite](http://webmineral.com/data/Pentlandite.shtml#.XF-6aM9Ki-w)	(FeNiS)
- [Olivine](http://webmineral.com/data/Olivine.shtml#.XF-86s9Ki-w) (Fe,Mg)2SiO4
- Pyroxene (Fe,Mg)SiO

# Dependencies

- python
- [Pillow](https://pillow.readthedocs.io/en/stable/) (PIL) for processing images in python.
- [numba](https://pypi.org/project/numba/) (optional)