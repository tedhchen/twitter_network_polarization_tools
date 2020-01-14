#---------------------------#
# Loading required packages #
#---------------------------#
import os, json, ast, pickle
import networkx as nx
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import math
import random
import statistics
import nxmetis
from scipy import stats

#--------------------#
# Defining functions #
#--------------------#

# (1) hashtag_overlap() and run_parser() are used to parse the raw data into text files of retweets.

# Subsetting retweet data:
# Takes one or two sets of topics (as lists of (topics = lists of textstrings)) and subsets sample of tweets;
# If only one set of topics, subset by of the topics;
# If two sets of topics, subset by the intersection of topics based on the cartesian product of the two sets;
# Writes as text files of tuples (timestamp, sender, receiver, type of overlap) to the outfolder;
# Type of overlap: 1 or 2 means tweet is on topic 1 or 2, respectively; 3 means tweet contains both topics; (if only one topic, then automatically 3).
# Arguments:
## tweet: tweet as json object
## set1 and set2: lists of lists of text strings to subset tweets by (if set2 == None: only subset by set1)
## all_text: if True, search all tweet for text string; if False, use only hashtags
## outfolder: where to save daily folders
### each daily folder will contain files with name format "has_topic.txt" if only one set of topics and name format "overlap_topic1_topic2.txt"
def hashtag_overlap(tweet, set1, set2, all_text, outfolder):
	if 'retweeted_status' in tweet:
		if all_text == True:
			text = tweet['retweeted_status']['text'].replace('\r', ' ').replace('\n', ' ').lower()
			for a in set1:
				if set2 == None:
					hts_a = a.split(',')
					if sum([x in text for x in hts_a]) > 0:
						outpath = outfolder + '/has_' + hts_a[0] + '.txt'
						with open(outpath.encode("utf-8"), 'a', encoding = 'utf-8') as outfile:
							outfile.write(str((tweet['timestamp'], tweet['user']['id'], tweet['retweeted_status']['user']['id'], 3)) + '\n')
				else:
					for b in set2:
						hts_a = a.split(',')
						hts_b = b.split(',')
						a_in = sum([x in text for x in hts_a]) > 0
						b_in = sum([x in text for x in hts_b]) > 0
						if a_in + b_in == 2:
							rt_stat = 3
						elif a_in == 1:
							rt_stat = 1
						elif b_in == 1:
							rt_stat = 2
						else:
							rt_stat = 0

						if rt_stat > 0:
							outpath = outfolder + '/overlap_' + hts_a[0] + '_' + hts_b[0] + '.txt'
							with open(outpath.encode("utf-8"), 'a', encoding = 'utf-8') as outfile:
								outfile.write(str((tweet['timestamp'], tweet['user']['id'], tweet['retweeted_status']['user']['id'], rt_stat)) + '\n')
		else:
			hts = [x.lower() for x in tweet['retweeted_status']['hashtags']]
			if len(hts) > 0:
				hts_set = set(hts)
				for a in set1:
					if set2 == None:
						hts_a = a.split(',')
						if len(hts_set.intersection(set(hts_a))) > 0:
							outpath = outfolder + '/has_' + hts_a[0] + '.txt'
							with open(outpath.encode("utf-8"), 'a', encoding = 'utf-8') as outfile:
								outfile.write(str((tweet['timestamp'], tweet['user']['id'], tweet['retweeted_status']['user']['id'], 3)) + '\n')
					else:
						for b in set2:
							hts_a = a.split(',')
							hts_b = b.split(',')
							if (len(hts_set.intersection(set(hts_a))) > 0) and (len(hts_set.intersection(set(hts_b))) > 0):
								rt_stat = 3
							elif len(hts_set.intersection(set(hts_a))) > 0:
								rt_stat = 1
							elif len(hts_set.intersection(set(hts_b))) > 0:
								rt_stat = 2
							else:
								rt_stat = 0

							if rt_stat > 0:
								outpath = outfolder + '/overlap_' + hts_a[0] + '_' + hts_b[0] + '.txt'
								with open(outpath.encode("utf-8"), 'a', encoding = 'utf-8') as outfile:
									outfile.write(str((tweet['timestamp'], tweet['user']['id'], tweet['retweeted_status']['user']['id'], rt_stat)) + '\n')

