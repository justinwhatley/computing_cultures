
#!/usr/bin/env python

import glob
# import csv
import os.path as path

data_directory = path.join('..', 'Data')
extention = '.xlsx'
data_filename = 'Altmetrics' + extention

from xlrd import open_workbook

def read_xlsx():
    global data_directory
    global data_filename
    book = open_workbook(path.join(data_directory, data_filename))
    sheet = book.sheet_by_index(0)

    # read header values into the list    
    keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols)]

    dict_list = []
    for row_index in xrange(1, sheet.nrows):
        d = {keys[col_index]: sheet.cell(row_index, col_index).value 
            for col_index in xrange(sheet.ncols)}
        dict_list.append(d)

    return dict_list


# def read_csv():
#     """
#     Loads the csv data by row, assigning each row value to a column key
#     :return:
#     """
#     directory = mechanical_turks_output_directory

#     csv_list_of_dicts = []
#     for filename in glob.glob(path.join(directory, '*.csv')):
#         with open(filename, 'rb') as csv_file:
#             reader = csv.reader(csv_file, delimiter=',')
#             header = None
#             for i, row_list in enumerate(reader):
#                 if i == 0:
#                     header = row_list
#                 else:
#                     result_obj = {}
#                     for j, result in enumerate(row_list):
#                         result_obj[header[j]] = row_list[j]
#                     csv_list_of_dicts.append(result_obj)

    # return csv_list_of_dicts

if __name__ == '__main__':

    #test
    dict_list = read_xlsx()
    print(dict_list)