
#!/usr/bin/env python

import glob
# import csv
import os.path as path

data_directory = path.join('..', 'Data')
extention = '.xlsx'
data_filename = 'Altmetrics' + extention

from xlrd import open_workbook

def read_xlsx(index=0):
    global data_directory
    global data_filename
    book = open_workbook(path.join(data_directory, data_filename))
    sheet = book.sheet_by_index(index)

    # read header values into the list    
    keys = [sheet.cell(0, col_index).value.strip() for col_index in xrange(sheet.ncols)]

    dict_list = []
    for row_index in xrange(1, sheet.nrows):
        d = {keys[col_index]: sheet.cell(row_index, col_index).value 
            for col_index in xrange(sheet.ncols)}
        dict_list.append(d)

    return dict_list

def remove_exact_duplicates(dict_list, column):
    """
    Counts the number of titles that have already appeared in the title set
    """
    hash_set = set()
    counter = 0 
    for i in range(len(dict_list)):
        temp_len = len(hash_set)
        print(dict_list[i][column])
        hash_set.add(dict_list[i][column])
        if len(hash_set) != temp_len +1:
            counter += 1
    print(counter)

    print(len(hash_set))

def compress_by_title(dict_list):
    """
    Cleans up data organization
    For instance, the authors appear on separate rows in the excel file so they are initially added
    as separate objects. This corrects that.
    """

    # Turn Authors, Institutional Affiliation, Department and Country into tuple
    clean_dict_list = {}
    author_details = []
    title = dict_list[0]['TITLE']
    for line in dict_list:
        for key in line:
            print key
        author = {'Authors': line['Authors'],
        'Institutional Affiliation': line['Institutional Affiliation'],
        'Department': line['Department'],
        'Country': line['Country']
        }
        
        if line['TITLE'] != '':
            title = line['TITLE'] 
            print(author_details)
            # Initialize with first author
            author_details = [author]
        else:
            author_details.append(author)

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

    dict_list = read_xlsx()
    key_set = set()
    for key in dict_list[0]:
        key_set.add(key)
    # dict_list = compare_value(dict_list, 'TITLE')
        
    compress_by_title(dict_list)
    