# Wrapper for the hashtag_overlap() function:
# Arguments:
## raw: where the raw tweet jsons are stored
def run_parser(set1, set2, all_text, raw, outfolder):
	try:
		os.mkdir(outfolder)
	except FileExistsError:
		pass
	# Cycles through tweets
	files = sorted(os.listdir(raw))
	for file in files:
		file_name = file[0:10]
		try:
			os.mkdir(outfolder + '/' + file_name)
		except FileExistsError:
			pass
		with open(os.path.join(raw, file), 'r', encoding = 'utf-8') as read_file:
			data = json.load(read_file)
			for tweet in data:
				hashtag_overlap(tweet, set1, set2, all_text, outfolder + '/' + file_name)


# (2) sort_rts() and to_links() take retweet tuples and create undirected and unweighted edgelists.

# Internal function used by to_links(). 
# Takes a .txt file of retweet tuples and returns list of retweets:
# If only one set of topics, returns retweets based on that set of topics;
# If two sets of topics, returns a) a list of retweets that are overlap type 1 or 2, and b) a list of retweets that are overlap type 3.
def sort_rts(infile):
	rts_either = []
	rts_both = []
	try:
		with open(infile.encode('utf-8'), 'r', encoding = 'utf-8') as f:
			for line in f:
				rt = ast.literal_eval(line)
				if rt[3] == 3:
					rts_both.append(tuple(sorted(rt[1:3])))
				if rt[3] == 1 or rt[3] == 2:
					rts_either.append((sorted(rt[1:3])[0], sorted(rt[1:3])[1], rt[3]))
		rts_both = list(set(rts_both))
		rts_either = set(rts_either)
		rts_freq_tab = Counter([x[0:2] for x in rts_either])
		rts_either = [key for (key, value) in rts_freq_tab.items() if value == 2]
		rts_either.extend(rts_both)
		rts_either = list(set(rts_either))
	except FileNotFoundError:
		pass
	return [rts_either, rts_both]

# Takes one or two sets of topics and returns retweet edgelists for specified period length and interval;
# The raw tweets for the topics must be parsed first using run_parser();
# Write nested edgelists as pickle files to the outfolder. 
# Arguments:
## set1 and set2: lists of lists of text strings to subset tweets by (if set2 == None: only subset by set1); (same as in run_parser())
## infolder: where the daily parsed retweet tuples are stored
## outfolder: where to save the edgelists
## period_size: number of days to include in each window
## period_interval: days to move window by
def to_links(set1, set2, infolder, outfolder, period_size, period_interval):
	try:
		os.mkdir(outfolder)
	except FileExistsError:
		pass
	period_size = int(period_size)
	period_interval = int(period_interval)
	for a in set1:
		if set2 == None:
			period_rts = []
			hts_a = a.split(',')
			files = sorted(os.listdir(infolder))
			for i in range(0, (len(files) - period_size + 1), period_interval):
				rts_strict = []
				rts_lax = []
				infiles = [infolder + '/' + files[j] + '/has_' + hts_a[0] + '.txt' for j in range(i, i + period_size)]
				for infile in infiles:
					rts = sort_rts(infile)
					rts_lax.extend(rts[0])
					rts_strict.extend(rts[1])
				rts_strict = list(set(rts_strict))
				rts_lax = list(set(rts_lax))
				period_rts.append([rts_lax, rts_strict])
			outpath = (outfolder + '/' + hts_a[0] + '_' + str(period_size) + '-' + str(period_interval) + '_edgelist.pickle')
			with open(outpath.encode("utf-8"), 'wb') as out_pickle:
				pickle.dump(period_rts, out_pickle)
		else:
			for b in set2:
				period_rts = []
				hts_a = a.split(',')
				hts_b = b.split(',')
				files = sorted(os.listdir(infolder))
				for i in range(0, (len(files) - period_size + 1), period_interval):
					rts_strict = []
					rts_lax = []
					infiles = [infolder + '/' + files[j] + '/overlap_' + hts_a[0] + '_' + hts_b[0] + '.txt' for j in range(i, i + period_size)]
					for infile in infiles:
						rts = sort_rts(infile)
						rts_lax.extend(rts[0])
						rts_strict.extend(rts[1])
					rts_strict = list(set(rts_strict))
					rts_lax = list(set(rts_lax))
					period_rts.append([rts_lax, rts_strict])
				outpath = (outfolder + '/' + hts_a[0] + '_' + hts_b[0] + '_' + str(period_size) + '-' + str(period_interval) + '_edgelist.pickle')
				with open(outpath.encode("utf-8"), 'wb') as out_pickle:
					pickle.dump(period_rts, out_pickle)

