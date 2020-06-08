# prep
import os, json, ast, pickle
import graph_tool.all as gt

peach = '#fcae91FF'
purple = '#7828a0FF'

# Loading sbm results
with open('output/results/period2_topics_sbm.pickle', 'rb') as in_pickle:
	results = pickle.load(in_pickle)

# Loading metis partitions
with open('output/results/period2_topics_metis_simple.pickle', 'rb') as in_pickle:
	simple_results = pickle.load(in_pickle)
	
# Plotting
def plot_metis(gt_output, metis_part, layout):
	g = gt_output[0]
	blocks = gt_output[1][0]
	v_col = g.new_vertex_property('string')
	for v in g.vertices():
		if int(g.vp.acc[v]) in metis_part[0]:
			v_col[v] = peach
		if int(g.vp.acc[v]) in metis_part[1]:
			v_col[v] = purple
	blocks.draw(vertex_color = v_col, vertex_fill_color = v_col, pos = layout)
			
#
gt_layout2 = {}
for topic in results:
	gt_layout2[topic] = gt.graph_draw(results[topic][0])


#
for topic in simple_results:
	name = topic[0]
	plot_metis(results[name], topic[1][0:2], layout = gt_layout2[name])

