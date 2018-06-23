# This python module is based on ModelBuilder from Arcgis, and under the license of Arcgis

import arcpy
from arcpy.sa import *


def arc_beg(work_path):
    """This function is used to set workspace and load extensions of Arcgis.
    The input should be the path all files store."""
    arcpy.env.workspace = work_path  # set workspace
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("3D")  # load 3D Analyst tool
    arcpy.CheckOutExtension("Spatial")  # load Spatial Analyst tool
    return


def las_to_raster(las, dem):
    """This function converts las data to las dataset, and turn the dataset into raster.
    The input should be .las files or folder and the name of output raster file"""
    arcpy.CreateLasDataset_management(las, 'dataset.lasd', 'RECURSION')  # convert las data into las dataset
    arcpy.LasDatasetToRaster_conversion('dataset.lasd', dem, "ELEVATION", "BINNING AVERAGE NATURAL_NEIGHBOR",
                                        "FLOAT", "CELLSIZE", 1, 1)  # convert las dataset into raster
    return


# need to test
def project_raster(dem, raster):
    """This function is used to convert unit of coordination system from feet to meter.
    The input should be a raster and the name of output raster file"""
    out_coordinate_system = arcpy.SpatialReference('GCS_WGS_1984')
    ProjectRaster_management(dem, 'XY_dem', out_coordinate_system, "BILINEAR", '#', "NAD_1983_To_WGS_1984"
                        '#', '#')  # Project XY coordination system
    Project_raster = Times('XY_dem', "0.3048")  # Covert unit of z value from feet to meter
    Project_raster.save(raster)
    return
