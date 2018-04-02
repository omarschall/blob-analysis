save_path = "/Users/omarschall/map/blob_analysis/blob_masks/striatum_mask/"
roiManager("Interpolate ROIs");
roiManager("Fill");
for (i=0; i<1400; i++) {
      roiManager("Select", i);
      s = getInfo("selection.name");
      run("Create Mask");
      saveAs("PNG", save_path+"mask-"+s+".png");
      close();
}
