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
            dict_list[i]['HasDuplicate'] = True
    
    print('Exact_duplicates: ' + str(counter))
    return dict_list

# From https://bommaritollc.com/2014/06/30/advanced-approximate-sentence-matching-python/
def get_token_set_match_ratio(tokens_a, tokens_b):
    """
    Checks whether token_a and token_b are similar by calculating Jaccard similiarity
    """
    # key_token = [token.lower().strip(string.punctuation) for token in  nltk.tokenize.word_tokenizer(dict_list[i][key]) \
    #             if token.lower().strip(string.punctuation) not in stopwords]

    # Calculate Jaccard similarity
    set_intesection = (set(tokens_a).intersection(tokens_b))
    set_union = (set(tokens_a).union(tokens_b))
    return len(set_intesection) / float(len(set_union))

def mark_possible_duplicates(dict_list, key):
    """

    """
    number_of_titles = len(dict_list)

    # Build a list of token sets for the strings in the key 
    token_list = []
    for i in range(number_of_titles):
        # Removes stop words to create token set
        value = tokenize(dict_list[i][key]) 
        value = remove_stop_words(value)
        token_list.append(value)

    # Dict of objects with the structure {(i:j) : score}
    similarity_map = {}
    score_threshold = 0.4

    # Indexes of tokens will match indexes in dict_list
    for i in range(number_of_titles):
        # Try brute forces comparison of all items (O(n^2))
        for j in range(i+1, number_of_titles):
            score = get_token_set_match_ratio(token_list[i], token_list[j])
            if score >= score_threshold:
                similarity_map[(i, j)] = score

    print(similarity_map)    
                


    # # The number of words
    # word_distance_allowed = 3

    # for line in dict_list:


# from nltk.corpus import stopwords





# import gensim  

# # Settings 
# train_lbls=False

# model = gensim.models.Doc2Vec.load('saved_doc2vec_model')  

# new_sentence = "I opened a new mailbox"  
# model.docvecs.most_similar(positive=[model.infer_vector(new_sentence)],topn=5)