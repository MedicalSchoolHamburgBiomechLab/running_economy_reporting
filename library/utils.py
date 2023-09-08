import os
import json
import warnings
from scipy.interpolate import interp1d
from scipy.stats import zscore
import numpy as np
import c3d
import h5py
from .constants import DEBUG_MODE
from sys import platform


def get_cpu_core_count(adj: int = -1):
    if DEBUG_MODE:
        return 1
    if adj > 0:
        adj = 0
        warnings.warn('cpu count to use can only be adjusted by negative values')
    cnt = os.cpu_count()
    if 'win' in platform:
        return int(cnt / 2) + adj
    return cnt + adj


def load_dict_from_hdf5(filename):
    with h5py.File(filename, 'r') as h5file:
        return recursively_load_dict_contents_from_group(h5file, '/')


def recursively_load_dict_contents_from_group(h5file, path):
    ans = {}
    try:
        for key, item in h5file[path].items():
            if isinstance(item, h5py._hl.dataset.Dataset):
                if item.shape:
                    ans[key] = item[:]
                else:
                    # ans[key] = np.array([0])
                    ans[key] = item.asstr()[()]
            elif isinstance(item, h5py._hl.group.Group):
                ans[key] = recursively_load_dict_contents_from_group(h5file, path + key + '/')
    except Exception as e:
        print(e)
    return ans


def save_dict_to_hdf5(dic, filename):
    with h5py.File(filename, 'w') as h5file:
        recursively_save_dict_contents_to_group(h5file, '/', dic)


def recursively_save_dict_contents_to_group(h5file, path, dic):
    for key, item in dic.items():
        if isinstance(item, (np.ndarray, np.int64, np.float64, str, bytes)):
            h5file[path + key] = item
        elif isinstance(item, dict):
            recursively_save_dict_contents_to_group(h5file, path + key + '/', item)
        else:
            h5file[path + key] = []
            # raise ValueError('Cannot save %s type'%type(item))


def load_c3d(file_path: str, system: str = 'qualisys'):
    # v = sys.version
    # if int(v[2]) < 6:
    #     raise SystemError('This function is only compatible with Python3 Version <= 3.6')
    with open(file_path, 'rb') as handle:
        reader = c3d.Reader(handle)
        try:
            point_labels = reader.point_labels
            point_labels = [pl.replace(" ", "") for pl in point_labels]
        except Exception as err:
            point_labels = []
            print(err)

        data = dict()
        meta = dict()

        try:
            # todo: consider recursive reading as with hdf5
            for key, values in reader.groups.items():
                if not isinstance(key, str):
                    continue
                meta[key] = dict()
                if not isinstance(values, c3d.Group):
                    # todo: check for params
                    continue
                for k, v in values.params.items():
                    if not isinstance(v, c3d.Param):
                        continue
                    meta[key][k] = get_proper_param_value(v)
                # if key == "FORCE_PLATFORM":
                #     fp = values.params
                #     data['force_platform'] = dict()
                #     data['force_platform']['USED'] = fp['USED'].uint16_value
                #     data['force_platform']['ZERO'] = fp['ZERO'].float_value
                #     data['force_platform']['TYPE'] = fp['TYPE'].uint16_array
                #     data['force_platform']['CORNERS'] = fp['CORNERS'].float_array
                #     data['force_platform']['ORIGIN'] = fp['ORIGIN'].float_array
                #     data['force_platform']['CHANNEL'] = fp['CHANNEL'].int16_array
                #     break
        except Exception as err:
            print(err)

        data['marker'] = dict.fromkeys(point_labels)
        data['analog'] = None
        data['analog_rate'] = reader.analog_rate
        data['point_rate'] = reader.point_rate
        try:
            data['creation_date'] = reader.get('PROCESSING').get_string('CREATION DATE')
            data['creation_time'] = reader.get('PROCESSING').get_string('CREATION TIME')
        except Exception as err:
            print(err)
        # ratio = int(reader.analog_rate/reader.point_rate)
        for i, points, analog in reader.read_frames():
            for m, marker in enumerate(point_labels):
                data['marker'][marker] = points[m, :3] if np.all(data['marker'][marker] is None) \
                    else np.vstack((data['marker'][marker], points[m, :3]))
            if np.all(data['analog'] is None):
                data['analog'] = analog.T
            else:
                data['analog'] = np.vstack((data['analog'], analog.T))

    return data, meta


