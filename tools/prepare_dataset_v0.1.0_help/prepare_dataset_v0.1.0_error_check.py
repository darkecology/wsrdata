import os


# make sure all scans are successfully downloaded
print("Printing scans that are not downloaded...")
scan_dir = "../../static/scans/scans"
for split in ["train.txt", "val.txt", "test.txt"]:
    filepath = os.path.join("../../static/splits/v1.0.0/", split)
    scans = [scan.strip() for scan in open(filepath, "r").readlines()]
    for scan in scans:
        station = scan[0:4]
        year = scan[4:8]
        month = scan[8:10]
        date = scan[10:12]
        scan_file = os.path.join(scan_dir, '%s/%s/%s/%s/%s.gz' % (year, month, date, station, scan))
        assert os.path.exists(scan_file)


# rendering exceptions from rendering.log
filepath = "rendering.log" # "../static/arrays/v1.0.0/rendering.log"
logs = [log.strip().split(" : ")[1] for log in open(filepath, "r").readlines()]
with open("rendering_exceptions.txt", "w") as f:
    f.writelines([log+"\n" for log in logs \
                  if log.startswith("Exception") and \
                  not (log.startswith("Exception while rendering a dualpol npy array from scan") and \
                       log.endswith("\'differential_reflectivity\'")
                       )
                  ])

# The rest of the script is only for checking the correctness of the rendering code:
# Scans in errors.log should be mentioned in rendering.log;
# there should not be any exception but print to txt files if so
"""
logs = [log for log in logs if log.startswith("Exception")]
scans_failed_to_render = set([log.split("scan ")[1].split(" - ")[0] for log in logs])

failed_arrays = [log.strip() for log in open("array_error_scans.log", "r").readlines()]
weird_failed_arrays = []
for failed_array in failed_arrays:
    if failed_array not in scans_failed_to_render:
        weird_failed_arrays.append(failed_array+"\n")
with open("weird_failed_arrays.txt", "w") as f:
    f.writelines(weird_failed_arrays)

failed_dualpol = [log.strip() for log in open("dualpol_error_scans.log", "r").readlines()]
weird_failed_dualpol = []
for failed_array in failed_dualpol:
    if failed_array not in scans_failed_to_render:
        weird_failed_dualpol.append(failed_array+"\n")
with open("weird_failed_dualpol.txt", "w") as f:
    f.writelines(weird_failed_dualpol)
"""
