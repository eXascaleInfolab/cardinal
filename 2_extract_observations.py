import pickle;
from collections import defaultdict
import pandas as pd;
import argparse
import bz2
import logging
from datetime import datetime
from graph_tool.all import *

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

#parse the input
parser = argparse.ArgumentParser(description='Extract all mentions x which belong to a class. Where x ==property?==> y and y ==instanceOf==> class.')
parser.add_argument('--ingraph', '-g', default="data/wikidata-20180813-all.json.bz2.universe.noattr.gt.bz2", help='the graph to load')
parser.add_argument('--infile', '-i', default="data/edits_wikidatawiki-20181001-pages.csv", help='the extracted edits from wikidata dump')
parser.add_argument('--outfile', '-o', default="data/observations_wikidatawiki-20181001-pages.pickle", help='the outfile')

args = parser.parse_args()

# parse csv
logging.info("parse csv: " + args.infile)
data = pd.read_csv(args.infile, sep="\t", names=['page','comment','user','time'])
data['from'] = data['page'].str.extract(r'Q(\d*)')
data['from'] = pd.to_numeric(data['from'], errors='coerce')
data['p'] = data['comment'].str.extract(r'Property:P(\d+)')
data['p'] = pd.to_numeric(data['p'], errors='coerce')
data['to'] = data['comment'].str.extract(r'Q(\d*)')
data['to'] = pd.to_numeric(data['to'], errors='coerce')
data = data.dropna()

# load graph
logging.info("load graph: " + args.ingraph)
universeFile = args.ingraph
universe = load_graph(universeFile)

logging.info("prepare the graph")
# unpack variables for O(1) access
q2v = {}
p2v = {}
for v in universe.vertices():
    if universe.vp.item[v]: #items => Q
        q2v[universe.vp.q[v]] = v
    else: #property => P
        p2v[universe.vp.q[v]] = v

# filter the graph 
instance_filter = universe.new_edge_property("bool") #create property for filtering
map_property_values(universe.ep.p, instance_filter, lambda x: int(x) == 31) #only allow "instance of" edges
instanceGraph = GraphView(universe, efilt=instance_filter) #create instanceGraph view

# extract
observations = defaultdict(list)

logging.info("extract...")

for i in data.index:
    to = data.get_value(i, 'to')
    from_ = data.get_value(i, 'from')

    if(not i%100000):
        logging.info('@'+str(i)+' / '+str(len(observations))+' observations')

    #add to
    if to in q2v:
        v = q2v[to]
        classes = instanceGraph.get_out_neighbours(v)
        for c in classes:
            #data (P, Q, timestamp, user) (31, 8138.0, 20130702231612, '**Romina**', True => Q == to)
            observations[universe.vp.q[c]].append((int(data.get_value(i, 'p')), int(to), datetime.strptime(str(data.get_value(i, 'time')), '%Y%m%d%H%M%S'), data.get_value(i, 'user'), True))

    #add from
    if from_ in q2v:
        v = q2v[from_]
        classes = instanceGraph.get_out_neighbours(v)
        for c in classes:
            observations[universe.vp.q[c]].append((int(data.get_value(i, 'p')), int(from_), datetime.strptime(str(data.get_value(i, 'time')), '%Y%m%d%H%M%S'), data.get_value(i, 'user'), False))

pickle.dump( observations, open( args.outfile, "wb" ) )
logging.info("saved observations:" + args.outfile)
