#import networkx as nx
#module load graph_tool
#from graph_tool.all import *
import graph_tool.all as gt
import matplotlib.pyplot as plt

ht = "ilmastonmuutos"
g = gt.load_graph(ht + "/" + ht + "_retweet_network_giant.gml")
#g = gt.Graph()


#bmodel = gt.minimize_nested_blockmodel_dl(g, B_min=2, B_max=2)
current_bmodel = gt.minimize_blockmodel_dl(g, B_min=2, B_max=2, deg_corr=True, verbose=True)

#for _ in range(100):
#    bmodel = gt.minimize_blockmodel_dl(g, B_min=2, B_max=2, deg_corr=True, verbose=True)
#    if (bmodel.entropy() < current_bmodel.entropy()):
#        current_bmodel = bmodel
#    else:
#        continue

#print(len(bmodel.get_bs()))
#bmodel.draw()
current_bmodel.draw()
b = current_bmodel.get_blocks()
community = g.new_vertex_property("int16_t")
for v in g.vertices(): 
    community[v] = b[v]

g.vertex_properties["community"] = community
print(community)
g.list_properties()

g.save(ht + "_with_com.graphml")

#e = bmodel.get_matrix()
#plt.matshow(e.todense())
#plt.savefig("football-edge-counts.svg")
#print(g.vertex_properties["label"][2])
#print(bmodel.get_blocks()[15])
#with open("kokoomus_retweet_network_giant_edgelist.csv", 'r') as f:
    #content = f.readlines()

#content = [x.strip() for x in content] 
#splitted_content = [x.split(" ") for x in content]
#int_conv = [[int(a), int(b)] for (a,b) in splitted_content]
#print(len(int_conv))

#for edge in int_conv:
#    g.add_edge(edge[0], edge[1])
#g.add_edge_list(int_conv)


    #splitted_content = [x.split(" ") for x in reader]
    #reader_network = list(splitted_content)

#print(len(reader_network))
#print(reader_network[0])
#g.add_edge_list(reader_network)

#g = gt.load_graph_from_csv("kokoomus_retweet_network_giant_edgelist.csv")
#print(g)

#print(g.get_vertices())
#gt.graph_draw(a, "output.pdf")

#g = gt.price_network(300)
#pos = gt.fruchterman_reingold_layout(a, n_iter=1000)
#gt.graph_draw(a, pos=pos, output="graph-draw-fr.pdf")
#ht = "sote"

#G = nx.read_gml("/m/cs/project/elebot/analysis/pol/"+str(ht) + "/" +str(ht)+ "_retweet_network.gml")

#print(nx.info(G))
#print(list(G.nodes)[0:10])
#nx.write_edgelist(G, "test.edgelist")
#G_int = nx.convert_node_labels_to_integers(G, label_attribute = "orig")

#nx.write_gml(G_int, "/m/cs/project/elebot/analysis/pol/"+str(ht) + "/" +str(ht)+ "_retweet_network_int.gml")