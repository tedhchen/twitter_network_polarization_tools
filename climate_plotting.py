# Prep
from tweet_polarization import * # make sure graphtools is uncommented in tweet_polarization.py
import itertools

# Setting colours
mk = ['#006E82FF', 
	  '#8214A0FF',
	  '#005AC8FF',
	  '#00A0FAFF',
	  '#FA78FAFF',
	  '#14D2DCFF',
	  '#AA0A3CFF',
	  '#FA7850FF',
	  '#0AB45AFF',
	  '#F0F032FF',
	  '#A0FA82FF',
	  '#FAE6BEFF',
	 ]
lightgray = '#E5E5E5FF'

# Reading in parameters
PARAMS = {}
with open('params.txt', encoding = 'utf-8') as params:
	for line in params:
		param, value = line.strip().split(':', 1)
		PARAMS[param] = value.split(';')
		if PARAMS[param] == ['']:
			PARAMS[param] = None

# Loading results from results_out() in main analysis script
with open('output/topics_metis_simple.pickle', 'rb') as in_pickle:
	results = pickle.load(in_pickle)

#------------------------#
# Functions for plotting #
#------------------------#

# Load edgelists, create gt networks
def to_network(filepath, results, pos = False):
	with open(filepath, 'rb') as in_pickle:
		rts = pickle.load(in_pickle)
	# Renaming vertices
	vs = []
	for rt in rts:
		vs.extend(rt)
	vs = sorted(set(vs))
	acc2node = {label: i for i, label in enumerate(vs, 0)}
	node2acc = {v: k for k, v in acc2node.items()}
	# Creating Graph
	g = gt.Graph(directed = False)
	for edge in rts:
		g.add_edge(acc2node[edge[0]], acc2node[edge[1]])
	# Saving node names
	c = results[filepath[25:-16] + filepath[23]][0]
	accnames = g.new_vertex_property('string')
	comm = g.new_vertex_property('bool')
	for v in g.vertices():
		accnames[v] = node2acc[v]
		if int(accnames[v]) in c[0]:
			comm[v] = 0
		else:
			comm[v] = 1
	g.vertex_properties['acc'] = accnames
	g.vertex_properties['comm'] = comm
	# Getting largest component
	g = gt.extract_largest_component(g, directed = False, prune = True)
	gt.remove_self_loops(g)
	if pos:
		g.vertex_properties['pos'] = gt.sfdp_layout(g)
	return g

# Create joint retweet networks from filepaths
def to_network_union(filepath1, filepath2, results):
	with open(filepath1, 'rb') as in_pickle:
		rts1 = pickle.load(in_pickle)
	with open(filepath2, 'rb') as in_pickle:
		rts2 = pickle.load(in_pickle)
	rts = list(set(rts1 + rts2))
	# Renaming vertices
	vs = []
	for rt in rts:
		vs.extend(rt)
	vs = sorted(set(vs))
	acc2node = {label: i for i, label in enumerate(vs, 0)}
	node2acc = {v: k for k, v in acc2node.items()}
	# Creating Graph
	g = gt.Graph(directed = False)
	for edge in rts:
		g.add_edge(acc2node[edge[0]], acc2node[edge[1]])
	# Saving node names and assigning communities
	c1 = results[filepath1[25:-16] + filepath1[23]][0]
	c2 = results[filepath2[25:-16] + filepath2[23]][0]
	accnames = g.new_vertex_property('string')
	comm1 = g.new_vertex_property('int')
	comm2 = g.new_vertex_property('int')
	for v in g.vertices():
		accnames[v] = node2acc[v]
		if int(accnames[v]) in c1[0]:
			comm1[v] = 0
		elif int(accnames[v]) in c1[1]:
			comm1[v] = 1
		else:
			comm1[v] = 2
		if int(accnames[v]) in c2[0]:
			comm2[v] = 0
		elif int(accnames[v]) in c2[1]:
			comm2[v] = 1
		else:
			comm2[v] = 2
	g.vertex_properties['acc'] = accnames
	g.vertex_properties['comm1'] = comm1
	g.vertex_properties['comm2'] = comm2
	# Getting largest component
	gt.remove_self_loops(g)
	g = gt.extract_largest_component(g, directed = False, prune = True) 
	return g

