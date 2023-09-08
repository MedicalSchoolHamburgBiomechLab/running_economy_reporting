import library.kinetics.force_events as fe

import library.utils as ut
import numpy as np
from scipy.signal import find_peaks
# from KiNetBlue.gait_events import get_cadence_estimate

CHANNEL_INDEX_RAW = ['force', 'cop_x', 'cop_y', 'sync']
CHANNEL_INDEX_GAIT_MODE = ['belt_velocity',
                           'left_foot_force',
                           'left_foot_cop_x',
                           'left_foot_cop_y',
                           'left_foot_max_pressure',
                           'left_foot_cop_x_loc',
                           'left_foot_cop_y_loc',
                           'right_foot_force',
                           'right_foot_cop_x',
                           'right_foot_cop_y',
                           'right_foot_max_pressure',
                           'right_foot_cop_x_loc',
                           'right_foot_cop_y_loc',
                           'sync']


def get_force_events_treadmill(f_z: np.ndarray, sample_rate: int, threshold: float = 10.0, offset_corr: bool = False):
    step_freq = 3.5
    peaks, _ = find_peaks(f_z, distance=(0.8 * sample_rate) / step_freq)
    mid = np.diff(peaks)
    mid = (peaks[:-1] + mid / 2).astype(int)
    ic_list = list()
    tc_list = list()
    for i, m in enumerate(mid):
        if i == (len(mid) - 1):
            break
        p = mid[i + 1]
        step = f_z[m:p]
        if offset_corr:
            step -= np.mean(np.sort(step)[:10])
        ic, tc = fe.get_foot_events(step, sample_rate=sample_rate, threshold=threshold)
        ic_list.append(ic + m)
        tc_list.append(tc + m)
    return {'ic': ic_list, 'tc': tc_list}


def get_zebris_force(c3d_data: dict):
    if c3d_data['analog'].shape[1] == 14:
        i1 = CHANNEL_INDEX_GAIT_MODE.index('right_foot_force')
        i2 = CHANNEL_INDEX_GAIT_MODE.index('left_foot_force')
        return np.array(c3d_data['analog'][:, i1]) + np.array(c3d_data['analog'][:, i2])
    elif c3d_data['analog'].shape[1] == 4:
        i1 = CHANNEL_INDEX_RAW.index('force')
        return np.array(c3d_data['analog'][:, i1])
    else:
        raise ValueError('Unexpected number of analog channels found')



if __name__ == '__main__':
    # path = "PATH_TO_ZEBRIS_C3D"
    path = 'D:\willi\Documents\TIS 5\Stage\SIP_project\SmartInjuryPrevention\QTM\TheiData\SmartInjury_c3d\Zelbris\S001/2021-10-28-15-54_RunTMMID.c3d'
    data, meta = ut.load_c3d(path)
    force = data['analog'][:, 0]
    events = get_force_events_treadmill(f_z=force, sample_rate=300)

    will = 1
