# Prep
from tweet_polarization import *

PARAMS = {}
with open('params.txt', encoding = 'utf-8') as params:
	for line in params:
		param, value = line.strip().split(':', 1)
		PARAMS[param] = value.split(';')
		if PARAMS[param] == ['']:
			PARAMS[param] = None
			
# Parsing tweets
# Period1
run_parser(set1 = PARAMS['SET1'], set2 = None, all_text = False, raw = '/home/tc/work/climate_polarization/raw_tweets/period1/', outfolder = 'parsed/period1')

# Period2
run_parser(set1 = PARAMS['SET2'], set2 = None, all_text = False, raw = '/home/tc/work/climate_polarization/raw_tweets/period2/', outfolder = 'parsed/period2')

# Period3
run_parser(set1 = PARAMS['SET3'], set2 = None, all_text = False, raw = '/home/tc/work/climate_polarization/raw_tweets/period3/', outfolder = 'parsed/period3')

# Creating edgelists
# Period1
to_links(set1 = PARAMS['SET1'], set2 = None, infolder = 'parsed/period1', outfolder = "edgelists/period1", period_size = 45, period_interval = 45)

# Period2
to_links(set1 = PARAMS['SET2'], set2 = None, infolder = 'parsed/period2', outfolder = "edgelists/period2", period_size = 42, period_interval = 42)

# Period3
to_links(set1 = PARAMS['SET3'], set2 = None, infolder = 'parsed/period3', outfolder = "edgelists/period3", period_size = 66, period_interval = 66)

# Load edgelists, create gt networks
topics = os.listdir('edgelists/period1/')
'edgelists/period1/' + topics[0]

def to_network(filepath):
	with open(filepath, 'rb') as in_pickle:
		rts = pickle.load(in_pickle)[0][0]
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
	return ps[0,0]

g = to_network('edgelists/period1/' + topics[14])
comms = comm_sbm(g, runs = 200, seed = 1616804)
ps = polarization_score(comms[0])
