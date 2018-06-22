# This python module is based on ModelBuilder from Arcgis, and under the license of Arcgis

import arcpy
from arcpy.sa import *

def arc_beg(work_path):
    """This function is used to set workspace and load extensions of Arcgis. The input should be the path all files store."""
    arcpy.env.workspace = work_path  # set workspace
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("3D")  # load 3D Analyst tool
    arcpy.CheckOutExtension("Spatial")  # load Spatial Analyst tool
    return

def las_to_raster(las, dem):
    """This function converts las data to las dataset, and turn the dataset into raster.
    The input should be .las files or folder and the name of output raster file"""
    lasd = 'dataset.lasd'
    arcpy.CreateLasDataset_management(las, lasd, 'RECURSION')  # convert las data into las dataset
    arcpy.LasDatasetToRaster_conversion(lasd, dem, "ELEVATION", "BINNING AVERAGE NATURAL_NEIGHBOR",
                                        "FLOAT", "CELLSIZE", 1, 1)  # convert las dataset into raster
    return