# Preparation
from tweet_polarization import *

# Importing parameters
# Make sure to set the parameters in params.txt (i.e. search terms, file paths, etc.)
PARAMS = {}
with open('params.txt', encoding = 'utf-8') as params:
	for line in params:
		param, value = line.strip().split(':', 1)
		PARAMS[param] = value.split(';')

# Running script
# 1) Parsing raw data
run_parser(set1 = PARAMS['HASHTAGS'], set2 = None, all_text = True, raw = PARAMS['TWEET_FOLDER'][0], outfolder = PARAMS['DIRS'][0])

# 2) Create edgelists
to_links(set1 = PARAMS['HASHTAGS'], set2 = None, infolder = PARAMS['DIRS'][0], outfolder = PARAMS['DIRS'][1], period_size = 85, period_interval = 1)

# 3) Working with edgelist data
Gs = []
for infile in sorted(os.listdir(bytes(PARAMS['DIRS'][1], encoding='utf-8'))):
	infile = infile.decode('utf-8')
	if True: # Only process the edgelists with the criteria here specified here
		filepath = (PARAMS['DIRS'][1] + '/' + infile)
		print('Processing: ' + infile)
		# Specify tasks and specifications here:
		Gs.append([g_prep(filepath, strict = False, gc = True, cd = True, polarization = True, n_checks = 100, n_influential = 8, n_sim = 1000,
						  func_name = 'sbm_search', col1 = "#7828a0FF", col2 = "#fcae91FF"), infile[:len(infile)-16]])
		print('Done')
# Gs[topic combo][0 (1 is name)][time period][0: graph; 1: [gc, node, edge]; 2: layout; 3: colours]

# 3a) If need to check auxiliary information from community detection:
#aux = []
#for gs in Gs:
#	for g in gs[0]:
#		aux.append(g[5])

# 4) Simple plotting
plot_filename = ''
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

# 5) Output a csv file with the following columns:
# a) id, b) combination, c) period and interval, d) period id, e) text or hashtag, f) 1000 polarization scores, g) model
import csv
csv_filename = '.csv'

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

