# Prep
from tweet_polarization import *
from sklearn import metrics
import numpy as np
import pandas as pd
import itertools
import random

# Loading settings
PARAMS = {}
with open('params.txt', encoding = 'utf-8') as params:
	for line in params:
		param, value = line.strip().split(':', 1)
		PARAMS[param] = value.split(';')
		if PARAMS[param] == ['']:
			PARAMS[param] = None

#--------------------------#
# Functions for the paper* #
#--------------------------#
# *This starts from loading in the edgelist (where each row is an undirected edge)
def to_network(filepath, gc = True):
	with open(filepath, 'rb') as in_pickle:
		rts = pickle.load(in_pickle)
	# Renaming vertices
	g1 = nx.MultiDiGraph()
	g1.add_edges_from([rt[0:2] for rt in rts])
	g.remove_edges_from(nx.selfloop_edges(g))
	if gc:
		g = get_giant_component(g)[0]
	#g = nx.convert_node_labels_to_integers(g, first_label = 0, ordering = 'default', label_attribute = 'handle')
	return g	
	
def polarization_score(g, left_partition_users, right_partition_users):
	# counting ties in blocks
	aa, bb, ab = 0, 0, 0
	for e in g.edges():
		if (e[0] in left_partition_users) and (e[1] in left_partition_users):
			aa += 1
		elif (e[0] in right_partition_users) and (e[1] in right_partition_users):
			bb += 1
		else:
			ab += 1
	# block density
	ln, rn = len(left_partition_users), len(right_partition_users)
	daa = aa/(ln*(ln - 1))
	dbb = bb/(rn*(rn - 1))
	dab = ab/(ln*rn)
	# polarization score
	ps = (daa + dbb - 2*dab)/(daa + dbb + 2*dab)
	return ps

def process_period(periods, ufactor, seed = 1):
	topics = PARAMS['TOPICS']
	results = {}
	for period in periods:
		for topic in topics:
			print('Starting: ' + topic + str(period))
			g = to_network('output/edgelists/period' + str(period) + '/' + topic + '_edgelist.pickle')
			comms = metis_partition(g, seed = seed, contig = True, ufactor = ufactor, ncuts = 50, niter = 500, pfactor = 100)
			ps = polarization_score(g, comms[0], comms[1])
			results[topic + str(period)] = [g, comms, ps]
	return results

def mutual_info(topic1, topic2, results):
	t1 = results[topic1]
	t2 = results[topic2]
	ids = sorted(set.intersection(set(t1[1][0] + t1[1][1]), set(t2[1][0] + t2[1][1])))
	l1 = []
	for i in ids:
		if i in t1[1][0]:
			l1.append(0)
		else:
			l1.append(1)
	l2 = []
	for i in ids:
		if i in t2[1][0]:
			l2.append(0)
		else:
			l2.append(1)		
	mi = metrics.normalized_mutual_info_score(l1, l2)
	return mi

def to_mi_mat(results):
	topics = list(results.keys())
	mi = []
	for pair in itertools.combinations(topics, 2):
		mi.append(mutual_info(*pair, results))
	mis = np.zeros(shape = (len(results), len(results)))
	inds = np.triu_indices_from(mis, 1)
	mis[inds] = mi
	df = pd.DataFrame(mis, columns = topics, index = topics)
	return df

def overlap_stats(topic1, topic2, results):
	t1 = results[topic1]
	t2 = results[topic2]
	ids = sorted(set.intersection(set(t1[1][0] + t1[1][1]), set(t2[1][0] + t2[1][1])))
	combo = dict.fromkeys(['one0two0', 'one1two1', 'one1two0', 'one0two1'], 0)
	for i in ids:
		if i in t1[1][0]:
			if i in t2[1][0]:
				combo['one0two0'] += 1
			else:
				combo['one0two1'] += 1
		else:
			if i in t2[1][0]:
				combo['one1two0'] += 1
			else:
				combo['one1two1'] += 1
	one0two0 = (combo['one0two0']/(combo['one0two0'] + combo['one0two1']))/(combo['one0two0'] + combo['one1two0'])
	one0two1 = (combo['one0two1']/(combo['one0two0'] + combo['one0two1']))/(combo['one0two1'] + combo['one1two1'])
	one1two0 = (combo['one1two0']/(combo['one1two0'] + combo['one1two1']))/(combo['one0two0'] + combo['one1two0'])
	one1two1 = (combo['one1two1']/(combo['one1two0'] + combo['one1two1']))/(combo['one0two1'] + combo['one1two1'])
	
	one0 = [i/sum([one0two0, one0two1]) for i in [one0two0, one0two1]]
	one1 = [i/sum([one1two0, one1two1]) for i in [one1two0, one1two1]]
	
	df = pd.DataFrame([one0, one1])
	df.index = [topic1 + 'A', topic1 + 'B']
	df.columns = [topic2 + 'A', topic2 + 'B']

	return df

def to_overlap_mat(results):
	topics = list(results.keys())
	names = [f'{a}{b}' for a in topics for b in ['A', 'B']]
	df = pd.DataFrame(np.zeros(shape = (len(names), len(names))), columns = names, index = names)
	for pair in itertools.permutations(topics, 2):
		overlap = overlap_stats(*pair, results)
		df.loc[overlap.index, overlap.columns] = overlap
	return df