# (3) Some utility functions
# Get Giant Component and its ratio to unsubsetted graph. Input (G) is a networkx graph object.
def get_giant_component(G):
	cc = nx.connected_components(G)
	curr_max = 0
	for sg in cc:
		if len(sg) > curr_max:
			gc = sg
			curr_max = len(sg)
	GC = G.subgraph(gc)
	giant_component_ratio = GC.number_of_nodes()/G.number_of_nodes()
	return GC, giant_component_ratio

# (4) Community detection algorithms. All these take networkx graph objects G.
# Add additional community detection algorithms:
# Input is always networkx graph object G, so add package converter in the beginning of the function if needed;
# Output should be nested list where index: 0) community 1 ids, 1) community 2 ids, 2) additional information if desired but not required
# Specifically: [[Ids for comm1], [Ids for comm2], auxiliary information]

# Metis
def metis_partition(G):
	
	# For further details on metis-parameters, please refer to the manual
	settings = nxmetis.MetisOptions(ncuts=4, niter=200, ufactor=280)
	par = nxmetis.partition(G, 2, options=settings)
	the_edge_cut = par[0]
	community1 = par[1][0]
	community2 = par[1][1]
	comm = [community1, community2, the_edge_cut]

	return(comm)


# (5) perform_randomwalk() and randomwalk_polarization() are used to estimate the random walk controversy for networks built from the pickle edgelists above.

# Performs a random walk terminating when an influential node (supplied) is reached;
# Returns the side that the walk ended on.
# Arguments:
## G: networkx graph object
## starting_node: the node to start the walk from
## li and ri: lists of influences from the left and right partitions, respectively
def perform_randomwalk(G, starting_node, li, ri):
	found = 0
	end_side = 0
	which_random_starting_node = starting_node
   
	while (found != 1):
		neighbors = list(G.neighbors(which_random_starting_node))
		next_node = random.choice(neighbors)
		if (next_node in li):
			end_side = "left"
			found = 1  
		elif (next_node in ri):
			end_side = "right"
			found = 1
		else:
			which_random_starting_node = next_node       
	return end_side

# Takes random walk controversy algorithm's specifications and estimates the controversy score for the supplied graph;
# Returns the random walk controvesy score over a specified number (n_sim) of draws;
# Arguments:
## G: networkx graph object
## n_checks: number of nodes in the random sample of nodes
## n_influential: number of influential nodes from each side
## n_sim: number of times to let the n_checks nodes walk
## left_ and right_partition_users: lists of nodes belonging to each respective community
def randomwalk_polarization(G, n_checks, n_influential, n_sim, left_partition_users, right_partition_users):
	# Number of nodes in each partition
	n_left = len(left_partition_users)
	n_right = len(right_partition_users)
	# Number of influential nodes as function of each partition
	n_influential_left = math.ceil(len(left_partition_users) * n_influential)
	n_influential_right = math.ceil(len(right_partition_users) * n_influential)
	# Going through all nodes to get degree and weights to balance sampling to 1:1
	dict_degree = {}
	ws = []
	for node in G.nodes():
		dict_degree[node] = G.degree(node)
		if node in left_partition_users:
			ws.append(n_right)
		else:
			ws.append(n_left)
	# Finding all influential nodes
	sorted_dict_degree = sorted(dict_degree.items(), key = lambda kv: kv[1], reverse = True)
	left_influencers, right_influencers = [], []
	count_left, count_right = 0, 0
	for node in sorted_dict_degree:
		if (node[0] in left_partition_users):
			if (count_left < n_influential_left):
				left_influencers.append(node[0])
				count_left += 1
		else:
			if (count_right < n_influential_right):
				right_influencers.append(node[0])
				count_right += 1
		if count_left == n_influential_left and count_right == n_influential_right:
			break
	# Starting random walks
	rwc = []
	for _ in range(n_sim):
		samp = random.choices(list(G.nodes()), k = n_checks, weights = ws)
		
		left_left = 0
		left_right = 0
		right_right = 0
		right_left = 0

		for node in samp:
			if node in left_partition_users:
				starting_side = 'left'
			else:
				starting_side = 'right'
			end_side = perform_randomwalk(G, node, left_influencers, right_influencers)
			if (starting_side == "left") and (end_side ==  "left"):
				left_left += 1
			elif (starting_side == "left") and (end_side ==  "right"):
				left_right += 1
			elif (starting_side == "right") and (end_side ==  "right"):
				right_right += 1
			elif (starting_side == "right") and (end_side ==  "left"):
				right_left += 1
			else:
				print("Oops!")
		try:
			pll = (left_left)/(left_left+right_left)
		except ZeroDivisionError:
			pll = 1
		try:
			plr = (left_right)/(left_right+right_right)
		except ZeroDivisionError:
			plr = 1
		try:
			prl = (right_left)/(left_left+right_left)
		except ZeroDivisionError:
			prl = 1
		try:
			prr = (right_right)/(left_right+right_right)
		except ZeroDivisionError:
			prr = 1
		rwc.append(pll*prr - plr*prl)
	return(rwc)

