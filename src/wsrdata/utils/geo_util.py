import geopy
from geopy import distance
import numpy as np
from wsrdata.utils.nexrad_util import NEXRAD_LOCATIONS

def cart2pol(x, y):
    dis = np.sqrt(x ** 2 + y ** 2)
    angle = np.arctan2(y, x)
    return angle, dis

def rad2deg(angle):
    return angle * 180. / np.pi

def pol2cmp(angle):
    bearing = rad2deg(np.pi / 2 - angle)
    bearing = np.mod(bearing, 360)
    return bearing

def get_roost_coor(roost_xy, station_xy, station_name, distance_per_pixel, y_direction="image"):
    """
        Convert from image coordinates to geographic coordinates

        Args:
            roost_xy: image coordinates of roost center
            station_xy: image coordinates of station
            station_name: name of station, e.g., KDOX
            distance_per_pixel: geographic distance per pixel, unit: meter
            y_direction: image (big y means South, row 0 is North) or geographic (big y means North, row 0 is South)

        Return:
            longitude, latitide of roost center
    """
    station_lat, station_lon = NEXRAD_LOCATIONS[station_name]["lat"], NEXRAD_LOCATIONS[station_name]["lon"]
    x_offset = roost_xy[0] - station_xy[0]
    y_offset = -(roost_xy[1] - station_xy[1]) if y_direction == "image" else roost_xy[1] - station_xy[1]
    angle, dis = cart2pol(x_offset, y_offset)
    bearing = pol2cmp(angle)
    origin = geopy.Point(station_lat, station_lon)
    des = distance.distance(kilometers=dis * distance_per_pixel/ 1000.).destination(origin, bearing) 
    return des[1], des[0] # in order of lon and lat

