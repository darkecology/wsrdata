from wsrlib import pyart, radar2mat
import logging
import time
import os
import numpy as np


# inputs a txt file where each line is a scan name, e.g.
# KOKX20130721_093320_V06
# KTBW20031123_115217
def render_by_scan_list(filepath, scan_dir,
                        array_render_config, array_attributes, array_dir, overwrite_array,
                        dualpol_render_config, dualpol_attributes, dualpol_dir, overwrite_dualpol):

    log_path = os.path.join(array_dir, "rendering.log")
        # this includes successful rendering for arrays and dualpol arrays
    array_error_log_path = os.path.join(array_dir, "errors.log")
    dualpol_error_log_path = os.path.join(dualpol_dir, "errors.log")

    logger = logging.getLogger(__name__)
    if not logger.handlers:
        filelog = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s [ %(fname)s ] : %(message)s')
        formatter.converter = time.gmtime
        filelog.setFormatter(formatter)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(filelog)
    logger = logging.LoggerAdapter(logger, {"fname": filepath})

    logger.info('***** Start rendering for %s *****' % (filepath))

    scans = [scan.strip() for scan in open(filepath, "r").readlines()] # Load all scans
    array_errors = [] # to record scans from which array rendering fails
    dualpol_errors = [] # to record scans from which dualpol array rendering fails

    # render arrays from scans
    for scan in scans:
        station = scan[0:4]
        year = scan[4:8]
        month = scan[8:10]
        date = scan[10:12]
        scan_file = os.path.join(scan_dir, '%s/%s/%s/%s/%s.gz' % (year, month, date, station, scan))

        if not os.path.exists(os.path.join(array_dir, scan+".npy")) or \
                not os.path.exists(os.path.join(dualpol_dir, scan+"_dualpol.npy")) or \
                overwrite_array or overwrite_dualpol:
            try:
                radar = pyart.io.read_nexrad_archive(scan_file)
                logger.info('Loaded scan %s' % scan)
            except Exception as ex:
                logger.error('Exception while loading scan %s - %s' % (scan, str(ex)))
                array_errors.append(scan)
                dualpol_errors.append(scan)
                continue

        if os.path.exists(os.path.join(array_dir, scan + ".npy")) and not overwrite_array:
            logger.info('A npy array already exists for scan %s' % scan)
        else:
            try:
                data, elevs, y, x = radar2mat(radar, **array_render_config)
                data = np.concatenate(tuple([data[attr] for attr in array_attributes]))
                with open(os.path.join(array_dir, scan+".npy"), "wb") as f:
                    np.save(f, data)
                logger.info('Rendered a npy array from scan %s' % scan)
            except Exception as ex:
                logger.error('Exception while rendering a npy array from scan %s - %s' % (scan, str(ex)))
                array_errors.append(scan)

        if os.path.exists(os.path.join(dualpol_dir, scan+"_dualpol.npy")) and not overwrite_dualpol:
            logger.info('A dual npy array already exists for scan %s' % scan)
        else:
            try:
                data, elevs, y, x = radar2mat(radar, **dualpol_render_config)
                data = np.concatenate(tuple([data[attr] for attr in dualpol_attributes]))
                with open(os.path.join(dualpol_dir, scan+"_dualpol.npy"), "wb") as f:
                    np.save(f, data)
                logger.info('Rendered a dualpol npy array from scan %s' % scan)
            except Exception as ex:
                logger.error('Exception while rendering a dualpol npy array from scan %s - %s' % (scan, str(ex)))
                dualpol_errors.append(scan)

    if len(array_errors) > 0:
        with open(array_error_log_path, 'a+') as f:
            f.write('\n'.join(array_errors)+'\n')
    if len(dualpol_errors) > 0:
        with open(dualpol_error_log_path, 'a+') as f:
            f.write('\n'.join(dualpol_errors)+'\n')

    logger.info('***** Finished rendering for file %s *****' % (filepath))