# Documentation coming soon

def kernel_density_estimation(cut, rest):

    kernel_for_cut = stats.gaussian_kde(cut, bw_method=1e-3)
    kernel_for_rest = stats.gaussian_kde(rest, bw_method=1e-3)
    
    cut_sample = kernel_for_cut.resample(size=10000)
    rest_sample = kernel_for_rest.resample(size=10000)

    epsilon = 0.0001
    cut_sample = [val + epsilon for val in cut_sample[0]]
    rest_sample = [val + epsilon for val in rest_sample[0]]
    
    return cut_sample, rest_sample

def BCC_score(G, n_sim, left_partition_users, right_partition_users):
    
    dict_edgebetweenness = nx.edge_betweenness_centrality(G)
    print("Edge betweenness scores computed. The simulations begin.")
    BCC_scores = []

    for _ in range(n_sim):

        dict_ebs = dict_edgebetweenness.copy()
        cut_ebs, rest_ebs = [], []
        keys_to_remove = []
        
        for n1 in left_partition_users:
            for n2 in right_partition_users:
                
                if G.has_edge(n1, n2):
                    
                    if ((n1, n2) in dict_ebs):
                        cut_ebs.append(dict_ebs[(n1, n2)])
                        keys_to_remove.append((n1, n2))

                    else:
                        cut_ebs.append(dict_ebs[(n2, n1)])
                        keys_to_remove.append((n2, n1))
                                    
        for k in keys_to_remove:
            dict_ebs.pop(k)
        
        rest_ebs = list(dict_ebs.values())

        cut_dist_kde, rest_dist_kde = kernel_density_estimation(cut_ebs, rest_ebs)

        kl_divergence = stats.entropy(cut_dist_kde, rest_dist_kde)
        BCC = 1-2.71828**(-kl_divergence)
        
        BCC_scores.append(BCC)

    return BCC_scores

# (6) comm_detect() and g_prep() are high level wrappers to perform the partitioning and polarization estimation procedures

