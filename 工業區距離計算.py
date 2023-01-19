#此程式用以計算距離環保署測站第N近之工業區為何，提供資訊包含各測站之：
#第N近工業區、第N近工業區距離(km)、第N近工業區最近點緯度、第N近工業區最近點經度、
#第N近工業區方位角、第N近工業區方位
#使用之資料皆為公開資料，
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import nearest_points
from geographiclib.geodesic import Geodesic
###########################手動輸入欲計算第N近之工業區############################
n = input('欲計算離測站第N近之工業區(請輸入N):') #取第N近工業區
#nn = int(n) - 1
###########################讀取工業區資訊############################
industrial_zone = gpd.read_file('data/提交2022工業區範圍.shp') #讀取工業區資料
industrial_zone_wgs84 = industrial_zone.to_crs('epsg: 4326') #工業區範圍座標轉WGS84
#industrial_zone = industrial_zone[(industrial_zone.開發情 == "已開發完成")] #篩選已開發完成的工業區
#industrial_zone.to_csv('industrial_zone.csv', sep = ',', index=False, encoding='utf_8_sig') #輸出csv
###########################讀取環保署測站經緯度資訊############################
epa = pd.read_csv('環保署測站經緯度(75站).csv')
station = list(epa.iloc[:, 0])
lat = list(epa.iloc[:, 2])
lon = list(epa.iloc[:, 1])
###########################計算環保署測站與工業區之相關資訊############################
list_0 =[]
list_1 =[]
list_2 =[]
list_3 =[]
list_4 =[]
list_5 =[]
list_6 =[]
for i, j, k in zip(station, lat, lon):
    point = Point(j, k)
    point_gdf_wgs84 = gpd.GeoDataFrame(geometry=[point], crs='epsg: 4326') #測站座標轉GeoDataFrame
    point_gdf_twd97 = point_gdf_wgs84.to_crs('epsg: 3826') #轉TWD97
    point_gdf_list = Point(*list(point_gdf_twd97.geometry[0].coords)[0]) #組成list
###########################計算出第N近工業區、距離(km)及其最近點經緯度資訊############################
    index_0 = industrial_zone.distance(point_gdf_list).sort_values().index[int(n) - 1] #抓出離該點第N近的工業區，修改index[0]以取出第N近
    industrial_name = industrial_zone.iloc[:, 1][index_0] #列出第N近工業區名稱
    industrial_distance = np.around(np.min((industrial_zone.geometry[index_0].distance(point_gdf_list))/1000), 2) #計算最短距離(km)
    point_gdf2_wgs84 = Point(*list(point_gdf_wgs84.geometry[0].coords)[0]) #組成list
    nearest_industrial_geometry = industrial_zone_wgs84.iloc[:, 9][index_0] #第N近工業區之geometry
    nearest_p = list(nearest_points(point_gdf2_wgs84, nearest_industrial_geometry))[1] #取測站與第N近工業區最近的點座標
    nearest_p_lat = list(nearest_p.coords[0])[1]
    nearest_p_lon = list(nearest_p.coords[0])[0]
###########################計算方位角############################
    azimuth = list(Geodesic.WGS84.Inverse(k, j, nearest_p_lat, nearest_p_lon).values())[6] #計算a點至b點方位角
    azimuth = azimuth if azimuth >= 0 else azimuth+360 #原先geographiclib的方位角是0~180以及0~-180，將其改為0~360的方式表示
###########################求得方位############################
    #定義每22.50度為一個方位，共16方位
    angle_left = [348.75,11.25,33.75,56.25,78.75,101.25,123.75,146.25,168.75,191.25,213.75,236.25,258.75,281.25,303.75,326.25]
    angle_right = [11.25,33.75,56.25,78.75,101.25,123.75,146.25,168.75,191.25,213.75,236.25,258.75,281.25,303.75,326.25,348.75]
    angle_class = ['北','北北東','東北','東北東','東','東南東','東南','南南東','南','南南西','西南','西南西','西','西北西','西北','北北西']
    for a in range(0,len(angle_left)):
        if a ==0:
            if azimuth >= angle_left[a] or azimuth < angle_right[a]:
                dir = angle_class[a]
        if azimuth >= angle_left[a] and azimuth < angle_right[a]:
            dir = angle_class[a]
###########################輸出為.csv############################
    list_0.append(i) #環保署測站名
    list_1.append(industrial_name) #第N近工業區
    list_2.append(industrial_distance) #距離
    list_3.append(np.around(nearest_p_lat, 3)) #測站與第N近工業區最近的點座標(lat)
    list_4.append(np.around(nearest_p_lon, 3)) #測站與第N近工業區最近的點座標(lon)
    list_5.append(np.around(azimuth, 2)) #方位角
    list_6.append(dir) #方位
    river_final = pd.DataFrame(zip(list_0, list_1, list_2, list_3, list_4, list_5, list_6),  columns=['測站名稱','第' + str(n) + '近工業區','第' + str(n) + '近工業區距離(km)', '第' + str(n) + '近工業區最近點緯度(°)', '第' + str(n) + '近工業區最近點經度(°)', '第' + str(n) + '近工業區方位角(°)', '第' + str(n) + '近工業區方位'])
    river_final.to_csv('industrial_zone_distance.csv', sep = ',', index=False, encoding='utf_8_sig') #輸出csv 