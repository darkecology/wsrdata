import os


# make sure all scans are successfully downloaded
print("Printing scans that are not downloaded...")
scan_dir = "../../static/scans/scans"
filepath = "../../static/scan_lists/v0.1.0/scan_list.txt"
scans = [scan.strip() for scan in open(filepath, "r").readlines()]
for scan in scans:
    station = scan[0:4]
    year = scan[4:8]
    month = scan[8:10]
    date = scan[10:12]
    scan_file = os.path.join(scan_dir, '%s/%s/%s/%s/%s.gz' % (year, month, date, station, scan))
    assert os.path.exists(scan_file)


# rendering exceptions from rendering.log
filepath = "rendering.log" # "../static/arrays/v0.1.0/rendering.log"
logs = [log.strip().split(" : ")[1] for log in open(filepath, "r").readlines()]
with open("rendering_exceptions.txt", "w") as f:
    f.writelines([log+"\n" for log in logs \
                  if log.startswith("Exception") and \
                  not (log.startswith("Exception while rendering a dualpol npy array from scan") and \
                       log.endswith("\'differential_reflectivity\'")
                       )
                  ])

