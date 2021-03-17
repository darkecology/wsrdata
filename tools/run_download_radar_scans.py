""" Downloading radar scans from AWS server """

from wsrdata import download_radar_scans
import argparse
import sys


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download radar scans')
    parser.add_argument('--target', dest='target',
                        help="""search the roost around a city (e.g. Boston) or a region (e.g. east US), 
                              select from [city, east, listfile, station, station_list], modify lib/nexrad_util.py to 
                              add more regions""",
                        default='city', type=str, required=True)
    parser.add_argument('--lat', dest='lat', 
                        help='the lat of a place where we search its surrounding roosts',
                        default= None, type=float)
    parser.add_argument('--lon', dest='lon', 
                        help='the longitude of a place where we search its surrounding roosts',
                        default= None, type=float)
    parser.add_argument('--radius', dest='radius', 
                        help='the radius of the region surrounding a place to search the roosts (Kilometers)',
                        default= 150, type=float)
    parser.add_argument('--from', dest='start_date',
                        help='the start date to download radar scans (time zone: UTC), format: 20190502',
                        default= None, type=str)
    parser.add_argument('--to', dest='end_date',
                        help='the end date to download radar scans (time zone: UTC), format: 20190505',
                        default= None, type=str)
    parser.add_argument('--fpath', dest='listfile',
                        help='a file contains lines with format station yyyy mm dd',
                        default= None, type=str)
    parser.add_argument('--station', dest='station',
                        help='name of radar station, e.g., KDOX',
                        default= None, type=str)
    parser.add_argument('--station_list', dest='station_list',
                        help='a list of radar stations, e.g., [KDOX, KAMX]',
                        nargs='+',
                        default= None)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if args.target not in ['city', 'east', 'listfile', 'station', 'station_list']:
        print('Please specify one of the target from [city, east, listfile, station, station_list]')
        sys.exit(1)
    elif args.target in ['city', 'east', 'station', 'station_list']:
        if args.start_date is None or args.end_date is None:
            print('Please specify the start date and end date before downloading the radar scans')
            sys.exit(1)

    if args.target == 'city':
        if (args.lat is not None) and (args.lon is not None) :
            download_radar_scans.dl_by_place_multiprocess((args.lat, args.lon), args.start_date, args.end_date, args.radius)
        else:
            print('Please specify the latitude and longitude of the city.')
            sys.exit(1)
    elif args.target == 'listfile':
        if args.listfile is not None:
            download_radar_scans.dl_by_list(args.listfile)
        else:
            print('Please specify the file path')
            sys.exit(1)
    elif args.target == 'station':
        if args.station is not None:
            download_radar_scans.dl_by_station(args.station, args.start_date, args.end_date)
        else:
            print('Please specify the name of the radar station')
            sys.exit(1)
    elif args.target == 'station_list':
        if args.station_list is not None:
            download_radar_scans.dl_by_station_list(args.station_list, args.start_date, args.end_date)
        else:
            print('Please specify the name of the radar stations')
            sys.exit(1)
    else:
        download_radar_scans.dl_by_region_multiprocess(args.target, args.start_date, args.end_date)
        # download_radar_scans.dl_by_region(args.target, args.start_date, args.end_date)
