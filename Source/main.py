 
#!/usr/bin/env python

import glob
import text_comparison as compare
import os.path as path

from xlrd import open_workbook
data_directory = path.join('..', 'Data')

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
    return key_list
# Sets global final key list
final_key_list = set_dictionary_keys()

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

def clean_altmetric_dictionary_authors_diff_lines(dict_list, key_set):
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

            # Initialize with first author
            author_details = [author]
        else:
            # Append new author to the publications
            author_details.append(author)
    
    # Handles last title
    clean_dict_list.append(new_line)

    return clean_dict_list

def clean_bibliometric_dictionary_authors_single_line_ands(dict_list, key_set):
    """
    Cleans up data according to the xlsx format for ACM New excel format
    Gets the country search, assigning these to individual authors that were previously separated by 'ands'
    """
    author_keys = ['authors', 'institutional affiliation', 'department', 'country']
    clean_dict_list = []
    author_details = []
    new_line = {}
    for line in dict_list:        
        # Handles line where the country search is given
        type = line['type'].strip().split(' ')
        if type[0] == 'search:':
            del(type[0])
            country = ' '.join(type)
        # Failed search 
        elif type[0] == '-':
            continue
        # Modifies new_line
        else:
            # Get authors:
            authors = line['author'].split(' and ')
            authors_details = []
            for a in authors:
                author = {'authors' : a.encode('utf-8').strip(),
                          'institutional affiliation' : None,
                          'department' : None,
                          'country' : country
                          }
                authors_details.append(author)

             # Adds non-author keys           
            for key in key_set:
                new_line[key] = line[key]

            del(new_line['author'])
            new_line['authors'] = authors_details
            clean_dict_list.append(new_line)

    return clean_dict_list

def get_key_delta(key_list, dict_line):
    # Puts all main keys in lower case for comparison
    key_list = [x.lower() for x in key_list]

    main_keys_missing = []
    for key in key_list:
        if key not in dict_line:
            main_keys_missing.append(key)
    print('Main keys missing are: ')
    for key in main_keys_missing:
        print(key)

    additional_keys = [] 
    for key in dict_line:
        if key not in key_list:
            additional_keys.append(key)
    print('Extras keys not in main list')
    for key in additional_keys:
        print(key)

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
    
    # print('Before')
    # for line in dict_list:
    #     print(line)
    #     break

    # Adds keys that will be used as final columns
    for line in dict_list:
        line.update({key: None for key in main_keys_missing})
 
   
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
        if line['other'] is None or line['other'] == '':
            line['other'] = []
        # Handles cases where the 'other' category is already filled by a string
        else:
            line['other'] = [{'other': line['other']}]

        # Append to 'others' list and remove old column placement
        for key in additional_keys:
            line['other'].append({key: line[key]})
            del(line[key])
    
    # print('After')
    # for line in dict_list:
    #     print(line)
    #     exit(0)
    return dict_list

def get_key_set(dict_list):
    key_set = set()
    for key in dict_list[0]:
        key_set.add(key)
    return key_set

def load_main_altmetric():
    # Gets main list of dictionary keys
    global final_key_list 

    # Loads main altmetric data sheet
    extention = '.xlsx'
    data_filename = 'Altmetrics' + extention
    dict_list = read_xlsx(0, data_filename)

    # Gets the set of all keys in the in the xlsx
    key_set = get_key_set(dict_list)

     # Cleans the dictionary by adding all authors to the same line of the list and associating author data    
    dict_list = clean_altmetric_dictionary_authors_diff_lines(dict_list, key_set)

    mapping_tup_list = [('journal', 'name of journal'), 
                            ('conference proceedings', 'conference paper'), 
                            ('book/chapter', 'book'),
                            ('year', 'vol/month/issue'), 
                            ]
    # TODO find out whether to map vol/month/issue to year
    # TODO find out where to map panel discussion (other?)
    # TODO find out where to map report (other?)

    dict_list = map_key_to_standard(mapping_tup_list, final_key_list, dict_list)
    dict_list = add_missing_columns(final_key_list, dict_list)
    return dict_list

def clean_bibliometric_dictionary_authors_single_line_semicolons(dict_list, key_set):
     """
    Cleans up data according to the xlsx format for INSPEC_new excel format
    Gets the country search, assigning these to individual authors that were previously separated by 'ands'
    """
    #TODO implement
    author_keys = ['authors', 'institutional affiliation', 'department', 'country']
    clean_dict_list = []
    author_details = []
    new_line = {}
    for line in dict_list:        
        # Handles line where the country search is given
        type = line['type'].strip().split(' ')
        if type[0] == 'search:':
            del(type[0])
            country = ' '.join(type)
        # Failed search 
        elif type[0] == '-':
            continue
        # Modifies new_line
        else:
            # Get authors:
            authors = line['author'].split(' and ')
            authors_details = []
            for a in authors:
                author = {'authors' : a.encode('utf-8').strip(),
                          'institutional affiliation' : None,
                          'department' : None,
                          'country' : country
                          }
                authors_details.append(author)

             # Adds non-author keys           
            for key in key_set:
                new_line[key] = line[key]

            del(new_line['author'])
            new_line['authors'] = authors_details
            clean_dict_list.append(new_line)


def load_acm_new():
    # Gets main list of dictionary keys
    global final_key_list 

    # Loads ACM_new data sheet
    extention = '.xlsx'
    data_filename = 'Bibliometrics' + extention
    dict_list = read_xlsx(2, data_filename)

    # Gets the set of all keys in the in the xlsx
    key_set = get_key_set(dict_list)

    dict_list = clean_bibliometric_dictionary_authors_single_line_ands(dict_list, key_set)

    get_key_delta(final_key_list, dict_list[0])

    # mapping_tup_list = [('journal', 'name of journal'), 
    #                         ('conference proceedings', 'conference paper'), 
    #                         ('book/chapter', 'book'),
    #                         ('year', 'vol/month/issue'), 
    #                         ]
    exit(0)
    return dict_list


def load_inspec():
    # Gets main list of dictionary keys
    global final_key_list 

    # Loads ACM_new data sheet
    extention = '.xlsx'
    data_filename = 'Bibliometrics' + extention
    dict_list = read_xlsx(8, data_filename)

    # Gets the set of all keys in the in the xlsx
    key_set = get_key_set(dict_list)

    dict_list = clean_bibliometric_dictionary_authors_single_line_ands(dict_list, key_set)

    get_key_delta(final_key_list, dict_list[0])
    exit(0)
    return dict_list 

def load_ieee():
    pass 

if __name__ == '__main__':
    

    # ----------------------------------------------------------------------------------
    # Loads altmetric data sheets
    # dict_list = load_main_altmetric()
    # ----------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------
    # Loads bibliometric data sheets
   
    # Loads ACM new data sheet
    # dict_list = load_acm_new()
    dict_list = load_inspec()




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
