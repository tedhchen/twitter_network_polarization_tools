import networkx as nx
import os
import matplotlib.pyplot as plt
import pickle
import nxmetis
import numpy as np
from tweet_polarization import *

def data_to_edges(HT):
    
    files = [f for f in os.listdir("has_topic")]
    rt_edges = []

    for f in files:

        rt_edges.append(f)
        if (os.path.exists("has_topic/" + f + "/has_" + HT + ".txt")):
            with open("has_topic/" + f + "/has_" + HT + ".txt") as ft:
                content = ft.readlines()
                content = [x.strip() for x in content] 
                content = [x[2:-1].split(",") for x in content] 
                rt_edges_new = [(int(content[i][1]), int(content[i][2])) for i, x in enumerate(content)]
                rt_edges = rt_edges + rt_edges_new
                
    return rt_edges

def partition_here(graph):
    
    if nx.is_empty(graph):
        return 0, 0
    Gcc = sorted(nx.connected_components(graph), key=len, reverse=True)
    G = graph.subgraph(Gcc[0])
    settings = nxmetis.MetisOptions(ncuts=4, niter=200, ufactor=280)
    par = nxmetis.partition(G, 2, options=settings)
    
    community1 = par[1][0]
    community2 = par[1][1]

    rwc = np.mean(randomwalk_polarization(G, 100, 0.02, 1000, community1, community2))
    prc = len(G)/len(graph)
    
    return rwc, prc


#TOPIC = "vihreät"
TOPIC = "perussuomalaiset"

rt_edges = data_to_edges(TOPIC)

G = nx.Graph()
switch = True #not always needed
i = 0 

for link in rt_edges:
    
    if link[:5] == "2019-":
        current_time = link
        current_rwc, current_gcr = partition_here(G)
        continue
        
    G.add_edge(*link)
    if switch:
        #pos = forceatlas2.forceatlas2_networkx_layout(G, pos=None, iterations=1)
        pos = nx.spring_layout(G, seed=12)
    else:
        #pos = forceatlas2.forceatlas2_networkx_layout(G, pos=pos, iterations=1)
        pos = nx.spring_layout(G, seed=12)
        switch = False
    
    i += 1
    
    f = plt.figure()
    plt.clf()
    nx.draw(G, pos = pos, node_size = 10, node_color = "darkgreen", label="time", with_labels= False)
    plt.annotate("time: " + current_time, (5,275), xycoords = 'figure points')
    plt.annotate("rwc: " + str(round(current_rwc, 2)), (5,265), xycoords = 'figure points')
    plt.annotate("gcr: " + str(round(current_gcr, 2)), (5,255), xycoords = 'figure points')

    f.savefig("pics_perussuomalaiset/img" + str(i) + ".jpg")
    plt.close()


### NOTE ####

# After having all the images saved in the folder, run the following on command line:
##### ffmpeg -f image2 -i camera%d.jpg time-lapse.mp4 #####