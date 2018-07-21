 
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
                'IEEE',
                'INSPEC',
                'ALT'
                'Academia.edu',
                'Web of Science',
                'Google Scholar',
                'DOAJ',
                'Other',
                'Possible Match ID']
    return key_list
# Sets global final key list
final_key_list = set_dictionary_keys()

def set_database(db_name, dict_list):
    """
    Sets the database key to each line in the dict_list
    """
    db_list = ['ACM', 'IEEE', 'INSPEC', 'ALT']
    
    # Sets to lowercase
    db_name = db_name.lower()
    db_list = [db.lower() for db in db_list]

    # If the db_name is specified, sets the correct db to 1 and the other dbs in the db_list to 0
    if db_name in db_list:
        for db in db_list:
            for line in dict_list:
                if db != db_name:
                    line[db] = 0
                else: 
                    line[db] = 1
    else: 
        print('The database ' + db_name + ' is not in the database list: ' + str(db_list))



def read_xlsx(sheet_index, data_filename):
    """
    Loads from an excel format file
    """
    global data_directory
    book = open_workbook(path.join(data_directory, data_filename))
    sheet = book.sheet_by_index(sheet_index)

    # read header values into the list    
    keys = [sheet.cell(0, col_index).value.strip().lower().encode('utf-8') for col_index in xrange(sheet.ncols)]

    dict_list = []
    for row_index in xrange(1, sheet.nrows):
        d = {keys[col_index]: sheet.cell(row_index, col_index).value 
            for col_index in xrange(sheet.ncols)}
        dict_list.append(d)

    return dict_list

def capitalize_title(str):
    """
    Puts the title in a standard capitalized format
    """
    word_lst = str.split()
    return ' '.join([word.capitalize() for word in word_lst])

def clean_altmetric_dictionary_authors_diff_lines(dict_list, key_set):
    """
    Cleans up data according to the xlsx format
    For instance, the authors appear on separate rows in the excel file so they are initially added
    as separate objects. This corrects that.
    """
    author_keys = ['authors', 'institutional affiliation', 'department', 'country']
    clean_dict_list = []
    author_details = []
    
    for line in dict_list:
        new_line = {}
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

def clean_acm_new(dict_list, key_set):
    """
    Cleans up data according to the xlsx format for ACM New excel format
    Gets the country search, assigning these to individual authors that were previously separated by 'ands'
    """
    author_keys = ['authors', 'institutional affiliation', 'department', 'country']
    clean_dict_list = []
    author_details = []
    
    for line in dict_list:   
        new_line = {}     
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


def clean_ieee(dict_list, key_set):
    """
    Cleans up data according to the xlsx format IEEE Explore.
    Gets the country search, assigning these to individual authors that were previously separated by 'ands'
    """
    author_keys = ['authors', 'institutional affiliation', 'department', 'country']
    clean_dict_list = []
    author_details = []
    
    for line in dict_list:      
        new_line = {}  
        # Handles line where the country search is given
        category = line['document title'].strip().split(' ')
        # This tells us the line is a search query
        if category[0] == 'search:':
            # del(category[0])
            # Note: Country column was added to the excel sheet
            country = line['country'].lower()
        # Failed search 
        elif category[0] == '-':
            continue
        # Modifies new_line
        else:
            # Get authors:
            authors = line['authors'].split(';')
            authors_details = []
            # Gets the institution information 
            institution_list = line['author affiliations']

            for i, a in enumerate(authors):
                mapped_affilations = institution_list

                author = {'authors' : a.encode('utf-8').strip(),
                          'institutional affiliation' : mapped_affilations,
                          'department' : None,
                          'country' : country
                          }
                authors_details.append(author)
             # Adds non-author keys           
            for key in key_set:
                new_line[key] = line[key]

            del(new_line['authors'])
            del(new_line['author affiliations'])
            new_line['authors'] = authors_details
            clean_dict_list.append(new_line)
    return clean_dict_list

def correct_year_format(year_str):
    # Checks whether the format is a valid year 
    try: 
        # Assumes year ranges will fall between 1900 and 2100
        year = int(year_str)
        if 1900 <= year <= 2100:
            return True
    except:
        pass
    return False

