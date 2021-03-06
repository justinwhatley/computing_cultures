# Imports
import nltk.corpus
import nltk.stem.snowball
import nltk.tokenize
import string
import nltk 
nltk.download('stopwords')
nltk.download('punkt')

# Get default English stopwords and extend with punctuation
stopwords = nltk.corpus.stopwords.words('english')
stopwords.extend(string.punctuation)
stopwords.append('')


def remove_stop_words(word_list):
    # Removes all stop words (TODO check if necessary)
    return [word for word in word_list if word not in stopwords]

def tokenize(text):
    # Tokenizes text
    tokens = nltk.word_tokenize(text)
    return tokens

def mark_exact_duplicates(dict_list, key):
    """
    Counts the number of titles that have already appeared in the title set
    """
    hash_set = set()
    duplicate_dict = {}

    counter = 0 
    for i in range(len(dict_list)):
        temp_len = len(hash_set)
        value = dict_list[i][key]
        hash_set.add(value)
        # If the set size did not increase the value was a duplicate in the dict_list
        if len(hash_set) != temp_len +1:
            if value not in duplicate_dict:
                duplicate_dict[value] = 1
            else:
                duplicate_dict[value] += 1
            counter += 1        

    for i in range(len(dict_list)):
        value = dict_list[i][key]
        if value in duplicate_dict:
            dict_list[i][''] = True
    
    return dict_list, counter

# TODO add list index of possible duplicates 

# TODO make case insensitive

# From https://bommaritollc.com/2014/06/30/advanced-approximate-sentence-matching-python/
def get_token_set_match_ratio(tokens_a, tokens_b):
    """
    Checks whether token_a and token_b are similar by calculating Jaccard similiarity
    """
    # key_token = [token.lower().strip(string.punctuation) for token in  nltk.tokenize.word_tokenizer(dict_list[i][key]) \
    #             if token.lower().strip(string.punctuation) not in stopwords]
    
    # Case insensitive comparison (should not be necessary with titles in standard capitalized format)
    # tokens_a = [token.lower() for token in tokens_a]
    # tokens_b = [token.lower() for token in tokens_b]

    # Calculate Jaccard similarity
    set_intesection = (set(tokens_a).intersection(tokens_b))
    set_union = (set(tokens_a).union(tokens_b))
    return len(set_intesection) / float(len(set_union))


def mark_database_for_full_match(k, dict_list):
    """
    Marks all databases containing a particular title
    """
    db_list = ['ACM', 'IEEE', 'INSPEC', 'ALT']
    db_list = [db.lower() for db in db_list]

    # For all the databases set in a particular line, add them to the other and vice-versa
    for db in db_list:
        if dict_list[k[0]][db] == 1:
            dict_list[k[1]][db] = 1
        if dict_list[k[1]][db] == 1:
            dict_list[k[0]][db] = 1

def add_match_clusters(similarity_map, dict_list):
    """
    Sets a cluster number for matches that are not perfect
    """
    cluster_number = 1

    cluster_key = 'possible match id'
    # TODO figure out hot to avoid full-matches
    
    for k, val in sorted(similarity_map.iteritems()):
        temp_cluster_number = ''
        # If either line has a specified cluster, add that cluster number to both
        first_line = dict_list[k[0]][cluster_key]
        second_line = dict_list[k[1]][cluster_key]
        if first_line:
            temp_cluster_number = int(first_line)
        elif second_line:
            temp_cluster_number = int(second_line)
        
        # Assigns the cluster number to both of the lines
        if temp_cluster_number:
            dict_list[k[0]][cluster_key] = temp_cluster_number
            dict_list[k[1]][cluster_key] = temp_cluster_number
        else:
            dict_list[k[0]][cluster_key] = cluster_number
            dict_list[k[1]][cluster_key] = cluster_number
            cluster_number += 1

def remove_match(similarity_map, dict_list, threshold = .9):
    """
    Deletes duplicates meeting high similarity threshold starting from the largest
    """
    initial_length = (len(dict_list))
    for k, val in sorted(similarity_map.iteritems(), key=lambda x: x[0][1], reverse=True):
        if val >= threshold:
            del dict_list[k[1]]
            # print(k, val)
            # print(dict_list[k[0]]['title']).encode('utf-8') 
            # print(dict_list[k[1]]['title']).encode('utf-8') 

    print('initial_length: ' + str(initial_length))
    print('new_length: ' + str(len(dict_list)))
            
def remove_ids_for_corrected_clusters(dict_list):
    """
    Removes the id numbers associated with cluster items that no longer have any matches in the list
    """
    cluster_key = 'possible match id'

    # Iterate through the list of dictionary items
    for i, line in enumerate(dict_list):
        cluster_id_1 = line[cluster_key]
        if cluster_id_1:
            actual_cluster = False
            for j in range(len(dict_list)):
                if j!=i:
                    cluster_id_2 = dict_list[j][cluster_key]
                    if cluster_id_1 == cluster_id_2:
                        actual_cluster = True
                        break
            # If the cluster ID only appears once, remove the ID since it is no longer a cluster
            if not actual_cluster:
                # print('made it')
                line[cluster_key] = None
    
            
def mark_possible_duplicates(dict_list, key):
    """
    Marks the possible duplicates strings
    """
    number_of_titles = len(dict_list)
    full_match_criteria = 0.9

    # Build a list of token sets for the strings in the key 
    token_list = []
    for i in range(number_of_titles):
        # Removes stop words to create token set
        value = tokenize(dict_list[i][key]) 
        value = remove_stop_words(value)
        token_list.append(value)

    # Dict of objects with the structure {(i:j) : score}
    similarity_map = {}
    score_threshold = 0.5

    # Indexes of tokens will match indexes in dict_list
    for i in range(number_of_titles):
        # Trying brute forces comparison of all items (O(n^2)/2), seems fast enough for this 
        for j in range(i+1, number_of_titles):
            score = get_token_set_match_ratio(token_list[i], token_list[j])
            if score >= score_threshold:
                similarity_map[(i, j)] = score

    partial_matches = 0 
    full_matches = 0 
    for k, val in sorted(similarity_map.iteritems()):
        # print(k)
        # print(val)
        if (val < full_match_criteria):
            # print(dict_list[k[0]][key]).encode('utf-8') 
            # print(dict_list[k[1]][key]).encode('utf-8') 
            # print('Similarity score: ' + str(val))  
            partial_matches +=1
        else:
            mark_database_for_full_match(k, dict_list)
            full_matches += 1
    
    add_match_clusters(similarity_map, dict_list)
    remove_match(similarity_map, dict_list, threshold = full_match_criteria)
    remove_ids_for_corrected_clusters(dict_list)

    print('Partial matches: ' + str(partial_matches))
    print('Full matches: ' + str(full_matches))

    return dict_list
    

