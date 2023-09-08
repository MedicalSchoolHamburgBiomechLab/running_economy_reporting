import numpy as np


def get_foot_events(f_z, sample_rate, threshold=10):
    ic_frame = get_ic_frame(f_z=f_z, sample_rate=sample_rate, threshold=threshold)
    if ic_frame < 0:
        ic_frame = 0
    # tc_frame = len(f_z) - get_ic_frame(f_z=np.flip(f_z), sample_rate=sample_rate, threshold=threshold) - 1
    tc_frame = get_tc_frame(f_z, ic_frame, threshold=threshold)
    return ic_frame, tc_frame


def get_tc_frame(f_z, ic_frame, threshold=10):
    # go backwards until there is no value underneath the threshold between TC and IC
    # IMPORTANT: Assumption that f_z[ic] is defined as last frame under threshold
    tc = len(f_z) - 1
    while np.nanmin(f_z[ic_frame+1:tc]) < threshold:
        tc -= 1
        if tc == ic_frame:
            break
    return tc + 1


def get_ic_frame(f_z, sample_rate, threshold=10):
    frame = 0
    ic = 1
    window = int(sample_rate / 10)  # 10th of second as window
    while frame == 0:
        if ic >= (len(f_z) - 1):
            return 0
        if f_z[ic] >= threshold:
            if np.min(f_z[ic:(ic + window)]) > threshold:
                frame = ic
            else:
                ic += 1
        else:
            ic += 1

    return frame-1