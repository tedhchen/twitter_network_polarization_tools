def write_the_communities(comlabels, ht):
    
    community1, community2 = [], []

    for key in comlabels:

        if comlabels[key] == "0":
            community1.append(key)
        else:
            community2.append(key)
    
    with open(ht+"/"+ht+"_community1.txt", 'w') as f:
        for item in community1:
            f.write("%s\n" % item)
            
    with open(ht+"/"+ht+"_community2.txt", 'w') as f:
        for item in community2:
            f.write("%s\n" % item)
            
    return 1

def main():

    #ht_list = ["perussuomalaiset", "jotainrajaa", "kokoomus", "maahanmuutto", "sote", "vihreät"]
    ht_list = ["ilmastonmuutos"] #this hashtag has a special format

    for ht in ht_list:
        
        with open(ht+"/"+ht + "_com.txt") as f:
            content = f.readlines()

        content = [x.strip() for x in content] 
        splitted_content = [x.split(",") for x in content]
        com_structure = [[sub[1], sub[3]] for sub in splitted_content][1:]
        community_dict = dict(com_structure)
        
        if write_the_communities(community_dict, ht):
            print(ht + " communities succesfully written.")