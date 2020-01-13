import pickle
import os
import json
import random
import networkx as nx
import pandas as pd

PRE = True
MID = False
POST = False

N_sample = 50 #From each bubble

topics = ["ilmastonmuutos", "sote", "maahanmuutto", "hallitus", "vihapuhe", "rasismi", "tekoäly", "yle", "talous", "demarit", "keskusta", "kokoomus", "perussuomalaiset", "vasemmisto", "vihreät", "populismi"]


def easier_indexing(Gs):
    """
        Quick tool for easier indexing 
    """
    keys = [Gs[i][1][:-8] for i in range(len(Gs))]
    topic_dict = dict(zip(keys, list(range(len(keys)))))
    return topic_dict


if PRE:
    Gs = pickle.load(open("graphlist_pre.pickle", "rb"))
    data_dir = "/run/user/1282311/gvfs/smb-share:server=data.triton.aalto.fi,share=scratch/cs/networks/ecanet/elections/raw_tweets/finnish_election"
    attach = "pre"
    
if MID: 
    Gs = pickle.load(open("graphlist_mid.pickle", "rb"))
    data_dir = "/run/user/1282311/gvfs/smb-share:server=data.triton.aalto.fi,share=scratch/cs/networks/ecanet/elections/raw_tweets/european_election"
    attach = "mid"
        
if POST:
    Gs = pickle.load(open("graphlist_post.pickle", "rb"))
    data_dir = "/run/user/1282311/gvfs/smb-share:server=data.triton.aalto.fi,share=scratch/cs/networks/ecanet/elections/raw_tweets/post_elections"
    attach = "post"

topic_dict = easier_indexing(Gs)

files = [f for f in os.listdir(data_dir) if f.endswith('.json')]


for topic in topics:
    
    f_count = len(files)
    print("Processing: ", topic)

    bubble1_tweets = []
    bubble2_tweets = []

    network = Gs[topic_dict[topic]][0][0][0]

    bubble1 = set([user[1]["handle"] for user in network.nodes(data=True) if user[1]["group"] == "#fcae91FF"])
    bubble2 = set([user[1]["handle"] for user in network.nodes(data=True) if user[1]["group"] == "#7828a0FF"])

    assert (len(bubble1) + len(bubble2)) == len(network), "Counts do not match"


    for f in files:
            
        with open(os.path.join(data_dir, f), "r") as read_file:
            data = json.load(read_file)
            
        for i in range(len(data)):
            
            if ("retweeted_status" in data[i]) and (topic in data[i]["retweeted_status"]["hashtags"]):

                if data[i]["user"]["id"] in bubble1:
                    bubble1_tweets.append(data[i]["retweeted_status"]["text"])
                
                elif data[i]["user"]["id"] in bubble2:
                    bubble2_tweets.append(data[i]["retweeted_status"]["text"])
                    
                else:
                    pass
                
            elif (topic in data[i]["hashtags"]):
                
                if data[i]["user"]["id"] in bubble1:
                    bubble1_tweets.append(data[i]["text"])
                
                elif data[i]["user"]["id"] in bubble2:
                    bubble2_tweets.append(data[i]["text"])
                else:
                    pass
        
            else:
                continue
            
        f_count -= 1
        print("A file completed. This many more: ", f_count)

    
    bubble1_random_sample = random.sample(bubble1_tweets, N_sample)
    bubble2_random_sample = random.sample(bubble2_tweets, N_sample)

    bubblemark = ["B1"] * N_sample + ["B2"] * N_sample
    random_sample = bubble1_random_sample + bubble2_random_sample

    df = pd.DataFrame(data={'BUBBLE': bubblemark, 'TWEET': random_sample})
    df_shuffled = df.sample(frac=1).reset_index(drop=True)
    df_shuffled.to_csv("random_samples/" + attach + "/random_sample_" + attach + "_" + topic + ".csv")

    print("Processing completed: ", topic)