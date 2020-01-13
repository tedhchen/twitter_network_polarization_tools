import networkx as nx
import matplotlib.pyplot as plt
import pickle
from fa2 import ForceAtlas2
from matplotlib.backends.backend_pdf import PdfPages
from collections import Counter
import matplotlib.patches as mpatches


def easier_indexing(Gs):
    """
        Quick tool for easier indexing 
    """
    keys = [Gs[i][1][:-5] for i in range(len(Gs))]
    topic_dict = dict(zip(keys, list(range(len(keys)))))
    return topic_dict

def side_renaming(network1, network2):
    """ 
        Rename stances of nodes on the topic.

        Parameters
        ----------
        network1 : networkx.classes.graph.Graph
            The first network
        network2 : networkx.classes.graph.Graph
            The second network
    """

    # There is probably faster way to perform this, optimize later if needed
    for i in range(len(network1.nodes)):
    
        if (network1.nodes[i]["group"] == "#fcae91FF"):
            network1.nodes[i]["T1"] = "0"

        elif (network1.nodes[i]["group"] == "#7828a0FF"):
            network1.nodes[i]["T1"] = "1"
            
        else:
            print("Error with group encoding!")
        
        
    for i in range(len(network2.nodes)):
        
        if (network2.nodes[i]["group"] == "#fcae91FF"):
            network2.nodes[i]["T2"] = "0"
            
        elif (network2.nodes[i]["group"] == "#7828a0FF"):
            network2.nodes[i]["T2"] = "1"
            
        else:
            print("This should not be printed! Error with group encoding!")

    return network1, network2

def encode_sides(network_union):
    """
        This function encodes all the possible combinations of different supporting behaviour

        Parameters
        ----------
        network_union : networkx.classes.graph.Graph
            The union of network1 and network1
    """
    user_stances = dict()

    for node in network_union.nodes.data():
        if ("T1" in node[1] and "T2" in node[1]):
            user_stances[node[1]["handle"]] = (node[1]["T1"], node[1]["T2"])
        else:
            if ("T1" not in node[1]):
                user_stances[node[1]["handle"]] = ("NA", node[1]["T2"])
                
            if ("T2" not in node[1]):
                user_stances[node[1]["handle"]] = (node[1]["T1"], "NA")

    assert len(user_stances) == len(network_union), "Check the side encoding"

    return user_stances

def get_statistics(network_union, user_sides):
    
    N_tweeting_on_either = len(network_union)
    stance_counts = Counter(user_sides.values())

    # How the stances on second topic differ among the users that agreed on the first topic
    try:
        T1G1_T2G1 = stance_counts[('0', '0')]/(stance_counts[('0', '0')] + stance_counts[('0', '1')])   
        T1G1_T2G2 = 1 - T1G1_T2G1
    except ZeroDivisionError:
        T1G1_T2G1 = "NA"
        T1G1_T2G2 = "NA"

    # How the stances on second topic differ among the users that disagreed on the first topic
    try:
        T1G2_T2G1 = stance_counts[('1', '0')]/(stance_counts[('1', '1')] + stance_counts[('1', '0')])
        T1G2_T2G2 = 1 - T1G2_T2G1
    except ZeroDivisionError:
        T1G2_T2G1 = "NA"
        T1G2_T2G2 = "NA"

    N_tweeting_on_both = stance_counts[('0', '0')] + stance_counts[('1', '1')] + stance_counts[('1', '0')] + stance_counts[('0', '1')]
    stats_dict = {"N_tweeting_on_either": N_tweeting_on_either, "N_tweeting_on_both": N_tweeting_on_both, (TOPIC1 + " B1", TOPIC2 + " B1"): T1G1_T2G1, (TOPIC1 + " B1", TOPIC2 + " B2"): T1G1_T2G2, (TOPIC1 + " B2", TOPIC2 + " B1"): T1G2_T2G1, (TOPIC1 + " B2", TOPIC2 + " B2"): T1G2_T2G2}

    return stats_dict


PARTIES = ["kokoomus", "vihreät", "keskusta", "perussuomalaiset", "vasemmisto"]
THEMES = ["ilmastonmuutos", "sote", "maahanmuutto", "hallitus", "vihapuhe", "rasismi", "tekoäly", "yle", "talous"]

total_dict = dict()

for TOPIC1 in PARTIES:
    for TOPIC2 in THEMES: 

        # Load the nested list of graphs that the pipeline outputs as a pickle
        Gs = pickle.load(open("graphlist.pickle", "rb"))

        # Easier indexing
        topic_dict = easier_indexing(Gs)

        # Load the corresponding networks
        network1 = Gs[topic_dict[TOPIC1]][0][0][0]
        network2 = Gs[topic_dict[TOPIC2]][0][0][0]

        # Rename the sides of each node
        network1, network2 = side_renaming(network1, network2)

        # Use handle names as node IDs
        network1 = nx.relabel_nodes(network1, nx.get_node_attributes(network1, "handle"))
        network2 = nx.relabel_nodes(network2, nx.get_node_attributes(network2, "handle"))

        # Take the union of the two networks
        network_union = nx.compose(network1, network2)

        # Get the positions of nodes
        #positions = pos_fa_layout(network_union)

        # Side encoding
        user_sides = encode_sides(network_union)

        # Compute the selected stats
        stance_stats = get_statistics(network_union, user_sides)
        total_dict[TOPIC1, TOPIC2] = stance_stats

G = nx.Graph()

for p in PARTIES:
    for t in THEMES:
        G.add_edge(p + " B1", t + " B1", weight=total_dict[(p,t)][p + " B1", t + " B1"])
        G.add_edge(p + " B1", t + " B2", weight=total_dict[(p,t)][p + " B1", t + " B2"])
        G.add_edge(p + " B2", t + " B1", weight=total_dict[(p,t)][p + " B2", t + " B1"])
        G.add_edge(p + " B2", t + " B2", weight=total_dict[(p,t)][p + " B2", t + " B2"])

for u,v,d in G.edges(data=True):
    if d['weight'] == "NA":
        d['weight'] = 0

pos = nx.spring_layout(G)

elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] > 0.7]
esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= 0.3]

fig = plt.figure(figsize=(20,15))
#nx.draw(G,pos=pos, with_labels=True)

# nodes
nx.draw_networkx_nodes(G, pos, node_size=700)

# edges
nx.draw_networkx_edges(G, pos, edgelist=elarge,
                       width=6)

# labels
_ = nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')

with PdfPages("topicnet.pdf") as pdf:
    pdf.savefig(fig)