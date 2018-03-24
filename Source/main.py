
#!/usr/bin/env python

import glob
import text_comparison as compare
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

def clean_dictionary(dict_list, key_set):
    """
    Cleans up data according to the xlsx format
    For instance, the authors appear on separate rows in the excel file so they are initially added
    as separate objects. This corrects that.
    """
    author_keys = ['Authors', 'Institutional Affiliation', 'Department', 'Country']
    clean_dict_list = []
    author_details = []
    new_line = {}
    for line in dict_list:
        # Turns Authors, Institutional Affiliation, Department and Country into an object as part of a list
        author = {}
        for key in author_keys:
            author[key] = line[key]
        
        # New line containing the title 
        if line['TITLE'] != '':
            title = line['TITLE']
            
             # Adds new line to the clean_dict after it's been instantiated
            if new_line:
                clean_dict_list.append(new_line)
                new_line = {}
            # Adds non-author keys           
            for key in key_set:
                if key not in author_keys:
                    new_line[key] = line[key]
            new_line['HasDuplicate'] = False

            # Initialize with first author
            author_details = [author]
        else:
            # Append new author to the publications
            author_details.append(author)
    
    # Handles last title
    clean_dict_list.append(new_line)

    return clean_dict_list


if __name__ == '__main__':

    dict_list = read_xlsx()
    
    # Gets the set of all keys in the in the xlsx
    key_set = set()
    for key in dict_list[0]:
        key_set.add(key)
        
    # Cleans the dictionary by adding all authors to the same line of the list and associating author data    
    dict_list = clean_dictionary(dict_list, key_set)

    # Check for exact title duplicates
    dict_list = compare.mark_exact_duplicates(dict_list, 'TITLE')

    # Text comparison 
    dict_list = compare.mark_possible_duplicates(dict_list, 'TITLE')

    # counter = 0 
    # for item in dict_list:
    #     if item['HasDuplicate']:
    #         counter += 1

    # print('Marked as duplicated: ' + counter)
