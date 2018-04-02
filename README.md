Uses Python 2.7 and requires h5py, the Allen SDK, and other packages that are
all available through Anaconda.

Example data are not included in this repo since the files are too big, so copy
the "data/" dir into the main directory of the repo before running. This directory
should contain both an image stack of projection data and also a h5py file
containing a numpy array representing the image stack of voxel intensities.

Instructions:
1) Load a CCF-aligned stack of images into ImageJ, for example the image stack
provided at 20um resolution in the directory "data/".
2) Use the polygon tool to draw planar ROIs through as many slices as you want.
3) Create a new directory with the naming convention "<name>_mask" in the
directory "blob_masks/".
4) Edit the imagej macro "save_parcellation.ijm" to make the variable save_path
point to this directory, and run it.
5) Repeat 2-4 for each large volume segmentation you want. After blob_masks/
has been filled up with directories containing image stacks of all the volumes
of interest, type

python main.py

into the command line (or python main.py -h to explore options first) and it
will spit out the results in a spreadsheet in /results.

Some incredibly lazy parcellations and the results thereof that I did myself
exist already in the directory, but these were just used to make sure the
program works.
