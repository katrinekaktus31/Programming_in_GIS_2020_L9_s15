import arcpy
import numpy as np

arcpy.env.overwriteOutput = True
cities = arcpy.GetParameterAsText(0)
inputraster = arcpy.GetParameterAsText(1)
clipzone = arcpy.GetParameterAsText(2)
workspace = arcpy.GetParameterAsText(3)
popsize = arcpy.GetParameterAsText(4)
'''
cities = r"D:\python_project\PC_project\S_arcPy\S_15\Programming_in_GIS_2020_L9_s15\us_boundariesCopy.shp"
inputraster = r"D:\python_project\PC_project\S_arcPy\S_15\Programming_in_GIS_2020_L9_s15\us.tmax_nohads_ll_20140525_float.tif"
clipzone = r"D:\python_project\PC_project\S_arcPy\S_15\Programming_in_GIS_2020_L9_s15\us_boundariesCopy.shp"
input_shape = r"D:\python_project\PC_project\S_arcPy\S_15\Programming_in_GIS_2020_L9_s15\Results\us_cities_level_2.shp"
workspace = r"D:\python_project\PC_project\S_arcPy\S_15\Programming_in_GIS_2020_L9_s15\Results"
popsize = 3
'''
arcpy.env.workspace = workspace
arcpy.MakeFeatureLayer_management(cities, "citiesLayer", "POPCLASS >= " + str(popsize))

arcpy.CopyFeatures_management("citiesLayer", "us_cities_level_" + str(popsize) + ".shp")
arcpy.AddMessage('Create feature layer ' + "us_cities_level_"+ str(popsize) + ".shp")


# Reprojest raster
arcpy.ProjectRaster_management(inputraster, "us.tmax_nohads_ll_20140525_float_NAD.tif", cities, geographic_transform = "WGS_1984_(ITRF00)_To_NAD_1983")
arcpy.AddMessage("Reprojected raster us.tmax_nohads_ll_20140525_float in to us.tmax_nohads_ll_20140525_float_NAD.tif")

# Clip raster
clip_raster = arcpy.sa.ExtractByMask("us.tmax_nohads_ll_20140525_float_NAD.tif", clipzone,)
clip_raster.save("us.tmax_nohads_ll_20140525_float_NAD_extract_by_mask.tif")
arcpy.AddMessage("ExtractByMask raster us.tmax_nohads_ll_20140525_float_NAD_extract_by_mask.tif")

# Get value temperature
with arcpy.da.SearchCursor("us_cities_level_" + str(popsize) + ".shp", "SHAPE@XY") as cursor:
    temperature = []
    for i in cursor:
        res = arcpy.GetCellValue_management("us.tmax_nohads_ll_20140525_float_NAD_extract_by_mask.tif", str(i[0][0]) + " " + str(i[0][1]))
        value = float(str(res.getOutput(0)).replace(",", "."))
        temperature.append(float(value))
arcpy.AddMessage("Get value temperature")

# Add new fields and update
arcpy.AddField_management("us_cities_level_" + str(popsize) + ".shp", "TEMPERATUR", 'FLOAT')
arcpy.AddField_management("us_cities_level_" + str(popsize) + ".shp", "EXCESS", 'FLOAT')
arcpy.AddMessage('Added new fields to the  TEMPERATUR and EXCESS')

with arcpy.da.UpdateCursor("us_cities_level_" + str(popsize) + ".shp", ["TEMPERATUR", "EXCESS"]) as Upcursor:
    i = 0
    for row in Upcursor:
        row[0] = temperature[i]
        row[1] = row[0] - np.mean(temperature)
        Upcursor.updateRow(row)
        i += 1
arcpy.AddMessage('Update fields')
arcpy.Delete_management("ScitiesLayer")