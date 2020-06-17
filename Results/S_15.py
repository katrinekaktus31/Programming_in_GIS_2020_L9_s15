import arcpy
import numpy as np

cities = r"D:\python_project\PC_project\S_arcPy\S_15\Programming_in_GIS_2020_L9_s15\us_cities1.shp"
inputraster = r"D:\python_project\PC_project\S_arcPy\S_15\Programming_in_GIS_2020_L9_s15\us.tmax_nohads_ll_20140525_float.tif"
clipzone = r"D:\python_project\PC_project\S_arcPy\S_15\Programming_in_GIS_2020_L9_s15\us_boundaries1.shp"
workspace = r"D:\python_project\PC_project\S_arcPy\S_15\Programming_in_GIS_2020_L9_s15\Results"
popsize = 3

arcpy.MakeFeatureLayer_management(cities, "citiesLayer", '"POPCLASS"' + ">=" + 'str(popsize)')
arcpy.CopyFeatures_management("citiesLayer", "us_cities_level_" +str(popsize)+".shp")

# Reprojest raster
arcpy.ProjectRaster_management(inputraster, inputraster[-5] + "_NAD" + ".tif", cities, geographic_transform=cities)

#Clip raster
clip = arcpy.sa.ExtractByMask(inputraster, clipzone, inputraster[-5] + "_NAD_extract_by_mask" + ".tif")

# Get value temperature
with arcpy.da.SearchCursor("us_cities_level_" + str(popsize)+".shp", "SHAPE@XY") as cursor:
    temperature = []
    for i in cursor:
        res = arcpy.GetCellValue_management(inputraster, str(i[0][0])+" "+str(i[0][1]))
        value=float(str(res.getOutput(0)).replace(",", "."))
        temperature.append(float(value))
    del cursor
# Add new fields and update
arcpy.AddField_management("us_cities_level_" + str(popsize)+".shp", "TEMPERATUR", 'FLOAT')
arcpy.AddField_management("us_cities_level_" + str(popsize)+".shp", "EXCESS", 'FLOAT')
arcpy.AddMessage('Added new fields to the  TEMPERATUR and EXCESS')

with arcpy.da.UpdateCursor("us_cities_level_" + str(popsize)+".shp", ["TEMPERATUR", "EXCESS"]) as Upcursor:
    i = 0
    for row in Upcursor:
        row[0] = temperature[i]
        row[1] = row[0] - np.mean(temperature)
        Upcursor.updateRow(row)
        i += 1
arcpy.AddMessage('Update fields')
