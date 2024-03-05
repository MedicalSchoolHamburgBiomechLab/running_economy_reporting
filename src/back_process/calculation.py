import pandas as pd
from library.constants import PATH_SPIRO
from library import utils
import os
from datetime import datetime
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns


class EXERCISE:

    def __init__(self, start, end, VO2_KG, R, HF, VO2, VCO2, Af):
        self.start = start
        self.end = end
        self.VO2_KG = VO2_KG
        self.R = R
        self.HF = HF
        self.VO2 = VO2
        self.VCO2 = VCO2
        self.Af = Af

    def get_json(self):
        energetic_cost = peronnet_massicotte_1991(VCO2=self.VCO2 / 60000,
                                                  VO2=self.VO2 / 60000)  #  VO2 and VCO2 come in mL/min
        energetic_cost *= 1000  # formula returns in kJ/s -> Watts

        # workaround to get weight:
        weight = np.mean( self.VO2 / self.VO2_KG)
        energetic_cost = energetic_cost / weight  # Watts/kg

        data_to_json = {
            'start': self.start.strftime('%H:%M:%S'),
            'end': self.end.strftime('%H:%M:%S'),
            'VO2_KG': round(np.mean(self.VO2_KG), 2),
            'R': round(np.mean(self.R), 2),
            'HF': np.mean(self.HF),
            'energetic_cost_W_KG': round(np.mean(energetic_cost), 2),
            'Af': round(np.mean(self.Af), 2),
        }

        return data_to_json


def export_result(PATH_PROTOCOLE_FILE, PATH_SAVE_RESULT, TIMESTAMP_TAKEN, subject_id: str):
    """
    function that return a json file containing the number of exercice describe by start/end time, VO2/KG and R mean
    """
    df = pd.read_excel(PATH_PROTOCOLE_FILE, usecols=['t', 'Phase', 'VO2/Kg', 'VO2', 'VCO2', 'R', 'HF', 'Af'], skiprows=[1, 2])
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

    f, [ax_top, ax_bottom] = plt.subplots(2, 1, sharex=True)
    f.set_size_inches([34.4, 13.45])
    f.suptitle(subject_id)
    sns.lineplot(data=df, x='timestamp', y='HF', ax=ax_top)
    sns.lineplot(data=df, x='timestamp', y='VO2/Kg', ax=ax_bottom)
    ylim_top = ax_top.get_ylim()
    ylim_bottom = ax_bottom.get_ylim()

    # Create Exercice and store data
    json_result = {}
    for index, (start, end) in enumerate(sequences):
        index_3_min = df.index[df['timestamp'] >= df['timestamp'][end] - TIMESTAMP_TAKEN][0]
        index_last_min = df.index[df['timestamp'] >= df['timestamp'][end] - 60][0]

        # draw patch to indicate phases

        # phase x values
        x_patch_start_phase = df['timestamp'][start]
        x_patch_end_phase = df['timestamp'][end]
        patch_width_phase = x_patch_end_phase - x_patch_start_phase
        # HF x-values
        x_patch_start_hf = df['timestamp'][index_last_min]
        patch_width_hf = x_patch_end_phase - x_patch_start_hf
        # VO2 x-values
        x_patch_start_vo2 = df['timestamp'][index_3_min]
        patch_width_vo2 = x_patch_end_phase - x_patch_start_vo2

        # HF y-values
        y_patch_start_hf, y_patch_end = ax_top.get_ylim()
        patch_height_hf = y_patch_end - y_patch_start_hf
        # VO2 y-values
        y_patch_start_v02, y_patch_end = ax_bottom.get_ylim()
        patch_height_v02 = y_patch_end - y_patch_start_v02

        # PHASE
        ax_top.add_patch(plt.Rectangle((x_patch_start_phase, y_patch_start_hf),
                                       patch_width_phase, patch_height_hf, color='red', alpha=0.1))
        ax_bottom.add_patch(plt.Rectangle((x_patch_start_phase, y_patch_start_v02),
                                          patch_width_phase, patch_height_v02, color='red', alpha=0.1))
        # HF
        ax_top.add_patch(plt.Rectangle((x_patch_start_hf, y_patch_start_hf),
                                       patch_width_hf, patch_height_hf, color='yellow', alpha=0.2))
        # VO2
        ax_bottom.add_patch(plt.Rectangle((x_patch_start_vo2, y_patch_start_v02),
                                          patch_width_vo2, patch_height_v02, color='yellow', alpha=0.2))
        # Check number of value
        print(f" Number of samples : {end - index_3_min}")
        VO2_KG = df['VO2/Kg'][index_3_min:end]
        VCO2 = df['VCO2'][index_3_min:end]
        VO2 = df['VO2'][index_3_min:end]
        R = df['R'][index_3_min:end]
        HF = df['HF'][index_last_min:end]
        Af = df['Af'][index_3_min:end]

        exercise = EXERCISE(start=df['t'][start],
                            end=df['t'][end],
                            VO2_KG=VO2_KG,
                            R=R,
                            HF=HF,
                            VCO2=VCO2,
                            VO2=VO2,
                            Af=Af)
        results = exercise.get_json()
        json_result[f'Exercice_{index + 1}'] = results

        ax_top.plot((x_patch_start_hf, x_patch_end_phase), (results['HF'], results['HF']), 'k--')
        ax_bottom.plot((x_patch_start_vo2, x_patch_end_phase), (results['VO2_KG'], results['VO2_KG']), 'k--')

    ax_top.set_ylim(ylim_top)
    ax_bottom.set_ylim(ylim_bottom)

    # plt.show()
    plt.savefig(os.path.join(PATH_SAVE_RESULT, f'{subject_id}.png'))
    # Save JSON file
    with open(os.path.join(PATH_SAVE_RESULT, f'{subject_id}_out.json'), "w") as file:
        json.dump(json_result, file, indent=4)
    print("JSON saved ✅")
    # with open(os.path.join(PATH_SAVE_RESULT, f'out.txt'), "w") as file:
    #     json.dump(json_result, file, indent=4)
    # print("Text saved ✅")


def peronnet_massicotte_1991(VO2, VCO2):
    """Table of nonprotein respiratory quotient: an update. Peronnet F, Massicotte D. Can J Sport Sci. 1991;16(
    1):23-29.
     VO2 and VCO2 required in L/s"""
    return 16.89 * VO2 + 4.84 * VCO2


def main(subject_id: str):
    PATH_PROTOCOLE_FILE = os.path.join(PATH_SPIRO, subject_id, f'{subject_id}_protocol.xlsx')
    PATH_SAVE_RESULT = os.path.dirname(PATH_PROTOCOLE_FILE)
    TIMESTAMP_TAKEN = 3 * 60

    export_result(PATH_PROTOCOLE_FILE=PATH_PROTOCOLE_FILE, PATH_SAVE_RESULT=PATH_SAVE_RESULT,
                  TIMESTAMP_TAKEN=TIMESTAMP_TAKEN, subject_id=subject_id)


if __name__ == '__main__':
    ids = [f'RE{str(i).zfill(2)}' for i in range(1, 24)]
    # ids = ['RE09']
    for s_id in ids:
        print(s_id)
        try:
            main(s_id)
        except Exception as e:
            print(e)