def correct_proceedings_format(proceedings_str):
    if not isinstance(proceedings_str, basestring):
        return False

    if len(proceedings_str) == 0:
        return False

    # Checks that it is not the volume
    if proceedings_str.split()[0] == 'v':
        return False

    # Checks that it is not the page
    if proceedings_str.split()[0] == 'p':
        return False

    # Check that it is not a copyright
    split_str = proceedings_str.split()
    if 'Copyright' in split_str:
        return False

    # Check that it is not a database name
    if proceedings_str == 'Compendex' or proceedings_str == 'Inspec':
        return False
    
    if proceedings_str == 'Engineering Village':
        return False

    # # Check that the value is not a string
    # try: 
    #     int(year_str)
    #     return False
    # except:
    #     pass

    # Sanity check to ensure the string is long enough to be the conference title
    if len(proceedings_str) >= 20:
        return True

    return False

def clean_inspec_helper(dict_list):
    """
    Serves to extract the Publication Year and Issue Dates from the columns.
    The original web scrapping did not account for different outputs columns 
    were assigned the incorrect values in the excel sheet.

    The logic here orders assumes that Publication year and Issue Dates will fit 
    a general date format or simply show a string representing the year and will
    appear one after the other in the original excel ordering of the keys

    """
    cleaner_dict_list = []
    original_excel_ordering = ['country', 'title', 'author', 'author affiliation', 'source', 'isbn', 'isbn13', 'publication year',
                                'volume and issue', 'pages', 'issue date', 'monograph title',
                                'language', 'database', 'copyright']

    correct_excel_columns = ['title', 'author', 'author affiliation', 'source']

    country = ''
    for i, line in enumerate(dict_list):
        new_line = {}
        
        # Handles line where the country search is given
        category = line['title'].strip().split(' ')
        # This tells us the line is a search query
        if category[0] == 'search:':
            # Note: Country column was added to the excel sheet
            country = line['country'].lower()
            # Skips the search line as this contains no other information
            continue
        # Failed search 
        elif category[0] == '-':
            continue
        new_line['country'] = country
        new_line['publication_year'] = ''
        new_line['conference_proceedings'] = ''
        publication_year = ''
        conference_proceedings = ''
        for key in original_excel_ordering:
            # These particular value/key combinations were correctly mapped
            if key in correct_excel_columns:
                new_line[key] = line[key]
            elif key == 'country':
                continue
            else:
                if not publication_year and correct_year_format(line[key]):
                    #When the year the publication year is not available, issue date may be substituted
                    publication_year = line[key]
                    new_line[publication_year] = publication_year
                if not conference_proceedings and correct_proceedings_format(line[key]):
                    conference_proceedings = line[key]
                    new_line[conference_proceedings] = conference_proceedings

        cleaner_dict_list.append(new_line)       

    return cleaner_dict_list