def results_out():
	with open('output/topics_metis.pickle', 'wb') as out_pickle:
		pickle.dump(results, out_pickle)
	simple_results = dict()
	for k, v in results.items():
		simple_results[k] = [v[1][0:2], v[2]]
	with open('output/topics_metis_simple.pickle', 'wb') as out_pickle:
		pickle.dump(simple_results, out_pickle)

#-----------------#
# Analysis script #
#-----------------#
# 1) Polarization Results
results = process_period([1,2,3], ufactor = 400, seed = 173704)

# Checking visually
for k, v in results.items():
    print([k, v[2]])

# Exporting results
results_out()

# 2)  Alignment Results
mi_mat = to_mi_mat(results)
mi_mat.to_csv('output/climate_topic_alignment.csv', float_format='%.3f')

# 3) Overlap Results
overlap_mat = to_overlap_mat(results)
overlap_mat.to_csv('output/climate_bubble_overlap.csv', float_format='%.4f')

# 4) Robustness of results
ufs = [450, 400, 350, 300, 250, 200, 150] # different ufactors for metis
al_out = []
ps_out = []
for uf in ufs:
	rest = process_period([1,2,3], ufactor = uf, seed = 173704)
	mit = to_mi_mat(rest)
	al_out.append(mit.loc['CLIMATE1'])
	pss = []
	for k, v in rest.items():
		pss.append(v[2])
	ps_out.append(pss)

al_out = pd.DataFrame(al_out)
al_out = al_out.set_index(pd.Series(ufs))

ps_out = pd.DataFrame(ps_out)
ps_out = ps_out.set_index(pd.Series(ufs))

al_out.to_csv('output/alignment_robust.csv', float_format='%.3f')
ps_out.to_csv('output/polarization_robust.csv', float_format='%.3f')

#------------------------------#
# Additional utility functions #
#------------------------------#
# Tweet Content
# for each tweet, if original tweeter is in community, if original tweet has hashtag of x, save.
def content_extractor(tweet, set1, period, results, check_fi):
	hts_a = set1[0].split(',')
	c1 = results[hts_a[0] + str(period)][1][0]
	c2 = results[hts_a[0] + str(period)][1][1]
	check_fi = set(check_fi)
	if 'retweeted_status' in tweet:
		hts = [x.lower() for x in tweet['retweeted_status']['hashtags']]
		if len(hts) > 0:
			hts_set = set(hts)
			if len(hts_set.intersection(set(hts_a))) > 0:
				if (len(set(hts_a) & hts_set) > len(set(hts_a) & check_fi & hts_set)) or tweet['retweeted_status']['lang'] == 'fi': 
					if tweet['retweeted_status']['user']['id'] in c1:
						return tweet['retweeted_status']['text'], 0
					if tweet['retweeted_status']['user']['id'] in c2:
						return tweet['retweeted_status']['text'], 1

# Run content extractor
def run_content_extractor(set1, period, period_size, results, raw, check_fi):
	# Cycles through tweets
	files = sorted(os.listdir(raw))
	start_i = [index for index, item in enumerate(files) if item == start + '.json'][0]
	tweetsA, tweetsB = [], []
	for file in files[start_i:(start_i + period_size)]:
		file_name = file[0:10]
		with open(os.path.join(raw, file), 'r', encoding = 'utf-8') as read_file:
			data = json.load(read_file)
			for tweet in data:
				try:
					content, comm = content_extractor(tweet, set1, period, results, check_fi)
					if comm == 0:
						tweetsA.append(content)
					else:
						tweetsB.append(content)
				except TypeError:
					pass
	return [list(set(tweetsA)), list(set(tweetsB))]

def tweet_texts_out(results, write_out = False):
	tweet_texts = dict.fromkeys(results.keys())
	for key in results.keys():
		print('Starting: ' + key)
		period = key[-1]
		topic = key[:-1]
		period_size = {'1': 45, '2': 42, '3': 66}[period]
		tweet_texts[key] = run_content_extractor(PARAMS['HP_' + topic], period, period_size, results, raw = PARAMS['TWEET_FOLDER'][0], check_fi = PARAMS['HP_notfi'])
	if write_out:
		df = pd.concat([pd.Series(v_comm) for k, v in tweet_texts.items() for v_comm in v], axis=1)
		df.columns = [f'{a}{b}' for a in results.keys() for b in ['A', 'B']]
		df.to_csv('output/tweet_texts.csv')
	return tweet_texts

# Exporting all directed retweets to .txt
def process_edgelists(periods):
	topics = PARAMS['TOPICS']
	for period in periods:
		for topic in topics:
			with open('output/edgelists_weighted/period' + str(period) + '/' + topic + '_edgelist.pickle', 'rb') as inpickle:
				rts = pickle.load(inpickle)
			with open('output/edgelists_weighted/text/' + topic + '_' + 'p' + str(period) + '.txt', 'w') as outfile:
				for rt in rts:
					outfile.write(str(rt[0]) + ',' + str(rt[1]) + ',' + str(rt[2]) + '\n')

process_edgelists([1,2,3])
#