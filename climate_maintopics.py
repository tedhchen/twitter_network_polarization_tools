# Prep
from tweet_polarization import *
import graph_tool.all as gt

PARAMS = {}
with open('params.txt', encoding = 'utf-8') as params:
	for line in params:
		param, value = line.strip().split(':', 1)
		PARAMS[param] = value.split(';')
		if PARAMS[param] == ['']:
			PARAMS[param] = None

# Functions

# To edgelists

# Load edgelists, create gt networks

def to_network(filepath):
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
	accnames = g.new_vertex_property('string')
	for v in g.vertices():
		accnames[v] = node2acc[v]
	g.vertex_properties['acc'] = accnames
	# Getting largest component
	g = gt.extract_largest_component(g, directed = False, prune = True) 
	return g

# Stochastic blockmodel
def comm_sbm(g, runs = 1, seed = 0):
	mdl = math.inf 	# Minimum description length starts at inf
	gt.graph_tool.seed_rng(seed) # Setting seed
	# Starting runs
	for i in range(runs):
		state = gt.minimize_blockmodel_dl(g, B_max = 2, deg_corr = True) # sbm
		# Check result against previous best
		if state.entropy() < mdl:
			mdl = state.entropy()
			best = state
			best_i = i + 1
	return best, mdl, best_i

# Calculating polarization
def polarization_score(blockstate):
	if blockstate.B == 1:
		p_score = 0
	else:
		# Get the number of ties in each block
		mat = blockstate.get_matrix().todense()
		# Get community sizes
		bsizes = blockstate.get_nr().get_array()
		# Possible ties in each block
		denon = bsizes.reshape((2,1))*bsizes
		for i in range(0,2):
			denon[i,i] -= bsizes[i]
		# Density in each block
		den = mat/denon
		# Getting score
		ps = (den.trace() - 2*den[0,1])/den.sum()
		p_score = ps[0,0]
	return p_score

topics = os.listdir('output/edgelists/period3/')

# g = to_network('output/edgelists/period1/' + topics[14])
# comms = comm_sbm(g, runs = 500, seed = 161536)
# ps = polarization_score(comms[0])

results = {}
for topic in topics:
	print('Starting: ' + topic[:-16])
	g = to_network('output/edgelists/period3/' + topic)
	comms = comm_sbm(g, runs = 1, seed = 132676)
	ps = polarization_score(comms[0])
	results[topic[:-16]] = [g, comms, ps]
	
with open('output/results/period3_topics_sbm.pickle', 'wb') as out_pickle:
	pickle.dump(results, out_pickle)