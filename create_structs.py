import os, json

hashtags_to_study = ["jotainrajaa", "kokoomus", "maahanmuutto", "perussuomalaiset", "sote", "vihreät"]

data_dir = "/m/cs/project/elebot/processeddata/notebook_outputs/national_data/fin_filtered"
files = [f for f in os.listdir(data_dir) if f.endswith('.json')]

for ht in hashtags_to_study:

    to_be_saved = []

    for f in files:
        
        with open(os.path.join(data_dir, f), "r") as read_file:
            data = json.load(read_file)
            
        for i in range(len(data)):
            
            if "retweeted_status" in data[i]:
                if (ht in set(data[i]["retweeted_status"]["hashtags"])):
                    to_be_saved.append(data[i])
                
            else:
                if (ht in set(data[i]["hashtags"])):
                    to_be_saved.append(data[i])

    sub_data_dir = "/m/cs/project/elebot/analysis/pol/" + str(ht)
    
    with open(os.path.join(sub_data_dir, str(ht) + "_structs.json"), 'w+') as outfile:  
        json.dump(to_be_saved, outfile)