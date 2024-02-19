# Sonar-basedBoulderDimensionCalculator
processing of the MBES data

One of the most time-consuming tasks in processing of MBES data is the detection of boulders, 
i.e. stones on the seabed. Along with determining their positions, it is also necessary to calculate three 
key dimensions for each boulder: length, width, and height. Extensive efforts have been dedicated to 
the development of tools for automated boulder detection in MBES data. Although these tools have 
reached a relatively advanced stage and exhibit a high level of accuracy, manual quality control (QC) is 
still required to correct errors arising from the automated detection process. During the manual QC 
phase, processors review the results of the automatic detection and draw polygons around the 
boulders that were not successfully identified. After the processor draws the polygons, a script is used 
to automatically measure the dimensions of the boulders. For more information on MBES sonar data, 
please refer to the following link: https://www.youtube.com/watch?v=_ww2PflbWD8.
The main objective of this task is to develop metodology and according it write a script that 
automatically measures the three dimensions of manually drawn boulders and generates a target list. 
The script should utilize two input data layers:
1. A vector layer in SHP format containing polygons that approximate the shape of the boulders. 
No additional attribute fields are required, only the polygon geometry. The polygons should 
accurately outline the contours of the boulders.
2. A gridded surface of bathymetric average values encoded in GeoTiff format (32-bit floating 
point samples for elevation). The file extension must be .tif. The depths can be either positive 
or negative.

OUTPUT:

raster_path=r'C:\Users\Amela\Desktop\hidrocibalae\01_Task_BoulderHeights_toSend\MBES 
grid\Test_Encoded_Depths_File.tif'
vector_path=r'C:\Users\Amela\Desktop\hidrocibalae\01_Task_BoulderHeights_toSend\Boulder 
polygons\Test_Manually_Picked_Boulders.shp'
In these line of code, we use paths to specify the location of the raster and vector files, namely 
the TIFF file and the Shapefile(.tif, .shp)

vlayer=QgsVectorLayer(vector_path, 'Test Manually Picked Boulders', 'ogr')
rlayer=QgsRasterLayer(raster_path,'Test Encoded Depths File')
These lines of code create QgsVectorLayer and QgsRasterLayer objects in QGIS using the 
provided file paths.

QgsProject.instance().addMapLayer(vlayer)
QgsProject.instance().addMapLayer(rlayer)
Adding the vlayer and rlayer to the current QGIS project

fields_to_add = [
QgsField('Poly_ID', QVariant.Int), 
QgsField('Target_ID', QVariant.String),
QgsField('Block', QVariant.String),
QgsField('KP', QVariant.String),
QgsField('DCC',QVariant.String),
QgsField('Easting', QVariant.Double),
QgsField('Northing', QVariant.Double),
QgsField('WaterDepth', QVariant.Double),
QgsField('Length', QVariant.Double),
QgsField('Width', QVariant.Double),
QgsField('Height', QVariant.Double)]
Defining the list ‘fields_to_add’ that contains attributes we want to add to the vector layer. 
Each attribute is defined as QgsField.

existing_field_names=[field.name() for field in vlayer.fields()]
fields_to_add_filtered=[field for field in fields_to_add if field.name() not in existing_field_names]
Here, a list named ‘existing_field_names’ is created, containing the names of all exsisting 
attributes in the vector layer. This will be used to avoid adding the same attributes that already 
exists.

vlayer.dataProvider().addAttributes(fields_to_add_filtered)
vlayer.updateFields()
We inform the data provider to add new attributes to the vector layer. These attributes will be 
associated with the geometries within the layer, allowing us to store additional information 
about those geometries.

points_layer=QgsVectorLayer("Point?crs="+ vlayer.crs().authid(), "Centroids", "memory")
This line of code creates a new vector layer for storing point geometries. If specifies that the 
layer will contain point geometries with the same coordinate reference system (CRS) as the 
‘vlayer’. The layer is named ‘Centroids’ and is stored in memory.

