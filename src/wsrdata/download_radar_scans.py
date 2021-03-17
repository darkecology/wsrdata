import sys
import os
import os.path as osp
import re
from datetime import datetime, timedelta
from utils.sunset_util import get_sunset_sunrise_time
from utils.s3_util import get_scans, download_scans
import calendar
import pytz
from botocore.exceptions import ClientError
import time
import logging
import utils.nexrad_util as nexrad
import utils.geo_util as geo_util
from roost.config import cfg
from roost.config_function import get_config
import utils.fileOperator as fileUtil
from progress.bar import Bar # progress bar
import multiprocessing


def format_time(start_date_string, end_date_string):
    # INPUT: yyyymmdd, yyyymmdd
    # OUTPUT: datetime object
    year1 = int(start_date_string[:4])
    month1 = int(start_date_string[4:6])
    day1 = int(start_date_string[6:])
    year2 = int(end_date_string[:4])
    month2 = int(end_date_string[4:6])
    day2 = int(end_date_string[6:])
    # the start day and last day is 2 days before/after the specified date
    first_day = 1
    if day1 - 2 > first_day:
        first_day = day1 - 2
    tup = calendar.monthrange(year2, month2)
    last_day = tup[1]
    if day2 + 2 < last_day:
        last_day = day2+2
    start_date = datetime(year1, month1, first_day, 0, 0, 0, 0, tzinfo=pytz.utc) - timedelta(days=1)
    end_date = datetime(year2, month2, last_day, 0, 0, 0, 0, tzinfo=pytz.utc)
    return start_date, end_date


def total_days(start_date, end_date):
    return abs((start_date - end_date).total_seconds() / 3600. / 24.)

# Download function(station, start_date, end_date):
def download(station, start_date, end_date):

    img_dir = cfg.SCAN_DIR
    not_s3_dir = osp.join(img_dir, 'not_s3')
    error_scans_dir = osp.join(img_dir, 'error_scans')

    fileUtil.mkdir(img_dir)
    fileUtil.mkdir(not_s3_dir)
    fileUtil.mkdir(error_scans_dir)

    current_date = start_date
    not_s3 = []
    error_scans = []

    bar = Bar(station, max = total_days(start_date, end_date)) 
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        sunset, sunrise = get_sunset_sunrise_time(station, date_str)
        start_time = sunrise - timedelta(minutes=30)
        end_time = sunrise + timedelta(minutes=180)

        scans = get_scans(start_time, end_time, [station], with_station=False)
        scans = set(scans)
        for scan in scans:
            try:
                download_scans([scan], img_dir)
            except ClientError as err :
                error_code = int(err.response['Error']['Code'])
                if error_code == 404:
                    not_s3.append(scan)
                else:
                    error_scans.append(scan)
            except Exception as ex:
                error_scans.append(scan)
        current_date += timedelta(days=1)
        bar.next()
    bar.finish()

    if len(not_s3) > 0:
        not_s3_file = '%s/%s_%s'%(not_s3_dir, start_date, end_date)
        with open(not_s3_file, 'w') as f:
            f.write('\n'.join(not_s3))

    if len(error_scans) > 0:
        error_scans_file = '%s/%s_%s'%(error_scans_dir, start_date, end_date)
        with open(error_scans_file, 'w') as f:
            f.write('\n'.join(error_scans))
        

#1 Download the radar scans by coordinates of place and date, e.g. dl_by_place((42.3601, -71.0589))
def nearby_radars(coor, radius_in_km = 150):
    station_list = []
    NEXRAD_list = nexrad.NEXRAD_LOCATIONS
    for radar_name, coor_info in NEXRAD_list.items():
        station_coor = (coor_info['lat'], coor_info['lon'])
        if geo_util.geo_dist(coor, station_coor) <= radius_in_km:
            station_list.append(radar_name)
    fileUtil.mkdir(cfg.ROOST_DEMO_DATA_DIR)
    with open(cfg.STATION_LIST, 'w') as f:
        for station in station_list:
            f.write("%s\n" % station)
    return station_list

def dl_by_place(coor, start_date_string, end_date_string, radius_in_km):
    start_date, end_date = format_time(start_date_string, end_date_string)
    station_list = nearby_radars(coor, radius_in_km)
    if len(station_list) == 0:
        print('No radar stations in the specified neighbor, try increase the radius!')
        return False
    else:
        for station in station_list:
            download(station, start_date, end_date)
    return True


#2 Download scans indicated in a given list, e.g. dl_by_list('radar_scan_list.txt')
def dl_by_list(list_file):
    # list_file: station year month day
    # read files
    with open(list_file, 'r') as f:
        data_list = f.readlines()
    for item in data_list:
        station, year, month, day = item.split(' ')
        start_date, end_date = format_time(year+month+day, year+month+day)  
        download(station, start_date, end_date)
    return True


#3 Download scans based on regiones, e.g. dl_by_region('east', '20180701', '20190501')
def dl_by_region(region, start_date_string, end_date_string):
    if region not in nexrad.STATION_REGIONS.keys():
        print('ERROR: No such region recored!')
        return False
    else:
        station_list = nexrad.STATION_REGIONS[region]
        start_date, end_date = format_time(start_date_string, end_date_string)
        for station in station_list:
            download(station, start_date, end_date)
    # move all downloaded files to a same dictionary for convinience
    return True

#4 Download scans based on station
def dl_by_station(station, start_date_string, end_date_string):
    start_date, end_date = format_time(start_date_string, end_date_string)
    download(station, start_date, end_date)
    return True

#5 Download scans based on a list of stations
def dl_by_station_list(station_list, start_date_string, end_date_string):
    start_date, end_date = format_time(start_date_string, end_date_string)
    jobs = []
    for station in station_list:
        process = multiprocessing.Process(target=download,
                                      args=(station, start_date, end_date))
        jobs.append(process)
    # Start the processes
    for j in jobs:
        j.start()
    # Ensure all of the processes have finished
    for j in jobs:
        j.join()

    return True

# Parallelly download scans for difference radar stations
def dl_by_region_multiprocess(region, start_date_string, end_date_string):
    if region not in nexrad.STATION_REGIONS.keys():
        print('ERROR: No such region recored!')
        return False
    else:
        station_list = nexrad.STATION_REGIONS[region]
        start_date, end_date = format_time(start_date_string, end_date_string)
        jobs = []
        for station in station_list:
            process = multiprocessing.Process(target=download,
                                          args=(station, start_date, end_date))
            jobs.append(process)
        # Start the processes
        for j in jobs:
            j.start()
        # Ensure all of the processes have finished
        for j in jobs:
            j.join()
    return True


def dl_by_place_multiprocess(coor, start_date_string, end_date_string, radius_in_km):
    start_date, end_date = format_time(start_date_string, end_date_string)
    station_list = nearby_radars(coor, radius_in_km)
    if len(station_list) == 0:
        print('No radar stations in the specified neighbor, try increase the radius!')
        return False
    else:
        jobs = []
        for station in station_list:
            process = multiprocessing.Process(target=download,
                                          args=(station, start_date, end_date))
            jobs.append(process)
        # Start the processes
        for j in jobs:
            j.start()
        # Ensure all of the processes have finished
        for j in jobs:
            j.join()
    return True





