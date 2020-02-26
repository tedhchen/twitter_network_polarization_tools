from tweet_polarization import *

# Load or simulate data
# This is the top 100 hashtags:
def inpickle(infile):
	with open(infile, 'rb') as in_pickle:
		freq_dict = pickle.load(in_pickle)
	return freq_dict

# Get communities of observed network(s)
def comm_detect(Gs, func):
	functions = {'metis':metis_partition, 'sbm':sbm_strict2}
	if func in functions:
		comms = []
		for G in Gs:
			comm = functions[func](G)
			comms.append(comm)
		return comms
	else:
		print(func + ' is not a valid partitioning algorithm.')
	
# Get scores of observed networks
def get_score(Gs, comms, func, n_sim):
	if len(Gs) ==  len(comms):
		functions = {'rwc':randomwalk_polarization, 'bcc':bcc_score, 'ei':ei_ind}
		if func in functions:
			pol_scores = []
			for i in range(len(Gs)):
				print(i+1)
				ps = functions[func](Gs[i], n_sim, left_partition_users = comms[i][0], right_partition_users = comms[i][1])
				pol_scores.append(ps)
			return pol_scores
		else:
			print(func + ' is not a valid polarization score.')
	else:
		print('Length of Gs and comms are not equal.')

# Produce networks using the configuration model
def to_cmnets(G, n_sims):
	dd = [deg for name, deg in G.degree()]
	cm = []
	for _ in range(n_sims):
		G = nx.configuration_model(dd)
		G = nx.Graph(G)
		G.remove_edges_from(nx.selfloop_edges(G))
		G = get_giant_component(G)[0]
		cm.append(G)
	return cm

# Running the analysis
Gs = inpickle('top100_hashtag_graphs.pickle')
Gs = inpickle('garimella_20_graphs.pickle')

# Get giant component
GCs = [get_giant_component(G)[0] for G in Gs]

# Get communities
comms = comm_detect(GCs, func = 'metis')

# Get polarization score
pol_scores = get_score(GCs, comms, func = 'rwc', n_sim = 1)