point_fields = [
QgsField('Poly_ID', QVariant.Int), 
QgsField('Target_ID', QVariant.String),
QgsField('Block', QVariant.String),
QgsField('KP', QVariant.String),
QgsField('DCC',QVariant.String),
QgsField('Easting', QVariant.Double),
QgsField('Northing', QVariant.Double),
QgsField('WaterDepth', QVariant.Double),
QgsField('Length', QVariant.Double),
QgsField('Width', QVariant.Double),
QgsField('Height', QVariant.Double)]
points_layer.dataProvider().addAttributes(point_fields) 
points_layer.updateFields()
Defining a list that contains QgsField objects representing new attributes we want to add in the 
vector layer 'points_layer.

rect_layer = QgsVectorLayer("Polygon?crs=" + vlayer.crs().authid(), "Rectangles", "memory")
rect_layer.dataProvider().addAttributes([QgsField("Poly_ID", QVariant.Int)])
rect_layer.updateFields()
In these lines of code, a new vector layer is created to store rectangles representing minimum 
rotated bounding boxes aroud each polygon in the original layer, with an added attribute field 
‘Poly_ID’ for identification. We will utilize these rectangles to determine the length and width 
of the boulders.

block, ok_pressed = QInputDialog.getText(None, 'Enter Block', 'Enter a value for Block attribute:')
if not ok_pressed:
block = "DefaultBlock"
This code is used to prompt the user to enter a value for the "Block" attribute.

for index, feature in enumerate(vlayer.getFeature()):
This is a loop that iterates over all features in the ‘vlayer’ vector layer, and ‘index’ represents 
the index of the current feature (boulder).

poly_id_value=index
Setting the variable ‘poly_id_value’ to the index of current feature.

centroid=feature.geometry().centroid.asPoint()
Retrieves the geometry of the current feature, calculates its centroid and stores it in the 
variable centroid. Method ‘as.Point()’ converts the centroid into a ‘QgsPointXY’ object which 
contains the x and y coordinates of the point.

wkt_string=feature.geometry().aswkt()
Retrieves the Well-Known Text representation of the current object and stores it in the variable 
wkt_string. WKT is a text representation for geometric objects.

shapely_geometry=loads(wkt_string)
Uses the loads function from the Shapely library to convert the WKT string into a geometric 
objects, in this case, in Shapely object.

min_rotated_rect=shapely_geometry.minimum_rotated_rectangle
Calculates the minimum rotated rectangle for the geometry of the object using Shapely 
functionality.

rect_coords=list(min_rotated_rect.exterior.coords)
Converts the coordinates of the exterior (outer ring) of the minimum rotated rectangle into a 
list of coordinates and stores them in the variable rect_coords.

rectangle = QgsRectangle(rect_coords[0][0], rect_coords[0][1], rect_coords[2][0], rect_coords[2][1])
rect_geometry = QgsGeometry.fromRect(rectangle)
The ‘QgsRectangle’ represents a rectangle in the coordinate space. There we create a 
‘QgsRectangle’ object using the coordinates of the top-left and bottom-right corners of the 
rectangle obtained from ‘rect_coords’. Then, we xreaate QgsGeometry object from 
QgsRectangle. It represents the geometry of the rectangle.

rect_feature = QgsFeature()
rect_feature.setGeometry(rect_geometry)
rect_feature.setAttributes([poly_id_value]) 
rect_layer.dataProvider().addFeature(rect_feature)
QgsProject.instance().addMapLayer(rect_layer)
The code initializes a new feature ‘rect_feature’ with a specified geometry (a rectangle in this 
case), sets attributes, adds this feature to the data provider of a vector layer, and finally adds 
the vector layer to the QGIS project.

length = sqrt((rect_coords[1][0] - rect_coords[0][0])**2 + (rect_coords[1][1] - rect_coords[0][1])**2)
width = sqrt((rect_coords[2][0] - rect_coords[1][0])**2 + (rect_coords[2][1] - rect_coords[1][1])**2)
if width>length:
length, width = width, length
These lines of code are using Euclidean distance formula to calculate the distance between two 
points (length and width of a rectangle based on its coordinates). Ensure that the longer side
corresponds to the maximum distance within the boulder, i.e., the value for the boulder's length. Meanwhile, the boulder's width represents the distance within the polygon perpendicular to the length.

