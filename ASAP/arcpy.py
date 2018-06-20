### This python module is based on ModelBuilder from Arcgis, and under the license of Arcgis.

import arcpy
from arcpy.sa import *

def arc_beg(work_path):
    """This function is used to set workspace and load extensions of Arcgis"""
    arcpy.env.workspace = work_path  ###set workspace
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("3D")  ###load 3D Analyst tool
    arcpy.CheckOutExtension("Spatial")  ###load Spatial Analyst tool
    return


def las_to_raster(las, lasd, dem):
    """This function converts las data to las dataset, and turn the dataset into raster"""
    arcpy.CreateLasDataset_management(las, lasd, 'RECURSION')
    arcpy.LasDatasetToRaster_conversion(lasd, dem, "ELEVATION", "BINNING AVERAGE NATURAL_NEIGHBOR",
                                   "FLOAT", "CELLSIZE", 1, 1)
    return