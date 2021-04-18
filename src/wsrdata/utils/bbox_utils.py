# The default target_scale_factor is average sheldon factor
def scale_XYWH_box(bbox, annotator_scale_factor, target_scale_factor=0.7429):
    radius = [bbox[2] / 2, bbox[3] / 2]
    new_radius = [r / annotator_scale_factor * target_scale_factor for r in radius]
    center = [(2 * bbox[0] + bbox[2] - 1) / 2, (2 * bbox[1] + bbox[3] - 1) / 2]

    new_left = int(center[0] - new_radius[0])
    new_right = center[0] * 2 - new_left
    new_top = int(center[1] - new_radius[1])
    new_bottom = center[1] * 2 - new_top
    return [new_left, new_top, new_right - new_left + 1, new_bottom - new_top + 1]