# Simple drawing function
def draw_metis(g, output = None):
	v_col = g.new_vertex_property('string')
	for v in g.vertices():
		if g.vp.comm[v]:
			v_col[v] = mk[1]
		else:
			v_col[v] = mk[7]
	if 'pos' in g.vp:
		gt.graph_draw(g, vertex_color = v_col, vertex_fill_color = v_col, edge_color = lightgray, pos = g.vp['pos'], output = output)
	else:
		gt.graph_draw(g, vertex_color = v_col, vertex_fill_color = v_col, edge_color = lightgray, output = output)

# Drawing function for joint networks
def draw_metis_union(g, subset = False, pos = None, output = None):
	v_col = g.new_vertex_property('string')
	v_shape = g.new_vertex_property('string')
	v_plot = g.new_vertex_property('bool')
	for v in g.vertices():
		v_col[v] = lightgray
		v_shape[v] = 'circle'
		if (g.vp.comm1[v] == 0) and (g.vp.comm2[v] == 0):
			v_plot[v] = True
			v_col[v] = mk[8] #dark green
		if (g.vp.comm1[v] == 1) and (g.vp.comm2[v] == 0):
			v_plot[v] = True
			v_col[v] = mk[1] #dark purple
		if (g.vp.comm1[v] == 0) and (g.vp.comm2[v] == 1):
			v_plot[v] = True
			v_col[v] = mk[10] #light green
			#v_shape[v] = 'square'
		if (g.vp.comm1[v] == 1) and (g.vp.comm2[v] == 1):
			v_plot[v] = True
			v_col[v] = mk[4] #light purple
			#v_shape[v] = 'square'
	if subset:
		g.set_vertex_filter(v_plot)
		g = gt.extract_largest_component(g)
	if 'pos' in g.vp:
		gt.graph_draw(g, vertex_color = 'black', vertex_fill_color = v_col, vertex_size = 5, vertex_shape = v_shape, vertex_rotation = 0.785398, edge_color = lightgray, pos = g.vp['pos'], output = output)
	elif pos != None:
		gt.graph_draw(g, vertex_color = 'black', vertex_fill_color = v_col, vertex_size = 5, vertex_shape = v_shape, vertex_rotation = 0.785398, edge_color = lightgray, pos = pos, output = output)
	else:
		pos = gt.graph_draw(g, vertex_color = '#343434FF', vertex_fill_color = v_col, vertex_size = 12, vertex_shape = v_shape, vertex_pen_width = 0.05, vertex_rotation = 0.785398, edge_color = 'lightgray', output_size = (1200,1200), output = output)
		return(pos)



#-------------------------#
# Running plotting script #
#-------------------------#

# Making joint network
g1 = to_network_union('output/edgelists/period1/CLIMATE_edgelist.pickle', 'output/edgelists/period1/IMMIGRATION_edgelist.pickle', results) 
g2 = to_network_union('output/edgelists/period1/CLIMATE_edgelist.pickle', 'output/edgelists/period1/ECONOMICPOLICY_edgelist.pickle', results) 

# 
draw_metis_union(g1, subset = True, output = 'output/paper_plots/p1_climate_economicpolicy2.pdf')
draw_metis_union(g2, subset = True, output = 'output/paper_plots/p1_climate_immigration2.pdf')

# Plotting all joint networks (within period)
# topics = PARAMS['TOPICS']
# for period in range(1,4):
# 	path = 'output/edgelists/period' + str(period) + '/'
# 	for pair in itertools.combinations(topics, 2):
# 		g = to_network_union(path + pair[0] + '_edgelist.pickle', path + pair[1] + '_edgelist.pickle', results)
# 		draw_metis_union(g, subset = True, output = 'output/joint_plots/p' + str(period) + '_' + pair[0] + '_' + pair[1] + '.png')