# Community Detection Wrapper
# Takes a networkx graph object G, specifications, and returns:
# a) a list of community membership by node, b) the random walk controversy score, and c) auxiliary information returned by some comm detect algorithms
# Arguments:
## G: networkx graph object
## col1 and col2: ids for the two communities; best specified as colours to facilitate easy plotting
## func_name: specify the community detection algorithm to use (see below for key)
## n_checks, n_influential, n_sim: used by randomwalk_polarization()
def comm_detect(G, col1, col2, func_name, polarization, n_checks, n_influential, n_sim):
	# functions = {'girvan_newman': gn_comm2, 'async_fluid': af_comm2, 'louvain': louvain_comm,
	# 			 'infomap': infomap_comm, 'eigenvector': eigenvector_comm, 'em': em_comm2,
	# 			 'sbm_lax': sbm_lax_comm2, 'sbm_strict': sbm_strict_comm2, 'sbm_search': sbm_search,
	# 			 'sbm_nested_lax': sbm_nested_lax_comm2, 'sbm_nested_strict': sbm_nested_strict_comm2}
	# if func_name in functions:
	# 	comm = functions[func_name](G)
	# if len(comm) == 3:
	# 	aux = comm[2]
	# else:
	# 	aux = 'NA"'
	# if len(comm[1]) == 0:
	# 	rwc = -1
	# else:

	comm = metis_partition(G)
	aux = comm[2]

	if polarization == 1:
		if len(comm[0]) == 0 or len(comm[1]) == 0:
			pol_score = 0
		else:
			pol_score = randomwalk_polarization(G, n_checks, n_influential, n_sim, left_partition_users = comm[0], right_partition_users = comm[1])
	
	elif polarization == 2:
		if len(comm[0]) == 0 or len(comm[1]) == 0:
			pol_score = 0
		else:
			pol_score = BCC_score(G, n_sim, left_partition_users = comm[0], right_partition_users = comm[1])
	
	else:
		pol_score = 0

	cols = []
	for node in list(G.nodes):
		if node in comm[0]:
			cols.append(col1)
		elif node in comm[1]:
			cols.append(col2)
		else:
			cols.append('#696969')
	return cols, pol_score, aux


# High level wrapper to process the pickle edgelists. Has specification to include/omit various subtasks.
# Returns a nested list of graphs, communities, and other information.
# The returned object: Gs[topic combination][0 (1 is name)][time period][0: graph; 1: [gcr, node, edge]; 2: layout; 3: colours, 4: rwc, 5: aux]
# Can be keyboard interrupted and keep current results
# Arguments:
## infile: name of pickle file
## strict: whether retweets only count if the original tweet had both set1 and set2 topics (probably best to use False)
## gc: whether to subset to giant component
## cd: whether to run community detection (False is useful to visualize faster)
## polarization: whether to estimate random walk controversy score
## n_checks, n_influential, n_sim: specification for the random walk score (see randomwalk_polarization())
## func_name: the community detection algorithm to use
## col1 and col2: ids (best to be plottable colors) for community membership
def g_prep(infile, strict, gc, cd, polarization, plot_layout, n_checks, n_influential, n_sim, func_name, col1, col2):
	with open(infile.encode('utf-8'), 'rb') as in_pickle:
		rt_list = pickle.load(in_pickle)
	if strict:
		rt_list = [x[1] for x in rt_list]
	else:
		rt_list = [x[0] for x in rt_list]
	
	Gs = []
	i = 0
	try:
		for period in rt_list:
			i += 1
			print('\tPeriod ' + str(i) + '...')
			G = nx.Graph()
			G.add_edges_from(period)
			if G.number_of_nodes() < 2:
				gc, cd = False, False
			if gc == True:
				G, GCR = get_giant_component(G)
			else:
				GCR = 1
			G = nx.convert_node_labels_to_integers(G, first_label = 0, ordering = 'default', label_attribute = 'handle')
			if plot_layout == True:
				node_layout = nx.spring_layout(G)
			else:
				node_layout = 0
			if cd == True:
				cols, rwc, aux = comm_detect(G, col1, col2, func_name, polarization, n_checks, n_influential, n_sim)
			else:
				cols, rwc, aux = col1, 0, 'NA'
			
			dict_attr = dict(zip(range(G.number_of_nodes()), cols))
			nx.set_node_attributes(G, dict_attr, "group")
			
			Gs.append([G, [GCR, G.number_of_nodes(), G.number_of_edges()], node_layout, cols, rwc, aux])
	except KeyboardInterrupt:
		print('Manually stopped.')
		return Gs
	return Gs

#------------#
# Not in use #
#------------#
# # Girvan Newman
# def gn_comm2(G):
# 	comm = community.girvan_newman(G)
# 	comm = tuple(sorted(c) for c in next(comm))
# 	return(comm)

# # Fluid-C
# def af_comm2(G):
# 	comm = algorithms.async_fluid(G, k = 2).communities
# 	return(comm)

