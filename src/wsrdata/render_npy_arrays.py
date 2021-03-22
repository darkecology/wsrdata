from wsrlib import pyart, radar2mat
import logging
import time


# inputs a txt file where each line is a scan name, e.g.
# KOKX20130721_093320_V06
# KTBW20031123_115217
def render_by_scan_list(filepath, scan_dir, array_dir, dualpol_dir):

    logger = logging.getLogger(__name__)
    filelog = logging.FileHandler(log_path)
    formatter = logging.Formatter('%(asctime)s [ %(fname)s ] : %(message)s')
    formatter.converter = time.gmtime
    filelog.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(filelog)
    logger = logging.LoggerAdapter(logger, {"fname": filepath})

    logger.info('***** Start rendering for %s *****' % (filepath))

    # Load all scans
    with open(filepath, 'r') as f:
        scans = f.readlines()

    not_s3 = []
    error_scans = []

    # download each scan
    for scan in scans:
        try:
            scan = '%s.gz' % (scan.strip())
            station = scan[0:4]
            year = scan[4:8]
            month = scan[8:10]
            date = scan[10:12]
            aws_key = '%s/%s/%s/%s/%s' % (year, month, date, station, scan)
            print(aws_key)
            logger.info('Downloading scan %s, aws key %s' % (scan, aws_key))
            download_scans([aws_key], out_dir)
        except ClientError as err:
            error_code = int(err.response['Error']['Code'])
            if error_code == 404:
                logger.error('Error Scan %s not found in s3, adding to list' % scan)
                not_s3.append(scan)
            else:
                logger.error('Exception while processing scan %s - %s' % (scan, str(err)))
                error_scans.append(scan)
        except Exception as ex:
            logger.error('Exception while processing scan %s - %s' % (scan, str(ex)))
            error_scans.append(scan)

    if len(not_s3) > 0:
        with open(not_s3_log_path, 'w') as f:
            f.write('\n'.join(not_s3))

    if len(error_scans) > 0:
        with open(error_scans_log_path, 'w') as f:
            f.write('\n'.join(error_scans))

    logger.info('***** Finished rendering for file %s *****' % (filepath))