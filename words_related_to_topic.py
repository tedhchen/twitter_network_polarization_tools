import json
import re
from uralicNLP import uralicApi
import itertools
from collections import Counter
import os

def load_tweet_file(path):

    with open(path, "r") as read_file:
        tweets = json.load(read_file)
    return tweets

def load_stopwords():

    with open("stopwords.txt", "r") as read_file:
        list_of_words = read_file.readlines()
        stopwords = [w.strip("\n") for w in list_of_words]
    
    return stopwords

def remove_url(txt):

    text = re.sub(r"http\S+", "", txt)
    return text

def process_text(tweets, sw, LEM):

    processed_tweets = []

    for i in range(len(tweets)):

        if "retweeted_status" in tweets[i]:

            # Remove URL
            tweet_1 = remove_url(tweets[i]["retweeted_status"]["text"])
            
            # Lower case and split
            tweet_2 = tweet_1.lower().split()
            
            # Remove stopwords
            tweet_3 = [w for w in tweet_2 if w not in sw]
            
            # Lemmatize
            if LEM:
                tweet_3 = [uralicApi.lemmatize(w, "fin") for w in tweet_3]
            
            processed_tweets.append(tweet_3)
    
        else:

            # Remove URL
            tweet_1 = remove_url(tweets[i]["text"])
            
            # Lower case and split
            tweet_2 = tweet_1.lower().split()
            
            # Remove stopwords
            tweet_3 = [w for w in tweet_2 if w not in sw]
            
            #  Lemmatize
            if LEM:
                tweet_3 = [uralicApi.lemmatize(w, "fin") for w in tweet_3]
        
            processed_tweets.append(tweet_3)

    return processed_tweets

def word_frequency(all_tweets):
    flat_list = [item for sublist in all_tweets for item in sublist]
    word_counts = Counter(flat_list)
    return dict(word_counts)

def flatten(l): 
    flattened = []
    for i in range(len(l)):
        flat_list = [item for sublist in l[i] for item in sublist]
        flattened.append(flat_list)
    return flattened

def main():

    # Write the data path
    data_dir = "/run/user/1282311/gvfs/smb-share:server=data.triton.aalto.fi,share=scratch/cs/networks/ecanet/elections/raw_tweets/all_data"
    
    # Select the word
    seed_word = "yle"

    # Lemmatize
    LEM = False

    ##########################################################################################################

    stopwords_fin = load_stopwords()

    files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    files = files[0:4]
    f_count = len(files)
    freq_dict_all = dict()
    selected_structs = []

    for f in files:
        
        with open(os.path.join(data_dir, f), "r") as read_file:
            data = json.load(read_file)

        all_tweets_processed = process_text(data, stopwords_fin, LEM)
        #print(all_tweets_processed)
        if LEM:
            all_tweets_processed = flatten(all_tweets_processed)
        freq_dict_batch = word_frequency(all_tweets_processed)
        freq_dict_all = Counter(freq_dict_all) + Counter(freq_dict_batch)

        for tweet in all_tweets_processed:
            if (seed_word in tweet) or (("#" + seed_word) in tweet):
                selected_structs.append(tweet)
    
        
        f_count -= 1
        print("A file completed. This many more: ", f_count)
    
    
    #all_tweets = load_tweet_file(data_path)
    # Flatten the sublists
    #all_tweets_flatten = flatten(all_tweets_processed) 
    #all_tweets_flatten = all_tweets_processed 

    
    
    # Keep the structs with seed word

    # Flatten the struct list
    flattened_structs = [item for sublist in selected_structs for item in sublist]
    #print(flattened_structs)
    struct_counts = list(Counter(flattened_structs).items())
    #print(struct_counts)
    # Normalized occurences
    n_occ = dict()
    
    for s in struct_counts:
        #print(s)
        if freq_dict_all[s[0]] > 50: #Select threshold here
            n_occ[s[0]] = (s[1]/freq_dict_all[s[0]], freq_dict_all[s[0]])

    #print(n_occ)

    # This prints/saves the normalized co-occurence score for words that appears the most with selected seed word.
    sorted_dict = sorted(n_occ.items(), key=lambda kv: kv[1])
    
    #print(sorted_dict)

    with open('cooccurence_result_try.json', 'w', encoding='utf8') as fp:
        json.dump(sorted_dict, fp, ensure_ascii=False)
    

if __name__ == '__main__':
    main()
    