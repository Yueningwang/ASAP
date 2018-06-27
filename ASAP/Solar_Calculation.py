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
    print("The workspace has set to:"+ work_path)
    return


def las_to_raster(las):
    """This function converts las data to las dataset, and turn the dataset into raster.
    The input should be .las files or folder and the ouput will be raster file"""
    dem = 'DEM_raster'
    arcpy.CreateLasDataset_management(las, 'dataset.lasd', 'RECURSION')  # convert las data into las dataset
    arcpy.LasDatasetToRaster_conversion('dataset.lasd', dem, "ELEVATION", "BINNING AVERAGE NATURAL_NEIGHBOR",
                                        "FLOAT", "CELLSIZE", 1, 1)  # convert las dataset into raster
    return dem


def project_raster(dem):
    """This function is used to convert unit of corrdination system from feet to meter.
    The input should be a raster and the output will be projected raster file"""
    raster = 'projected_DEM'
    out_coordinate_system = arcpy.SpatialReference(26934)
    arcpy.ProjectRaster_management(dem, 'XY_dem', out_coordinate_system, "BILINEAR") #Project XY coordination system
    pro_raster = Times('XY_dem', 0.3048) #Covert unit of z value from feet to meter
    pro_raster.save(raster)
    return raster


def create_mask(raster):
    """This function creates a mask to filter unsuitable location to install solar panels.
    The input should be a raster and the output will be mask raster"""
    mask = 'mask_raster'
    arcpy.Aspect_3d(raster, 'aspect')  # filter aspect
    # filter south facing or horizontal aspect. Flat, 112.5 <= aspect <= 247.5, set value to 1, others to None
    filter_aspect = Con((Raster('aspect') == -1) | (Raster('aspect') >= 112.5) & (Raster('aspect') <= 247.5), 1, '')
    filter_aspect.save("filtered_aspect.tif")
    arcpy.Slope_3d(raster, 'slope', "DEGREE", 1)  # filter slope
    # filter slope degree <= 35 to 1, others to None
    filter_slope = Con(Raster('slope') <= 35, 1, '')
    filter_slope.save("filtered_slope.tif")
    result = Times("filtered_aspect.tif", "filtered_slope.tif")  # Combine slope and aspect
    result.save(mask)
    return mask


def solar_radiation(mask, raster, polygon):
    """This function is used to calculate solar radiation of filtered location.
    The input should be mask raster, DEM raster, polygon shape file and the output will be solar raster"""
    solar = 'solar_raster'
    result = Times(mask, raster)
    result.save("result")
    polygon_raster = ExtractByMask("result", polygon)  # extract by polygon of buildings or parking lots
    polygon_raster.save("poly_raster")
    sol_radiation = AreaSolarRadiation("poly_raster", time_configuration=TimeWholeYear(2018), 
                                       out_direct_duration_raster='solar_dur')  # calculate solar radiation
    sol_radiation.save("solar_rad")  # unit WH/m2
    solar_result = Divide('solar_rad', "solar_dur")
    solar_result.save(solar)  # unit W/m2
    return solar
