# Prep
from tweet_polarization import *

PARAMS = {}
with open('params.txt', encoding = 'utf-8') as params:
	for line in params:
		param, value = line.strip().split(':', 1)
		PARAMS[param] = value.split(';')
		if PARAMS[param] == ['']:
			PARAMS[param] = None

#
def to_network(filepath, gc = True):
	with open(filepath, 'rb') as in_pickle:
		rts = pickle.load(in_pickle)
	# Renaming vertices
	g = nx.Graph()
	g.add_edges_from(rts)
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

topics = os.listdir('output/edgelists/period2/')
# g = to_network('output/edgelists/period1/' + topics[0])
# comms = metis_partition(g, seed = 100, contig = True, ufactor = 300, ncuts = 10, niter = 200, pfactor = 100)
# polarization_score(g, comms[0], comms[1])

results = {}
for topic in topics:
	print('Starting: ' + topic[:-16])
	g = to_network('output/edgelists/period2/' + topic)
	comms = metis_partition(g, seed = 161576, contig = True, ufactor = 300, ncuts = 20, niter = 500, pfactor = 100)
	ps = polarization_score(g, comms[0], comms[1])
	results[topic[:-16]] = [g, comms, ps]

for k, v in results.items():
    print([k, v[2]])
	
with open('output/results/period2_topics_metis.pickle', 'wb') as out_pickle:
	pickle.dump(results, out_pickle)

simple_results = []
for k, v in results.items():
    simple_results.append([k, v[1], v[2]])

with open('output/results/period2_topics_metis_simple.pickle', 'wb') as out_pickle:
	pickle.dump(simple_results, out_pickle)
#

#testing
topic = 'SCIENCE' + '_edgelist.pickle'
g = to_network('output/edgelists/period1/' + topic)
comms = metis_partition(g)
ps = polarization_score(g, comms[0], comms[1])

ps_test = []
for topic in topics:
	print('Starting: ' + topic[:-16])
	g = to_network('output/edgelists/period1/' + topic, gc = False)
	gc = get_giant_component(g)[0]
	comms = metis_partition(gc)
	pss = [polarization_score(gc, comms[0], comms[1])]
	cm = to_cmnets(g, 20)
	for gt in cm:
		comms = metis_partition(gt)
		ps = polarization_score(gt, comms[0], comms[1])
		pss.append(ps)
	ps_test.append(pss)

	
# configuration model
def to_cmnets(g, n_sims):
	dd = [deg for name, deg in g.degree()]
	cm = []
	for _ in range(n_sims):
		g = nx.configuration_model(dd)
		g = nx.Graph(g)
		g.remove_edges_from(nx.selfloop_edges(g))
		g = get_giant_component(g)[0]
		cm.append(g)
	return cm
#
cm = to_cmnets(g, 10)
pss = []
for g in cm:
	comms = metis_partition(g)[0:2]
	ps = polarization_score(g, comms[0], comms[1])
	pss.append(ps)


#
['SDP', 0.889]
['IMMIGRATION', 0.946]
['SOCIALSECURITY', 0.709]
['NATIONAL', 0.883]
['SPEECH', 0.97]
['SCIENCE', 0.719]
['FAMILY', 0.794]
['GREEN', 0.928]
['EDUCATION', 0.765]
['CENTRE', 0.878]
['FINNS', 0.967]
['PARTIES', 0.86]
['LEFT', 0.932]
['ECONOMICPOLICY', 0.794]
['CLIMATE', 0.75]

#
pss = []
for i in range(50):
	g = nx.erdos_renyi_graph(2000, 0.001, directed = False)
	g = get_giant_component(g)[0]
	comms = metis_partition(g)
	ps = polarization_score(g, comms[0], comms[1])
	pss.append(ps)
#
peach = '#fcae91FF'
purple = '#7828a0FF'
v_col = []
for node in list(g.nodes):
	if node in comms[0]:
		v_col.append(peach)
	if node in comms[1]:
		v_col.append(purple)

nx.draw(g,
		#pos = g[2],
		node_size = 3,
		width = 0.2,
		node_color = v_col,
		edge_color = "#333333FF"
	   )