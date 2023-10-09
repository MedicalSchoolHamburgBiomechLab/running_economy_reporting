import pandas as pd
from library.constants import PATH_SPIRO
from library import utils
import os
from datetime import datetime
import numpy as np
import json


class EXERCICE:

    def __init__(self, start, end, VO2_KG, R):
        self.start = start
        self.end = end
        self.VO2_KG = VO2_KG
        self.R = R

    def get_json(self):
        data_to_json = {
            'start': self.start.strftime('%H:%M:%S'),
            'end': self.end.strftime('%H:%M:%S'),
            'VO2_KG': round(np.mean(self.VO2_KG), 2),
            'R': round(np.mean(self.R), 2),
        }

        return data_to_json


def export_result(PATH_PROTOCOLE_FILE, PATH_SAVE_RESULT, TIMESTAMP_TAKEN, subject_id: str):
    """
    function that return a json file containing the number of exercice describe by start/end time, VO2/KG and R mean
    """
    df = pd.read_excel(PATH_PROTOCOLE_FILE, usecols=['t', 'Phase', 'VO2/Kg', 'R'], skiprows=[1, 2])
    tab_timestamp = []
    for value in df['t']:
        tab_timestamp.append(datetime.combine(datetime.today().date(), value).timestamp())
    df['timestamp'] = tab_timestamp

    # Get exercice phase start and end index
    exercise_mask = df['Phase'] == 'EXERCISE'
    shifted_mask = exercise_mask.shift()
    shifted_mask = shifted_mask.fillna(False)
    start_indices = df.index[exercise_mask & (~shifted_mask.astype(bool))]
    end_indices = df.index[(~exercise_mask) & shifted_mask.astype(bool)] - 1
    sequences = list(zip(start_indices, end_indices))

    # Create Exercice and store data
    json_result = {}
    for index, (start, end) in enumerate(sequences):
        index_3_min = df.index[df['timestamp'] >= df['timestamp'][end] - TIMESTAMP_TAKEN][0]

        # Check number of value
        print(f" Number of samples : {end - index_3_min}")

        VO2_KG = df['VO2/Kg'][index_3_min:end]
        R = df['R'][index_3_min:end]
        json_result[f'Exercice_{index + 1}'] = EXERCICE(start=df['t'][start], end=df['t'][end], VO2_KG=VO2_KG,
                                                        R=R).get_json()

    # Save JSON file
    with open(os.path.join(PATH_SAVE_RESULT, f'{subject_id}_out.json'), "w") as file:
        json.dump(json_result, file, indent=4)
    print("JSON saved ✅")
    # with open(os.path.join(PATH_SAVE_RESULT, f'out.txt'), "w") as file:
    #     json.dump(json_result, file, indent=4)
    # print("Text saved ✅")


def main(subject_id: str):
    PATH_PROTOCOLE_FILE = os.path.join(PATH_SPIRO, subject_id, f'{subject_id}_protocol.xlsx')
    PATH_SAVE_RESULT = os.path.dirname(PATH_PROTOCOLE_FILE)
    TIMESTAMP_TAKEN = 3 * 60

    export_result(PATH_PROTOCOLE_FILE=PATH_PROTOCOLE_FILE, PATH_SAVE_RESULT=PATH_SAVE_RESULT,
                  TIMESTAMP_TAKEN=TIMESTAMP_TAKEN, subject_id=subject_id)


if __name__ == '__main__':
    # ids = [f'RE{str(i).zfill(2)}' for i in range(1, 12)]
    ids = ['RE09']
    for s_id in ids:
        print(s_id)
        try:
            main(s_id)
        except Exception as e:
            print(e)
