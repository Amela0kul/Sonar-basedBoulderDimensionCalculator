from qgis.core import QgsProject, QgsVectorLayer
from math import sqrt
from shapely.wkt import loads as wkt_loads
from shapely.geometry import shape
from shapely.ops import unary_union
from shapely.geometry import MultiPolygon, Polygon
from shapely.wkt import loads
from qgis.core import QgsPointXY

raster_path=r'C:\Users\Amela\Desktop\hidrocibalae\01_Task_BoulderHeights_toSend\01_Task_BoulderHeights_toSend\MBES grid\Test_Encoded_Depths_File.tif'
vector_path=r'C:\Users\Amela\Desktop\hidrocibalae\01_Task_BoulderHeights_toSend\01_Task_BoulderHeights_toSend\Boulder polygons\Test_Manually_Picked_Boulders.shp'

vlayer=QgsVectorLayer(vector_path, 'Test Manually Picked Boulders', 'ogr')
rlayer=QgsRasterLayer(raster_path,'Test Encoded Depths File')

QgsProject.instance().addMapLayer(vlayer)
QgsProject.instance().addMapLayer(rlayer)

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
    
existing_field_names=[field.name() for field in vlayer.fields()]
fields_to_add_filtered=[field for field in fields_to_add if field.name() not in existing_field_names]
vlayer.dataProvider().addAttributes(fields_to_add_filtered)
vlayer.updateFields()

points_layer=QgsVectorLayer("Point?crs="+ vlayer.crs().authid(), "Centroids", "memory")

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

rect_layer=QgsVectorLayer("Polygon?crs="+vlayer.crs().authid(), "Rectangles", "memory")
rect_layer.dataProvider().addAttributes([QgsField("Poly_ID", QVariant.Int)])
rect_layer.updateFields()

block, ok_pressed=QInputDialog.getText(None, 'Enter Block', 'Enter a value for Block attribute: ')
if not ok_pressed:
    block="defaultBlock"


for index, feature in enumerate(vlayer.getFeatures()):
    poly_id_value=index
    centroid=feature.geometry().centroid().asPoint()
    
    wkt_string=feature.geometry().asWkt()
    shapely_geometry=loads(wkt_string)
    
    min_rotated_rect=shapely_geometry.minimum_rotated_rectangle
    rect_coords=list(min_rotated_rect.exterior.coords)
    
    rectangle=QgsRectangle(rect_coords[0][0], rect_coords[0][1], rect_coords[2][0], rect_coords[2][1])
    rect_geometry=QgsGeometry.fromRect(rectangle)
    
    rect_feature=QgsFeature()
    rect_feature.setGeometry(rect_geometry)
    rect_feature.setAttributes([poly_id_value])
    rect_layer.dataProvider().addFeature(rect_feature)
    #QgsProject.instance().addMapLayer(rect_layer)
    
    length=sqrt((rect_coords[1][0]-rect_coords[0][0])**2 + (rect_coords[1][1]-rect_coords[0][1])**2)
    width = sqrt((rect_coords[2][0] - rect_coords[1][0])**2 + (rect_coords[2][1] - rect_coords[1][1])**2)
    
    if width>length:
        length, width=width, length
        
    z_values=[]
    
    if isinstance(shapely_geometry, MultiPolygon):
            for part in shapely_geometry.geoms:
                if not isinstance(part, Polygon):
                    continue
                    
                for point in part.exterior.coords:
                    value, success=rlayer.dataProvider().sample(QgsPointXY(point[0],point[1]), 1)
                    if success:
                        z_values.append(value)
                        
                for point in part.interiors:
                    for point in interior.coords:
                        value, success=rlayer.dataProvider().sample(QgsPointXY(point[0], point[1]), 1)
                        if success:
                            z_values.append(value)
                    
    if(z_values):         
        lowest_point_depth=min(z_values)
        highest_point_depth=max(z_values)
        height=highest_point_depth-lowest_point_depth
        
        depth, success= rlayer.dataProvider().sample(QgsPointXY(centroid), 1)
        
        new_feature = QgsFeature()
        new_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(centroid)))
        new_feature.setAttributes([poly_id_value, f"MBES_{block}_{str(poly_id_value).zfill(2)}", block,
                                   feature['KP'], feature['DCC'], centroid.x(), centroid.y(),
                                   round((depth), 10), length, width, round((height), 10)])


        points_layer.dataProvider().addFeature(new_feature)
        
QgsProject.instance().addMapLayer(points_layer)    
output_path=r'C:\Users\Amela\Desktop\hidrocibalae\01_Task_BoulderHeights_toSend\01_Task_BoulderHeights_toSend\Boulder polygons\Output_Layer.shp'

error = QgsVectorFileWriter.writeAsVectorFormat(points_layer, output_path, 'utf-8', QgsCoordinateReferenceSystem(), 'ESRI Shapefile')

if error[0] == QgsVectorFileWriter.NoError:
    print('SHP file successfully created at:', output_path)
else:
    print('Error creating SHP file:', error)