
#!/usr/bin/env python

import glob
import text_comparison as compare
import os.path as path

from xlrd import open_workbook
data_directory = path.join('..', 'Data')

def read_xlsx(sheet_index, data_filename):
    global data_directory
    book = open_workbook(path.join(data_directory, data_filename))
    sheet = book.sheet_by_index(sheet_index)

    # read header values into the list    
    keys = [sheet.cell(0, col_index).value.strip().lower() for col_index in xrange(sheet.ncols)]

    dict_list = []
    for row_index in xrange(1, sheet.nrows):
        d = {keys[col_index]: sheet.cell(row_index, col_index).value 
            for col_index in xrange(sheet.ncols)}
        dict_list.append(d)

    return dict_list

def clean_altmetric_dictionary(dict_list, key_set):
    """
    Cleans up data according to the xlsx format
    For instance, the authors appear on separate rows in the excel file so they are initially added
    as separate objects. This corrects that.
    """
    author_keys = ['authors', 'institutional affiliation', 'department', 'country']
    clean_dict_list = []
    author_details = []
    new_line = {}
    for line in dict_list:
        # Turns Authors, Institutional Affiliation, Department and Country into an object as part of a list
        author = {}
        for key in author_keys:
            author[key] = line[key]
        
        # New line containing the title 
        if line['title'] != '':
            title = line['title']
            
             # Adds new line to the clean_dict after it's been instantiated
            if new_line:
                new_line['authors'] = author_details
                clean_dict_list.append(new_line)
                new_line = {}
            # Adds non-author keys           
            for key in key_set:
                if key not in author_keys:
                    new_line[key] = line[key]
            new_line['has duplicate'] = False

            # Initialize with first author
            author_details = [author]
        else:
            # Append new author to the publications
            author_details.append(author)
    
    # Handles last title
    clean_dict_list.append(new_line)

    return clean_dict_list

def set_dictionary_keys():
    """
    Initializes the desired outputs keys for the columns of the dictionary
    """
    key_list = ['Title', 
                'Authors',
                'Institution',
                'Country',
                'Journal',
                'Conference proceedings',
                'Book/chapter',
                'Working paper',
                'Thesis',
                'Year',
                'Keywords',
                'Abstract',
                'ACM',
                'IEE',
                'INSPEC',
                'Academia.edu',
                'Web of Science',
                'Google Scholar',
                'DOAJ',
                'Other',
                'Has Duplicate']
    # return {key:None for key in key_list}
    return key_list

def get_key_delta(key_list, dict_line):
    # Puts all main keys in lower case for comparison
    key_list = [x.lower() for x in key_list]

    main_keys_missing = []
    for key in key_list:
        if key not in dict_line:
            main_keys_missing.append(key)

    additional_keys = [] 
    for key in dict_line:
        if key not in key_list:
            additional_keys.append(key)
    return (main_keys_missing, additional_keys)

def map_key_to_standard(mapping_tup_list, key_list, dict_list):
    # Takes a list of tuples that map key names in input dataset to expected key names

    # Puts all main keys in lower case for comparison
    key_list = [x.lower() for x in key_list]
    incorrect_mapping = False
    for tup in mapping_tup_list:
        if tup[0] not in key_list:
            print(tup[0])
            incorrect_mapping = True
    if incorrect_mapping:
        print('Mapping to a key that is not in output key_list, fix this and try again')
        exit(0)

    for tup in mapping_tup_list:
        for i in range(len(dict_list)):
            # Changes dict_list keys from tup[1] to tup[0]
            dict_list[i][tup[0]] = dict_list[i][tup[1]]
            # Removes input key from line
            del(dict_list[i][tup[1]])

    return dict_list

def add_missing_columns(key_list, dict_list, remove_empty_column = True):
    """
    Adds the missing the columns which are keys in the key_list not in the dict_list
    """
    # Puts all main keys in lower case for comparison
    key_list = [x.lower() for x in key_list]

    main_keys_missing, additional_keys = get_key_delta(key_list, dict_list[0])
    
    # Adds keys that will be used as final columns
    for line in dict_list:
        line.update({key: None for key in key_list})
 
   
    if remove_empty_column:
        # Removes empty columns keys in existing dataset
        for line in dict_list:
            del(line[''])
        # Removes empty columns from the 'additional_keys' variable
        number_additional_keys = len(additional_keys)
        for i in range(number_additional_keys):
            checking_index = number_additional_keys-1-i
            if not additional_keys[checking_index]:
                del(additional_keys[checking_index])

    # Adds extra columns and data to the 'other' category
    for line in dict_list:
        # Init list for other
        if line['other'] is None:
            line['other'] = []
        # Append to 'others' list and remove old column placement
        for key in additional_keys:
            line['other'].append({key: line[key]})
            del(line[key])
    
    return dict_list


if __name__ == '__main__':
    # Gets main list of dictionary keys
    final_key_list = set_dictionary_keys()

    # Loads main altmetric data sheet
    extention = '.xlsx'
    data_filename = 'Altmetrics' + extention
    dict_list = read_xlsx(0, data_filename)
    
    # Gets the set of all keys in the in the xlsx
    key_set = set()
    for key in dict_list[0]:
        key_set.add(key)

    # Cleans the dictionary by adding all authors to the same line of the list and associating author data    
    dict_list = clean_altmetric_dictionary(dict_list, key_set)

    mapping_tup_list = [('journal', 'name of journal'), 
                            ('conference proceedings', 'conference paper'), 
                            ('book/chapter', 'book'),
                            ('year', 'vol/month/issue'), 
                            ]
    # TODO find out whether to map vol/month/issue to year
    # TODO find out where to map panel discussion (other?)
    # TODO find out where to map report (other?)

    map_key_to_standard(mapping_tup_list, final_key_list, dict_list)

    add_missing_columns(final_key_list, dict_list)
    exit(0)

     # Loads main bibliometric data sheet
    data_filename = 'Bibliometrics' + extention
    dict_list = read_xlsx(0, data_filename)

    # Check for exact title duplicates
    dict_list, exact_matches = compare.mark_exact_duplicates(dict_list, 'title')

    # Text comparison 
    dict_list = compare.mark_possible_duplicates(dict_list, 'title')

    print('Full matches: ' + str(exact_matches))

    # counter = 0 
    # for item in dict_list:
    #     if item['has duplicate']:
    #         counter += 1

    # print('Marked as duplicated: ' + counter)
