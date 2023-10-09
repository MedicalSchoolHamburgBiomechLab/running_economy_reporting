# MERGE Script for REPORT GENERATION
import pandas as pd

from library.constants import *
from report import report
import os
import json
from src.back_process import update_data_table
import numpy as np


class Subject:
    def __init__(self, ID):
        self.ID = ID
        self.set_personal_information()
        self.set_info_from_excel()
        self.set_data_excel()

    def set_personal_information(self, first_name='null', second_name='null'):
        self.first_name = first_name
        self.second_name = second_name

    def set_info_from_excel(self):
        self.info = pd.read_excel(PATH_EXCEL, index_col=0).loc[self.ID, :]
        self.session_date = self.info['session_date'].strftime('%d.%m.%Y')
        self.sb_distance = self.info['sb_distance']
        self.sb_time = self.info['sb_time']
        self.speed_kph = self.info['speed kph']
        self.DOB = self.info['dob']
        self.height = self.info['height']
        self.weight = self.info['weight']

    def set_data_excel(self):
        order = self.info['order_nike':'order_individual_3'].sort_values(ascending=True).dropna()

        # Check the link between order and shoes value --> avoid Nan indivual shoe
        for i in range(1, 4):
            if str(self.info[f'individual_{i}']) == 'nan':
                try:
                    del (order[f'order_individual_{i}'])
                except:
                    continue

        order[:] = range(1, len(order) + 1)

        self.data_excel = pd.DataFrame()
        for i, shoe in enumerate(order.index):
            print(i)
            ind = '_'.join(shoe.split('_')[1:])
            match ind:
                case 'individual_1':
                    name = self.info['individual_1']
                case 'individual_2':
                    name = self.info['individual_2']
                case 'individual_3':
                    name = self.info['individual_3']
                case 'ascis':
                    ind = 'asics'
                    name = 'Asics Metaspeed'
                case 'nike':
                    name = 'Nike Alphafly Next%'
                case 'puma':
                    name = 'Puma Nitro Elite'
            try:
                picture_name = name.rstrip().replace(' ', '_')
                print(name)
                self.data_excel.loc[' ', name] = os.path.join(r'assets', f'{picture_name}.png')
                # self.data_excel.loc['Order', name] = self.info[shoe]
                self.data_excel.loc['Weight_g', name] = self.info.loc[f'weight_{ind}']
                self.data_excel.loc['VO2_ml_min_kg', name] = round(self.info.loc[f'economy_{i + 1} [ml/min/kg]'], 1)
                self.data_excel.loc['VO2_ml_km_kg', name] = round(self.data_excel.loc['VO2_ml_min_kg', name] / (
                        self.speed_kph / 60), 1)
                self.data_excel.loc['HR_bpm', name] = round(self.info.loc[f'HR_{i + 1}'], 1)
                self.data_excel.loc['RPE_6_20', name] = self.info.loc[f'BORG_{i + 1}'].astype(int)
                self.data_excel.loc['Comfort_1_10', name] = self.info.loc[f'comfort_{i + 1}'].astype(int)
                self.data_excel.loc['Lactate_mmol_l', name] = self.info.loc[f'lactate_{i + 1}']

                self.data_excel.loc['Size_US', name] = self.info.loc[f'us_size_{ind}']
                self.data_excel.loc['Cadence', name] = self.info.loc[f'cadence_{i + 1}']
            except:
                continue
        max_vo2 = max(self.data_excel.loc['VO2_ml_km_kg', :])
        for column in self.data_excel.columns:
            if self.data_excel.loc['VO2_ml_km_kg', column] == max_vo2:
                self.data_excel.loc['VO2_ml_km_kg', column] = f"{self.data_excel.loc['VO2_ml_km_kg', column]} (Ref.)"
            else:
                vo2_variation = round(100 / max_vo2 * (self.data_excel.loc['VO2_ml_km_kg', column] - max_vo2), 1)
                self.data_excel.loc[
                    'VO2_ml_km_kg', column] = f"{self.data_excel.loc['VO2_ml_km_kg', column]} ({vo2_variation})"

    def generate_json(self, name_json: str = 'data', path_json: str = PATH_PROJECT) -> str:
        data_to_json = {
            'ID': self.ID,
            'first_name': self.first_name,
            'second_name': self.second_name,
            'DOB': self.DOB.isoformat(),
            'height': self.height,
            'weight': self.weight,
            'date_visit': self.session_date,
            'sb_distance': self.sb_distance,
            'sb_time': self.sb_time.isoformat(),
            'speed_kph': self.speed_kph,
            'data': self.data_excel.to_dict(),
        }

        json_dumps = json.dumps(data_to_json, indent=4)

        # Save JSON file
        os.makedirs(path_json, exist_ok=True)
        with open(os.path.join(path_json, f'{name_json}.json'), "w") as file:
            file.write(json_dumps)
        print("JSON saved ✅")

        return os.path.join(path_json, f'{name_json}.json')


if __name__ == '__main__':
    # TODO:
    #                              !!!!!! MAKE SURE THAT THE CONSTANTS PATH ARE WELL SET !!!!!!

    update_data_table.update_cadence(_id='RE05')
    subject = Subject('RE05')
    path_json = subject.generate_json(f'data_{subject.ID}', path_json=os.path.join(PATH_PROJECT, 'result'))
    report.main(path_json)
