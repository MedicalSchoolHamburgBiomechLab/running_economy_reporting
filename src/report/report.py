import pandas as pd
import os
import datetime

try:
    import weasyprint
    from weasyprint.text.fonts import FontConfiguration
except OSError as e:
    raise OSError(
        'Have you installed GTK? If not, check here: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases')
from jinja2 import Environment

import json
from typing import Dict, Any
from library.constants import PATH_PROJECT
import webbrowser

def render_report(template_vars: dict, path_report: str = os.path.dirname(os.path.abspath(__file__))):
    # Load HTML template

    with open(os.path.join(PATH_PROJECT, 'src', 'report', 'templates','report_A4.html'), "r") as html:
        html_str = html.read()
    template = Environment().from_string(html_str)

    html_out = template.render(template_vars)
    stylesheet = os.path.join(PATH_PROJECT, 'src', 'report', 'css','style_A4.css')
    font_config = FontConfiguration()
    base_url = os.path.dirname(os.path.realpath(__file__))
    css = weasyprint.CSS(filename=stylesheet, base_url=base_url, font_config=font_config)
    html = weasyprint.HTML(string=html_out, base_url=base_url)
    os.makedirs(path_report, exist_ok=True)
    path_report = os.path.join(path_report, f'report_{template_vars["ID"]}.pdf')
    html.write_pdf(target=path_report, stylesheets=[css], font_config=font_config)
    print("PDF exported ✅")
    webbrowser.open(path_report)


def data_to_html(json_subject: dict):
    # html_df = pd.DataFrame(json_subject['data']).to_html(index=True, header=True, classes='data-table')

    df = pd.DataFrame(json_subject['data'])
    new_index = ['Shoe'] + df.index.values.tolist()[1:]
    path_image = df.iloc[0].values.tolist()
    df.iloc[0] = df.columns.values
    df = df.set_axis(new_index, axis='index')
    row_image = '<tr><th></th>'
    for value in path_image:
        new_value = value.split('/')[-1].replace('\\', '/')
        row_image += f'<td><img src="{new_value}"/></td>'
    row_image += '</tr>'

    index_label = df.index.values
    html_index_label = [
        'Shoe',
        'Weight <i>[g]</i>',
        'VO<sub>2</sub> <i>[ml/min/kg]</i>',
        'VO<sub>2</sub> <i>[ml/km/kg]</i>',
        'RER',
        'HR <i>[bpm]</i>',
        'RPE <i>[6-20]</i>',
        'Comfort <i>[1-10]</i>',
        'Lactate <i>[mmol/l]</i>',
        'Size (US)',
        'Cadence steps/min'
    ]

    for index, value in enumerate(index_label):
        perc_true = 0
        for val in value.split('_'):
            if val not in html_index_label[index]:
                perc_true += 1

        if (perc_true / len(value.split('_'))) > 0.3:
            html_index_label[index] = value

    df = df.set_axis(html_index_label, axis='index')

    # Add image row
    split_html = df.to_html(index=True, header=False, classes='data-table', escape=False).split('\n')
    html_df = split_html[0] + row_image + ''.join(split_html[1:])

    return html_df


def generate_report(json_path: str) -> Dict[str, Any]:
    # Load Data Json
    with open(json_path, "r") as file:
        template_vars = json.load(file)
    template_vars['data_table'] = data_to_html(json_subject=template_vars)

    del template_vars['data']

    # format DOB
    date_obj = datetime.datetime.strptime(template_vars['DOB'], "%Y-%m-%dT%H:%M:%S")
    template_vars['DOB'] = date_obj.strftime("%d.%m.%y")

    return template_vars


def main(subject_json_path):
    template_vars = generate_report(json_path=subject_json_path)
    render_report(template_vars=template_vars, path_report= os.path.dirname(subject_json_path))

