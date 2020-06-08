# Preparation
from tweet_polarization import *

# Importing parameters
# Make sure to set the parameters in params.txt (i.e. search terms, file paths, etc.)
PARAMS = {}
with open('params.txt', encoding = 'utf-8') as params:
	for line in params:
		param, value = line.strip().split(':', 1)
		PARAMS[param] = value.split(';')
		if PARAMS[param] == ['']:
			PARAMS[param] = None

# Running script
# 1) Parsing raw data
# print('Start parsing raw data.')
# run_parser(set1 = PARAMS['SET1'], set2 = PARAMS['SET2'], all_text = True, raw = PARAMS['TWEET_FOLDER'][0], outfolder = PARAMS['OUTPUT'][0])
for topic in PARAMS['TOPICS']:
	run_simple_parser(set1 = PARAMS['HP_' + topic], check_fi = PARAMS['HP_notfi'], raw = PARAMS['TWEET_FOLDER'][0], outfolder = PARAMS['OUTPUT'][0])

# 2) Create edgelists
# print('Start creating edgelists.')
# to_links(set1 = PARAMS['SET1'], set2 = PARAMS['SET2'], infolder = PARAMS['OUTPUT'][0], outfolder = PARAMS['OUTPUT'][1], period_size = PARAMS['TIME'][0], period_interval = PARAMS['TIME'][1])
period1 = to_simple_network(PARAMS['TOPICS'], start = '2019-03-01', period_size = 45, infolder = PARAMS['OUTPUT'][0])
period2 = to_simple_network(PARAMS['TOPICS'], start = '2019-04-15', period_size = 42, infolder = PARAMS['OUTPUT'][0])
period3 = to_simple_network(PARAMS['TOPICS'], start = '2019-05-27', period_size = 66, infolder = PARAMS['OUTPUT'][0])

els = [period1, period2, period3]

for period in range(0,3):
	for topic in range(len(PARAMS['TOPICS'])):
		with open('output/edgelists/period' + str(period + 1) + '/' + PARAMS['TOPICS'][topic] + '_edgelist.pickle', 'wb') as out_pickle:
			pickle.dump(els[period][topic], out_pickle)

# 3) Working with edgelist data
print('Start graph partitioning.')
Gs = []
for infile in sorted(os.listdir(bytes(PARAMS['OUTPUT'][1], encoding = 'utf-8'))):
	infile = infile.decode('utf-8')
	if True: # Only process the edgelists with the criteria here specified here
		filepath = (PARAMS['OUTPUT'][1] + '/' + infile)
		# Specify tasks and specifications here:
		Gs.append([g_prep(filepath, strict = False, func_name = 'none',
						  gc = True, cd = True, polarization = True, plot_layout = False,
						  n_checks = 1000, n_influential = 0.02, n_sim = 1000,
						  col1 = "#7828a0FF", col2 = "#fcae91FF"),
				   infile[:len(infile)-16]])
		

# This is the structure of the nested list Gs:
# Gs[topic combination][0][time period][0: graph object; 1: [giant component ratio, n_node, n_edge]; 2: fr-layout; 3: communities; 4: random-walk score; 5: aux info (safe to ignore)]

# 4) Saving Gs as pickle output
Gs_pickle_path = PARAMS['OUTPUT'][2] + '.pickle'
with open(Gs_pickle_path.encode("utf-8"), 'wb') as out_pickle:
	pickle.dump(Gs, out_pickle)

# 5) Simple plotting
plot = False
if plot == True:
	plot_filename = 'all_plots.pdf'
	with PdfPages(plot_filename) as pdf:
		for gs in Gs:
			i = 0
			for g in gs[0]:
				i += 1
				fig = plt.figure()
				nx.draw(g[0],
					pos = g[2],
					node_size = 3,
					width = 0.2,
					node_color = g[3],
					edge_color = "#333333FF"
				       )
				if isinstance(g[4], list):
					rwc = statistics.median(g[4])
				else:
					rwc = g[4]
				fig.suptitle(str(i) + ') ' + gs[1] + ' (RWC: ' + str(round(rwc, 3)) + ')' + 
					     '\n(Nodes: ' + str(g[1][1]) + ', Edges: ' + str(g[1][2]) + ' , Portion of Nodes Plotted: ' + str(round(g[1][0], 3)) + ')', fontsize = 10)
				pdf.savefig()
				plt.close()

# 6) Output a csv file with the following columns:
# a) id, b) combination, c) period id, d) text or hashtag, e) n_nodes, f) n_edges, g) giant component ratio, f) 1000 polarization scores
import csv
csv_filename = PARAMS['OUTPUT'][3] + '.csv'

# Writing header
header = ['gid', 'name', 'pid', 'type', 'n_nodes', 'n_edges', 'gcr']
header.extend(['rwc_' + str(i + 1) for i in range(1000)])
with open(csv_filename, 'a', encoding = 'utf-8', newline = '') as out_file:
	writer = csv.writer(out_file)
	writer.writerow(header)
	
# Writing rows
gid = 0
for gs in Gs:
	name = gs[1]
	pid = 0
	for g in gs[0]:
		pid += 1
		gid += 1
		outrow = [gid, name, pid, 'text', g[1][1], g[1][2], g[1][0]]
		rwc = []
		if isinstance(g[4], int):
			for _ in range(1000):
				rwc.append(g[4])
		else:
			rwc = g[4]
		outrow.extend(rwc)
	
		# Writing data
		with open(csv_filename, 'a', encoding = 'utf-8', newline = '') as out_file:
			writer = csv.writer(out_file)
			writer.writerow(outrow)