def clean_inspec_new(dict_list, key_set):
    """
    Cleans up data according to the xlsx format for INSPEC_new excel format.
    Gets the country search, assigning these to individual authors that were previously separated by 'ands'
    """
    author_keys = ['authors', 'institutional affiliation', 'department', 'country']

    # Gets correct key/value pairs despite bad web scraping allignment 
    dict_list = clean_inspec_helper(dict_list)

    clean_dict_list = []
    author_details = []
    for line in dict_list:        
        # Modifies new_line
        new_line = {}
        # Get authors:
        authors = line['author'].split(';')
        authors_details = []
        # Gets the institution information 
        institution_list = line['author affiliation'].split('(')
        del institution_list[0]

        for i, a in enumerate(authors):
            # Extracts the affiliation numbers associated with the author
            author_affiliation_string = (a[a.find("(")+1:a.find(")")])
            # Puts the string of numbers into a list of int values                
            try: 
                author_affiliation = [int(s.strip()) for s in author_affiliation_string.split(',')]
            except:
                # Author will not have numbered affiliations in certain cases
                pass
            # Remove numbers from author names
            a = a.split('(')[0].strip()
            # Maps institutional affilations for that author to a list
            mapped_affilations = []
            try: 
                for value in author_affiliation:
                    mapped_affilations.append(institution_list[value-1].split(')')[1].strip())
            except:
                # Case where parsing fails because of special chars, simply adds the author affilation without precise mapping
                mapped_affilations.append(line['author affiliation'])

            author = {'authors' : a.encode('utf-8').strip(),
                        'institutional affiliation' : mapped_affilations,
                        'department' : None,
                        'country' : line['country']
                        }
            authors_details.append(author)

        # Adds non-author keys           
        for key in key_set:
            if key in line:
                new_line[key] = line[key]

        del(new_line['author'])
        del(new_line['country'])
        del(new_line['author affiliation'])

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
    
    print('\nExtra keys not in main list: ')
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
        # print(tup)
        for i in range(len(dict_list)):
            # Changes dict_list keys from tup[1] to tup[0]
            # for key in dict_list[i].iterkeys():
            #     print(key)
            #TODO check output 
            try:
                dict_list[i][tup[0]] = dict_list[i][tup[1]]
                # Removes input key from line
                del(dict_list[i][tup[1]])
            except:
                pass

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
        line.update({key: None for key in main_keys_missing})
   
    if remove_empty_column:
        # Removes empty columns keys in existing dataset
        for line in dict_list:
            if '' in line.iterkeys():
                del(line[''])       
        # Removes empty columns from the 'additional_keys' variable
        number_additional_keys = len(additional_keys)
        for i in range(number_additional_keys):
            checking_index = number_additional_keys-1-i
            if not additional_keys[checking_index]:
                del(additional_keys[checking_index])

    # Adds extra columns and data to the 'other' category
    if additional_keys: 
        for line in dict_list:
            # Init list for other
            if line['other'] is None or line['other'] == '':
                line['other'] = []
            # Handles cases where the 'other' category is already filled by a string
            else:
                line['other'] = [('other', line['other'])]

            # Append to 'others' list and remove old column placement
            # for key in additional_keys:
            #     print(key)
            
            for key in additional_keys:
                # print('*********')
                # print('made it!!!')
                # print('*********')
                # for item in line.iterkeys():
                #     print(item)
                # TODO verify expected behavior - removal of a key seems to generalize to all lines
                # but it does seem like it should work that way
                try:
                    line['other'].append((key, line[key]))
                    del(line[key])
                except:
                    pass
    
    # print('After')
    # for line in dict_list:
    #     print(line)
    #     exit(0)
    return dict_list

def remove_columns(key_list, dict_list):
    for row in dict_list:
        for key_to_remove in key_list:
            try:
                del(row[key_to_remove])
            except:
                print(key_to_remove + ' not removed.')
        break

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

    # Removes specified columns that do not contain pertinent information 
    columns_to_remove = ['panel discussion', 'report']
    dict_list = remove_columns(columns_to_remove, dict_list)

    # Maps keys to a standard form
    mapping_tup_list = [('journal', 'name of journal'), 
                            ('conference proceedings', 'conference paper'), 
                            ('book/chapter', 'book'),
                            ('year', 'vol/month/issue'), 
                            ]
    dict_list = map_key_to_standard(mapping_tup_list, final_key_list, dict_list)
    dict_list = add_missing_columns(final_key_list, dict_list)

    return dict_list


def load_acm_new():
    # Gets main list of dictionary keys
    global final_key_list 

    # Loads ACM_new data sheet
    extention = '.xlsx'
    data_filename = 'Bibliometrics' + extention
    dict_list = read_xlsx(2, data_filename)

    # Gets the set of all keys in the in the xlsx
    key_set = get_key_set(dict_list)

    # Cleans the dictionary by adding all authors to the same line of the list and associating author data    
    dict_list = clean_acm_new(dict_list, key_set)

    # Removes specified columns that do not contain pertinent information 
    columns_to_remove = ['angola', 'article_no', 'month', 'edition', 'isbn', 'id', 'note', 'issue_no',
                        'editor', 'publisher_loc', 'description', 'acronym', 'volume', 'conf_loc', 'advisor',
                        'pages', 'publisher', 'num_pages', 'issn']
    dict_list = remove_columns(columns_to_remove, dict_list)

    # Maps keys to a standard form
    mapping_tup_list = [('book/chapter', 'booktitle'),
                            ('year', 'issue_date')]
    dict_list = map_key_to_standard(mapping_tup_list, final_key_list, dict_list)
    dict_list = add_missing_columns(final_key_list, dict_list)

    get_key_delta(final_key_list, dict_list[1])

    return dict_list

