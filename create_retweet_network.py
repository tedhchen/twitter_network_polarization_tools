import os, json
import networkx as nx
#from graph_tool.all import *



def get_giant_component(G):

    #print("The graph is connected: ", nx.is_connected(G))
    #print("The number of components: ", nx.number_connected_components(G))
    
    cc = nx.connected_components(G)

    subgraphs_sizes = [len(sg) for sg in cc]
    #print(subgraphs_sizes)

    
    #print("Percentage of nodes in giant component: ", giant_component_ratio)

    #largest_cc = max(nx.connected_components(G), key=len)
    #len(largest_cc)
    #print("The size of giant component: ", len(largest_cc))


    #subgraphs = [G.subgraph(c) for c in nx.connected_components(G)]
    
    GC = max(nx.connected_component_subgraphs(G), key=len)
    #print(len(GC.nodes))
    #print(type(GC))

    giant_component_ratio = len(GC.nodes)/sum(subgraphs_sizes)

    return GC, giant_component_ratio

hashtags_to_study = ["jotainrajaa", "kokoomus", "maahanmuutto", "perussuomalaiset", "sote", "vihreät"]

for ht in hashtags_to_study:
    data_dir = "/m/cs/project/elebot/analysis/pol/" + str(ht)
    f = str(ht) + "_structs.json"

    with open(os.path.join(data_dir, f), "r") as read_file:
        data = json.load(read_file)

    retweets = [] # (a,b) where b is retweeted by a

    for i in range(len(data)):
    
        if "retweeted_status" in data[i]:
            #retweets.append((int(data[i]["user"]["id"]), int(data[i]["retweeted_status"]["user"]["id"]))) # (a,b) where b is retweeted by a
            retweets.append((data[i]["user"]["id"], data[i]["retweeted_status"]["user"]["id"]))

    G = nx.Graph()
    G.add_edges_from(retweets)
    
    giantcomponent, gc_frac = get_giant_component(G)

    #nx.write_gml(giantcomponent, "/m/cs/project/elebot/analysis/pol/"+str(ht) + "/" +str(ht)+ "_retweet_network_giant.gml")
    #nx.write_edgelist(giantcomponent, "/m/cs/project/elebot/analysis/pol/"+str(ht) + "/" +str(ht)+ "_retweet_network_giant_edgelist.csv", data=False)
    nx.write_graphml(giantcomponent, "/m/cs/project/elebot/analysis/pol/"+str(ht) + "/" +str(ht)+ "_retweet_network_giant.graphml")
    print("A " + str(ht) + " network completed. And the GC-ratio is: ", gc_frac)