def get_proper_param_value(p: c3d.Param):
    # todo: implement
    # get data type
    # return correct instance of parameter
    return p


def get_file_list(path: str, extension: str = None, sort: bool = False):
    file_list = os.listdir(path)
    if "images" in extension:
        extension = ["jpg", "jpeg", "png", "bmp", "svg"]
    else:
        extension = [extension]
    if sort:
        file_list.sort()
    if extension is not None:
        files_out = [os.path.join(path, f) for f in file_list if any(ext in f for ext in extension)]
    else:
        files_out = [os.path.join(path, f) for f in file_list]
    return files_out


def get_folder_list(path: str, absolute: bool = False, sort: bool = False):
    folders_list = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    if sort:
        folders_list.sort()
    if absolute:
        folders_list = [os.path.join(path, f) for f in folders_list]
    return folders_list


def get_subject_folder_list(path: str, sort: bool = False, prefix: str = 'S', absolute: bool = False, ):
    subjects = get_folder_list(path=path, absolute=False, sort=sort)
    subjects = [s for s in subjects if (s.startswith(prefix) & (s[len(prefix):].isnumeric()))]
    if absolute:
        subjects = [os.path.join(path, s) for s in subjects]
    return subjects


def json_to_dict(path: str):
    with open(path) as json_file:
        data = json.load(json_file)
    return data


def key_from_value(dictionary: dict, value):
    keys_list = []
    for key, val in dictionary.items():
        if val == value:
            # found the key
            keys_list.append(key)
    if not keys_list:
        return None
    elif len(keys_list) == 1:
        return keys_list[0]
    else:
        return keys_list


def outlier_check_signal(signal: np.ndarray):
    threshold = 10
    signal_norm = zscore(signal)
    outliers = np.where((abs(signal_norm) > threshold))

    # import matplotlib.pyplot as plt
    # plt.plot(signal_norm)
    # plt.hlines(10, 0, len(signal_norm))
    # plt.hlines(-10, 0, len(signal_norm))
    # plt.scatter(outliers, signal_norm[outliers], color='r')
    # plt.show()

    return outliers


# function to get unique values from a list
def unique_from_list(my_list: list):
    x = np.array(my_list)
    return np.unique(x).tolist()


def normalize_to_stance(sig: np.ndarray, ic: int = 0, tc: int = -1, n_samples: int = 101, axis=0):
    if len(sig.shape) > 1:
        if axis == 0:
            sig_in = sig[ic:tc, :].copy()
        elif axis == 1:
            sig_in = sig[:, ic:tc].copy().T
    else:
        sig_in = sig[ic:tc].copy()
    return resample(sig=sig_in, n_samples=n_samples)


def resample(sig: np.ndarray, n_samples: int = 101, axis=0):
    if len(sig.shape) > 1:
        if axis == 0:
            sig_in = sig.copy()
        elif axis == 1:
            sig_in = sig.copy().T
    else:
        sig_in = sig.copy()
    length = sig_in.shape[0]
    n = 100  # arbitrary
    timebase = np.linspace(0, n, length)
    new_timebase = np.linspace(0, n, n_samples)
    func = interp1d(timebase, sig_in, axis=0)
    return func(new_timebase)


if __name__ == '__main__':
    path = ''
    files = get_file_list(path)
    data, meta = load_c3d(files[-1], ".c3d", True)
