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
    print("The workspace has set to: " + work_path)
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
    # Project XY coordination system
    arcpy.ProjectRaster_management(dem, 'XY_dem', out_coordinate_system, "BILINEAR", '1')
    pro_raster = Times('XY_dem', 0.3048)  # Covert unit of z value from feet to meter
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
    The input should be mask raster, DEM raster, polygon shape file and the output will be solar energy table"""
    solar = 'solar_raster'
    solar_tab = 'solar_energy'
    result = Times(mask, raster)
    result.save("result")
    polygon_raster = ExtractByMask("result", polygon)  # extract by polygon of buildings or parking lots
    polygon_raster.save("poly_raster")
    # calculate solar radiation
    sol_radiation = AreaSolarRadiation("poly_raster", time_configuration=TimeWholeYear(2018),
                                       out_direct_duration_raster='solar_dur')
    sol_radiation.save("solar_rad")  # unit WH/m2
    solar_result = Divide('solar_rad', "solar_dur")
    solar_result.save(solar)  # unit W/m2
    ZonalStatisticsAsTable(polygon, 'FID', solar, solar_tab, "DATA", "SUM")  # generate solar energy table
    return solar_tab


def join_shape(solar_tab, building, address):
    """This function is used to join the solar energy table with building and address shape files
    The input should be table, building and address shape files, and the output should be joined shape file"""
    sol_build = 'solar_build'
    build_addr = 'addr_build'
    arcpy.AddIndex_management(solar_tab, 'FID')  # Index.
    # join table to building
    arcpy.MakeFeatureLayer_management(building, 'build_layer')
    arcpy.AddJoin_management('build_layer', 'FID', solar_tab, 'FID', 'KEEP_COMMON')
    arcpy.CopyFeatures_management('build_layer', 'solar_build')
    # join address to building
    arcpy.SpatialJoin_analysis('solar_build', address, build_addr,
                           'JOIN_ONE_TO_ONE', 'KEEP_COMMON', field_mappings(sol_build, address), 'CLOSEST')
    return build_addr


def field_mappings(sol_build, address):
    """This function creates field mappings for other function"""
    fms = arcpy.FieldMappings()
    # create field maps
    f_st_add = arcpy.FieldMap()
    f_st_add.addInputField(address, 'ST_ADD')
    f_cityzip = arcpy.FieldMap()
    f_cityzip.addInputField(address,'CITYSTZIP')
    f_council = arcpy.FieldMap()
    f_council.addInputField(address, 'COUNCIL')
    f_area = arcpy.FieldMap()
    f_area.addInputField(sol_build, 'solar_en_3')
    f_solar = arcpy.FieldMap()
    f_solar.addInputField(sol_build, 'solar_en_4')
    # rename field maps
    area_name = f_area.outputField
    area_name.name = 'AREA'
    f_area.outputField = area_name
    solar_name = f_solar.outputField
    solar_name.name = 'SOLAR'
    f_solar.outputField = solar_name
    # add field maps to field mappings
    fms.addFieldMap(f_st_add)
    fms.addFieldMap(f_cityzip)
    fms.addFieldMap(f_council)
    fms.addFieldMap(f_area)
    fms.addFieldMap(f_solar)
    return fms


def generate_result(shape):
    """This function converts shape file into excel and kml files.
    The input should be shape file, and the output will be excel and kml files"""
    table = 'fin_result.xls'
    kml = 'fin_result.kml'
    arcpy.TableToExcel_conversion(shape, table)
    arcpy.MakeFeatureLayer_management(shape, 'layer')
    arcpy.LayerToKML_conversion('layer', kml)
    return table, kml


def main(work_path, las, building, address):
    """This is the main function of the module.
    The input should be the path all files store, .las files or folder, building shapefile, and address shape file.
    The output will be .xls file and .kml file""""
    arc_beg(work_path)
    dem = las_to_raster(las)
    raster = project_raster(dem)
    mask = create_mask(raster)
    solar_tab = solar_radiation(mask, raster, building)
    build_addr = join_shape(solar_tab, building, address)
    generate_result(build_addr)
    print("Work completed. The output files fin_result.xls and fin_result.kml are saved to " + work_path)
    return