z_values = []
if isinstance(shapely_geometry, MultiPolygon):
for part in shapely_geometry.geoms:
if not isinstance(part, Polygon):
continue
for point in part.exterior.coords:
value, success = rlayer.dataProvider().sample(QgsPointXY(point[0], point[1]), 1)
if success:
z_values.append(value)
for interior in part.interiors:
for point in interior.coords:
value, success = rlayer.dataProvider().sample(QgsPointXY(point[0], point[1]), 1)
if success:
z_values.append(value)
The code collects depth values for points along both the exterior and interior coordinates of 
each polygon within ‘shapely_geometry’. It checks if the geometry is a ‘MultiPolygon’, iterates 
though its parts, and samples depth values from the raster layer for each point. The depth 
values are appended to the ‘z_values’ list.

if z_values:
lowest_point_depth = min(z_values)
highest_point_depth = max(z_values)
height = highest_point_depth - lowest_point_depth
These lines calculate the minimum and maximum depth values from the collected ‘z_value’ list. 
Then, we calculate the height of the boulder as the difference between the highest and lowest 
depth points.

depth, success = rlayer.dataProvider().sample(QgsPointXY(centroid), 1)
This line samples the depth values at the centroid of the boulder from the rlayer.

new_feature = QgsFeature()
new_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(centroid)))
new_feature.setAttributes([poly_id_value, f"MBES_{block}_{str(poly_id_value).zfill(2)}", block,
feature['KP'], feature['DCC'], centroid.x(), centroid.y(),
round((depth), 10), length, width,
round((height), 10)])
points_layer.dataProvider().addFeature(new_feature)
QgsProject.instance().addMapLayer(points_layer) 
Creating a new feature for the point layer, setting the geometry of the new feature to the 
centroid of the boulder and then setting attributes for the new feature. Let's break down the 
attributes that are being set:
Poly_ID– identifier for the polygon feature,
Target_ID - contain the value "MBES" and include the block name and target order number
Block – value provided by the user
Easting and Northing - These are the x and y coordinates of the centroid of the original polygon,
Depth - sampling the depth values at the centroid of the boulder from the rlayer
Length - longer side od rectangle
Width - distance within the polygon perpendicular to the length
Height - difference between the highest and lowest boulder’s depth points.

points_layer.dataProvider().addFeature(new_feature)
QgsProject.instance().addMapLayer(points_layer) 
Adding features to ‘points_layer’ and adding that layer to the QGIS project.
output_path=r'C:\Users\Amela\Desktop\hidrocibalae\01_Task_BoulderHeights_toSend\01_Task_BoulderHeights_toS
end\Boulder polygons\Output_Layer.shp'

error = QgsVectorFileWriter.writeAsVectorFormat(points_layer, output_path, 'utf-8', 
QgsCoordinateReferenceSystem(), 'ESRI Shapefile')
if error[0] == QgsVectorFileWriter.NoError:
print('SHP file successfully created at:', output_path)
else:
print('Error creating SHP file:', error)
Storing the output layer in the same folder as the input vector layer.

This script is designed for the QGIS platform and utilizes the QGIS Python API along with the 
Shapely library for working with geometric data. It is designed to analyze specific vector and 
raster data. To test it, follow these steps:
 Ensure all required data is available at the specified paths,
 Open the script in the QGIS Python console or use an external text editor (such as 
VSCode) connected to QGIS
 Run the script and follow the output in the console,
 Check the resulting vector layer in the QGIS project
The script uses various libraries such as Shapely and the QGIS Python API, so it's important to 
ensure that these libraries are available in your environment. The results will be exported to a 
new Shapefile at the path specified in the ‘output_path’ variable. Verify that this path is correct 
and has write permission