def load_ieee_explore():
    # Gets main list of dictionary keys
    global final_key_list 

    # Loads ieee explore data sheet
    extention = '.xlsx'
    data_filename = 'Bibliometrics' + extention
    dict_list = read_xlsx(4, data_filename)

    # Gets the set of all keys in the in the xlsx
    key_set = get_key_set(dict_list)

    # Cleans the dictionary by adding all authors to the same line of the list and associating author data    
    dict_list = clean_ieee(dict_list, key_set)

     # Removes specified columns that do not contain pertinent information 
    columns_to_remove = ['isbn', 'copyright year', 'start page', 'inspec non-controlled terms', 'reference count',
                        'date added to xplore', 'meeting date', 'eisbn', 'article citation count', 'issue', 
                        'patent citation count', 'mesh terms', 'volume', 'online date', 'inspec controlled terms',
                        'publisher', 'end page', 'issn', 'document identifier']
    dict_list = remove_columns(columns_to_remove, dict_list)

    # Maps keys to a standard form
    mapping_tup_list = [('title', 'document title'), 
                            ('keywords', 'author keywords'), 
                            ('conference proceedings', 'publication title'),
                            ('year', 'issue date'), 
                            ]
    dict_list = map_key_to_standard(mapping_tup_list, final_key_list, dict_list)
    dict_list = add_missing_columns(final_key_list, dict_list)

    return dict_list

def load_inspec():
    # Gets main list of dictionary keys
    global final_key_list 

    # Loads ACM_new data sheet
    extention = '.xlsx'
    data_filename = 'Bibliometrics' + extention
    dict_list = read_xlsx(7, data_filename)

    # Gets the set of all keys in the in the xlsx
    key_set = get_key_set(dict_list)

    # Cleans the dictionary by adding all authors to the same line of the list and associating author data    
    dict_list = clean_inspec_new(dict_list, key_set)

    # Removes specified columns that do not contain pertinent information 
    # **Removal was done in the clean load helper with allignment**
    # columns_to_remove = ['isbn', 'language', 'isbn13', 'database', 'data provider', 'volume and issue', 'copyright']
    # dict_list = remove_columns(columns_to_remove, dict_list)

    # Maps keys to a standard form
    mapping_tup_list = [('conference proceedings', 'source')]
    dict_list = map_key_to_standard(mapping_tup_list, final_key_list, dict_list)
    dict_list = add_missing_columns(final_key_list, dict_list)

    return dict_list 


if __name__ == '__main__':
    
    # ----------------------------------------------------------------------------------
    # Loads bibliometric data sheets
   
    # Loads inspect data sheet
    print('********************************************')
    print('Loading inspec')
    print('********************************************')
    inspec_dict_list = load_inspec()
    set_database('inspec', inspec_dict_list)

    # Loads IEEE data sheet
    print('********************************************') 
    print('Loading IEEE explore')
    print('********************************************')
    ieee_dict_list = load_ieee_explore()
    set_database('ieee', ieee_dict_list)

    # Loads ACM new data sheet
    print('********************************************')
    print('Loading ACM new')
    print('********************************************')
    acm_new_dict_list = load_acm_new()
    set_database('acm', acm_new_dict_list)

       # ----------------------------------------------------------------------------------
    # Loads altmetric data sheets
    print('********************************************')
    print('Loading main altmetric')
    print('********************************************')
    altmetric_dict_list = load_main_altmetric()
    set_database('alt', altmetric_dict_list)
    # ----------------------------------------------------------------------------------

    print('Appending dictionary lists')
    dict_list =  inspec_dict_list + ieee_dict_list + acm_new_dict_list + altmetric_dict_list
    # dict_list = acm_new_dict_list + ieee_dict_list 
    print('Complete')

    # Puts titles in a standard format
    for line in dict_list:
        line['title'] = capitalize_title(line['title'])

    # Check for exact title duplicates
    # print('Searching for exact matches in the list')
    # dict_list, exact_matches = compare.mark_exact_duplicates(dict_list, 'title')
    # print('Complete')

    # Text comparison 
    print('Marking possible duplicates: ')
    dict_list = compare.mark_possible_duplicates(dict_list, 'title')

    import csv
    keys = dict_list[0].keys()
    with open('test.csv', 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(dict_list)

