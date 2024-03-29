# -*- coding: utf-8 -*-
#  * 各地图API坐标系统比较与转换;
#  * WGS84坐标系：即地球坐标系，国际上通用的坐标系。
#  * 设备一般包含GPS芯片或者北斗芯片获取的经纬度为WGS84地理坐标系,
#  * 谷歌地图采用的是WGS84地理坐标系（中国范围除外）;
#  * GCJ02坐标系：即火星坐标系，是由中国国家测绘局制订的地理信息系统的坐标系统。
#  * 由WGS84坐标系经加密后的坐标系。谷歌中国地图和搜搜中国地图采用的是GCJ02地理坐标系；
#  * 3BD09坐标系：即百度坐标系，GCJ02坐标系经加密后的坐标系;

import math
from decimal import *


class Transfer():
    def __init__(self,key=None):
        self.a=6378245.0
        self.ee=Decimal(0.00669342162296594323)

    def transformLng(self,x,y):
        ret=Decimal()
        ret = 300.0+x+2.0*y+0.1*x*x+0.1*x*y+0.1*math.sqrt(math.fabs(x))
        ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0* math.pi)) * 2.0 / 3.0
        return ret

    def transformLat(self,x,y):
        ret = Decimal()
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y+ 0.2 * math.sqrt(math.fabs(x))
        ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(y / 12.0 * math.pi) + 320 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
        return ret

    def transfrom(self,lng,lat):
        dLat = self.transformLat(lng - 105.0, lat - 35.0)
        dLng = self.transformLng(lng - 105.0, lat - 35.0)
        radLat = lat / 180.0 * math.pi
        magic = math.sin(radLat)
        magic = 1 - self.ee * Decimal(magic) * Decimal(magic)
        sqrtMagic = math.sqrt(magic)
        dLat = Decimal((dLat * 180.0)) / ((Decimal(self.a) * (1 - self.ee)) / (Decimal(magic) * Decimal(sqrtMagic)) * Decimal(math.pi))
        dLng = (dLng * 180.0) / (self.a / sqrtMagic * math.cos(radLat) * math.pi)
        mgLat = lat + float(dLat)
        mgLng = lng + dLng
        return mgLng,mgLat


    # gps坐标转换为gcj02坐标系
    def wg84_to_gcj02(self,wg84_lng,wg84_lat):
        dLat=self.transformLat(wg84_lng-105.0,wg84_lat-35.0)
        dLng=self.transformLng(wg84_lng-105.0,wg84_lat-35.0)
        radLat = wg84_lat / 180.0 * math.pi
        magic = math.sin(radLat)
        magic = 1 - self.ee * Decimal(magic) * Decimal(magic)
        sqrtMagic = math.sqrt(magic)
        dLat = Decimal((dLat * 180.0)) / ((Decimal(self.a) * (1 - self.ee)) / (Decimal(magic) * Decimal(sqrtMagic)) * Decimal(math.pi))
        dLng = (dLng * 180.0) / (self.a / sqrtMagic * math.cos(radLat) * math.pi)
        gcj02Lat = wg84_lat + float(dLat)
        gcj02Lng = wg84_lng + dLng
        return gcj02Lng,gcj02Lat

    # gcj02坐标转百度坐标
    def gcj02_to_bd09(self,gcj02_lng,gcj02_lat):
        x = gcj02_lng
        y = gcj02_lat
        z = math.sqrt(x * x + y * y) + 0.00002 * math.sin(y * math.pi)
        theta = math.atan2(y, x) + 0.000003 * math.cos(x * math.pi)
        bd09_Lng = z * math.cos(theta) + 0.0065
        bd09_Lat = z * math.sin(theta) + 0.006
        return bd09_Lng,bd09_Lat

    # wg84坐标转百度坐标
    def wg84_to_bd09(self,wg84_lng,wg84_lat):
        gcj02lng,gcj02lat=self.wg84_to_gcj02(wg84_lng,wg84_lat)
        return self.gcj02_to_bd09(gcj02lng,gcj02lat)

    # 百度坐标转GCJ02坐标
    def bd09_to_gcj02(self,bd09_lng,bd09_lat):
        x = bd09_lng - 0.0065
        y = bd09_lat - 0.006
        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * math.pi)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * math.pi)
        gcj02_lng = z * math.cos(theta)
        gcj02_lat = z * math.sin(theta)
        return gcj02_lng,gcj02_lat

    # GCJ坐标转WG84坐标
    def gcj02_to_wg84(self,gcj02_lng,gcj02_lat):
        mlng,mlat=self.transfrom(gcj02_lng,gcj02_lat)
        wg84_Lng=gcj02_lng*2-mlng
        wg84_Lat=gcj02_lat*2-mlat
        return wg84_Lng,wg84_Lat

    # 将百度坐标转WG84坐标
    def bd09_to_wg84(self,bd09_lng,bd09_lat):
        gcj02_lng, gcj02_lat=self.bd09_to_gcj02(bd09_lng,bd09_lat)
        return self.gcj02_to_wg84(gcj02_lng,gcj02_lat)

# 实例
# tr = Transfer()
# print(type(float(25.0)))
# print(tr.wg84_to_gcj02(float(25.0), float(30.0)))