# # SBM (1-2)
# def sbm_lax_comm2(G):
# 	GT = gt.Graph(directed = False)
# 	es = list(G.edges())
# 	for e in es:
# 		GT.add_edge(e[0], e[1])
# 	dc = True
# 	curr_model = gt.minimize_blockmodel_dl(GT, B_min = 1, B_max = 2, deg_corr = True)
# 	curr_desclen = curr_model.entropy()
# 	for _ in range(9):
# 		sbm = gt.minimize_blockmodel_dl(GT, B_min = 1, B_max = 2, deg_corr = True)
# 		if sbm.entropy() < curr_desclen:
# 			curr_model = sbm
# 			curr_desclen = sbm.entropy()
# 	for _ in range(10):
# 		sbm = gt.minimize_blockmodel_dl(GT, B_min = 1, B_max = 2, deg_corr = False)
# 		if sbm.entropy() < curr_desclen:
# 			dc = False
# 			curr_model = sbm
# 			curr_desclen = sbm.entropy()
# 	comm = curr_model.get_blocks()
# 	comm1, comm2 = [], []
# 	for v in GT.vertices():
# 		if comm[v] == 0:
# 			comm1.append(GT.vertex_index[v])
# 		if comm[v] == 1:
# 			comm2.append(GT.vertex_index[v])
# 	return([comm1, comm2, dc])

# # SBM (strict 2)
# def sbm_strict_comm2(G):
# 	GT = gt.Graph(directed = False)
# 	es = list(G.edges())
# 	for e in es:
# 		GT.add_edge(e[0], e[1])
# 	dc = True
# 	curr_model = gt.minimize_blockmodel_dl(GT, B_min = 2, B_max = 2, deg_corr = True)
# 	curr_desclen = curr_model.entropy()
# 	for _ in range(9):
# 		sbm = gt.minimize_blockmodel_dl(GT, B_min = 2, B_max = 2, deg_corr = True)
# 		if sbm.entropy() < curr_desclen:
# 			curr_model = sbm
# 			curr_desclen = sbm.entropy()
# 	for _ in range(10):
# 		sbm = gt.minimize_blockmodel_dl(GT, B_min = 2, B_max = 2, deg_corr = False)
# 		if sbm.entropy() < curr_desclen:
# 			dc = False
# 			curr_model = sbm
# 			curr_desclen = sbm.entropy()
# 	comm = curr_model.get_blocks()
# 	comm1, comm2 = [], []
# 	for v in GT.vertices():
# 		if comm[v] == 0:
# 			comm1.append(GT.vertex_index[v])
# 		if comm[v] == 1:
# 			comm2.append(GT.vertex_index[v])
# 	return([comm1, comm2, dc])

# # SBM-nested (1-2)
# def sbm_nested_lax_comm2(G):
# 	GT = gt.Graph(directed = False)
# 	es = list(G.edges())
# 	for e in es:
# 		GT.add_edge(e[0], e[1])
# 	dc = True
# 	curr_model = gt.minimize_nested_blockmodel_dl(GT, B_min = 1, B_max = 2, deg_corr = True)
# 	curr_desclen = curr_model.entropy()
# 	for _ in range(9):
# 		sbm = gt.minimize_nested_blockmodel_dl(GT, B_min = 1, B_max = 2, deg_corr = True)
# 		if sbm.entropy() < curr_desclen:
# 			curr_model = sbm
# 			curr_desclen = sbm.entropy()
# 	for _ in range(10):
# 		sbm = gt.minimize_nested_blockmodel_dl(GT, B_min = 1, B_max = 2, deg_corr = False)
# 		if sbm.entropy() < curr_desclen:
# 			dc = False
# 			curr_model = sbm
# 			curr_desclen = sbm.entropy()

# 	comm = curr_model.get_levels()[0].get_blocks()
# 	comm1, comm2 = [], []
# 	for v in GT.vertices():
# 		if comm[v] == 0:
# 			comm1.append(GT.vertex_index[v])
# 		if comm[v] == 1:
# 			comm2.append(GT.vertex_index[v])
# 	return([comm1, comm2, dc])

