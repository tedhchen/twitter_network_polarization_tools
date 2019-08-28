#import graph_tool.all as gt
#import matplotlib.pyplot as plt
import networkx as nx
import metis

# Load the graph
ht = "ilmastonmuutos"
G = nx.read_gml(ht + "/" + ht + "_retweet_network_giant.gml")

#(edgecuts, parts) = metis.part_graph(G, 2, ptype="rb", contig=True, objtype="cut", ufactor=445, niter = 100)
(edgecuts, parts) = metis.part_graph(G, 2, ptype="kway", contig=True, objtype="cut", niter = 100)
combined = dict(list(zip(G.nodes(), parts)))
nx.set_node_attributes(G, combined, 'comx')
nx.write_graphml(G, ht + "_with_com_metis.graphml")
#G_int = nx.convert_node_labels_to_integers(G)

#print(nx.info(G))
#print(list(G.edges)[:10])

#d = {}
#with open("testaa.txt") as f:
#    for line in f:
#       (key, val) = line.split()
#       d[int(key)] = val


#print(d)

#nx.set_node_attributes(G_int, d, "section")
#nx.write_gml(G_int, "final_test.gml")

#nx.write_gml(G_int, "climate_int.gml")
#nx.write_edgelist(G_int, "test.edgelist", data=False)
#G_int = nx.convert_node_labels_to_integers(G)
#nx.write_gml(G_int, "fixed.gml")
#nx.write_edgelist(G_int, "fixed_edgelist.csv", delimiter = ",", data=False)
#print(nx.info(G_int))
#G = metis.example_networkx()

# Compute the "ground truth"
#state = gt.minimize_blockmodel_dl(g, B_min=2, B_max=2, deg_corr=True, verbose=True)
#e = state.get_matrix()
#print(e)
#matshow(e.todense())
#savefig("football-edge-counts.svg")
#state = state.copy(B=g.num_vertices()) NOT SURE WHAT THIS DOES

#dS, nattempts, nmoves = state.mcmc_sweep(niter=1000)

#print("Change in description length:", dS)
#print("Number of accepted vertex moves:", nmoves)

# Visualize and save the block model

#state.draw()

# Get the node membership
#b = state.get_blocks()

# New node property
#community = g.new_vertex_property("int16_t")

#for v in g.vertices(): 
#    community[v] = b[v]

#g.vertex_properties["community"] = community
#print(community)
#g.list_properties()
#g.save(ht + "_with_com.graphml")