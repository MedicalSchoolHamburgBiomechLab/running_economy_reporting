import os
import sys

gettrace = getattr(sys, 'gettrace', None)

if gettrace():
    DEBUG_MODE = True
else:
    DEBUG_MODE = False

ZEBRIS_SAMPLE_RATE = 300
ACQUISITION_DURATION = 1  # in minute

PATH_PROJECT = os.path.dirname(os.path.dirname(__file__))
PATH_DATA = "\\".join(['C:', 'Users', os.getlogin(),
                       'OneDrive - MSH Medical School Hamburg - University of Applied Sciences and Medical University','Dokumente', 'Projects','bisp_footwear','data'])


# PATH_DATA = r"/Users/dominikfohrmann/OneDrive - MSH Medical School Hamburg - University of Applied Sciences and Medical University/Dokumente/Projects/bisp_footwear/data"
# PATH_DATA = r"C:\Users\QTM\OneDrive - MSH Medical School Hamburg - University of Applied Sciences and Medical University\Dokumente\Projects\bisp_footwear\data"
PATH_DATA = r"C:\Users\dominik.fohrmann\OneDrive - MSH Medical School Hamburg - University of Applied Sciences and Medical University\Dokumente\Projects\bisp_footwear\data"
# if os.path.isfile(os.path.join(PATH_DATA, 'subjects_running_economy_update.xlsx')):
#     PATH_EXCEL = os.path.join(PATH_DATA, 'subjects_running_economy_update.xlsx')
# else:
PATH_EXCEL = os.path.join(PATH_DATA, 'subjects_running_economy.xlsx')
PATH_ZEBRIS = os.path.join(PATH_PROJECT, 'data', 'ZEBRIS')
PATH_PRESSURE_REPORT = os.path.join(PATH_DATA, 'pressure', 'pdf_reports')
PATH_SPIRO = os.path.join(PATH_DATA, 'spiro')


print(PATH_DATA)
print(os.path.isdir(PATH_DATA))