# # SBM-nested (strict 2)
# def sbm_nested_strict_comm2(G):
# 	GT = gt.Graph(directed = False)
# 	es = list(G.edges())
# 	for e in es:
# 		GT.add_edge(e[0], e[1])
# 	dc = True
# 	curr_model = gt.minimize_nested_blockmodel_dl(GT, B_min = 2, B_max = 2, deg_corr = True)
# 	curr_desclen = curr_model.entropy()
# 	for _ in range(9):
# 		sbm = gt.minimize_nested_blockmodel_dl(GT, B_min = 2, B_max = 2, deg_corr = True)
# 		if sbm.entropy() < curr_desclen:
# 			curr_model = sbm
# 			curr_desclen = sbm.entropy()
# 	for _ in range(10):
# 		sbm = gt.minimize_nested_blockmodel_dl(GT, B_min = 2, B_max = 2, deg_corr = False)
# 		if sbm.entropy() < curr_desclen:
# 			dc = False
# 			curr_model = sbm
# 			curr_desclen = sbm.entropy()

# 	comm = curr_model.get_levels()[0].get_blocks()
# 	comm1, comm2 = [], []
# 	for v in GT.vertices():
# 		if comm[v] == 0:
# 			comm1.append(GT.vertex_index[v])
# 		if comm[v] == 1:
# 			comm2.append(GT.vertex_index[v])
# 	return([comm1, comm2, dc])

# # SBM search
# def sbm_search(G):
# 	GT = simple_nx2gt(G)
# 	nested = False
	
# 	# Find SBM with lowest description length: curr_m
# 	curr_m = gt.minimize_blockmodel_dl(GT, B_min = 1, B_max = 2, deg_corr = True)
# 	curr_dl = curr_m.entropy()
# 	for _ in range(4):
# 		m = gt.minimize_blockmodel_dl(GT, B_min = 1, B_max = 2, deg_corr = True)
# 		if m.entropy() < curr_dl:
# 			curr_m = m
# 			curr_dl = m.entropy()
			
# 	# Find nested SBM that:
# 	# 1) splits into two blocks
# 	# 2) aggregated blocks performs better than curr_m
# 	# 3) best of ten fitted models
# 	for _ in range(5):
# 		m = gt.minimize_nested_blockmodel_dl(GT, B_min = 1, B_max = 4, deg_corr = True)
# 		m_levels = m.get_levels()
# 		for i in range(len(m_levels)):
# 			if m_levels[i].get_B() == 2:
# 				if m.entropy() < curr_dl:
# 					m = m.project_level(i)
# 					curr_m = m
# 					curr_dl = m.entropy()
# 					nested = True
# 				break
	
# 	# Getting communities
# 	comm = curr_m.get_blocks()
# 	comm1, comm2 = [], []
# 	for v in GT.vertices():
# 		if comm[v] == 0:
# 			comm1.append(GT.vertex_index[v])
# 		if comm[v] == 1:
# 			comm2.append(GT.vertex_index[v])
# 	return([comm1, comm2, nested])

# # Infomap
# def infomap_comm(G):
# 	comm = algorithms.infomap(G).communities
# 	return(comm)

# # Eigenvector
# def eigenvector_comm(G):
# 	comm = algorithms.eigenvector(G).communities
# 	return(comm)

# # Louvian
# def louvain_comm(G):
# 	comm = algorithms.louvain(G).communities
# 	return(comm)

# # EM
# def em_comm2(G):
# 	comm = algorithms.em(G, k = 2).communities
# 	return(comm)

# Takes networkx graph (G) and converts it to graphtool graph (GT). Only considers undirected edges without further information.
# def simple_nx2gt(G):
# 	GT = gt.Graph(directed = False)
# 	es = list(G.edges())
# 	for e in es:
# 		GT.add_edge(e[0], e[1])
# 	return GT

# Take community information and add it as a node attribute to networkx graph object.
# def attaching_communities(Gs_infos):
# 
# 	for i in range(len(Gs_infos)):
# 		for j in range(len(Gs_infos[i][0])):
# 			dict_attr = dict(zip(range(Gs_infos[i][0][0][1][2]), Gs_infos[i][0][0][3]))
# 			#G = Gs_infos[i][0][0][0]
# 			nx.set_node_attributes(Gs_infos[i][0][0][0], dict_attr, "group")
# 
# 	return(Gs_infos)
