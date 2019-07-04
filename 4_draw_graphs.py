import matplotlib;
matplotlib.use('pdf')
import matplotlib.pyplot as plt;
from graph_tool.all import *
import pickle
import os
import logging
import argparse
from datetime import datetime
from itertools import groupby
from collections import Counter

import pandas as pd;
import seaborn as sns;
import numpy as np
from mpl_toolkits.axes_grid.inset_locator import inset_axes


from estimators import Estimate, unravel
from metrics import conv

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

#parse the input
parser = argparse.ArgumentParser(description='Run the estimators on observations.')
parser.add_argument('--infile', '-f', default="data/estimates_wikidatawiki-20181001-pages.pickle", help='the estimations to load')
parser.add_argument('--outpath', '-o', default="docs/", help='the outpath of the graphics')
parser.add_argument('--ingraph', '-g', default="data/wikidata-20180813-all.json.bz2.universe.noattr.gt.bz2", help='the graph to load (only necessary for nice labels)')
parser.add_argument('--results', '-r', default="data/results_wikidatawiki-20181001-pages.pickle", help='all results')

args = parser.parse_args()

def plot(df, title, ax, idx):
    lines = ['N1‒UNIF','Chao92','Jack1','SOR','Distinct']

    ax.set_title(title + '\n')    

    #plot estimators
    resrow = {}
    metrics = [] 

    for idx, column in enumerate(lines):
        sns.lineplot(x=df.columns[0], y=column, data=df, label=column, ax=ax, markers=idx)

        #add convergence
        if column != 'Distinct':
            metric = column + ' ρ'        
            metrics.append(metric)
            resrow[metric] = conv(list(df[column]), list(df['Distinct']))

    ax.set(xlabel='Sample Periods', ylabel='Cardinality')

    #add distinct
    metric = 'Distinct'
    metrics.append(metric)
    resrow[metric] = df['Distinct'].max().astype(np.float64)

    #prepare results
    df = pd.DataFrame({title: resrow}).transpose()
    df = df.reindex(columns=metrics)

    return df

def plotInd(df, title, ax, idx):
    # indicators
    df['$f_1$'] = df['$f_1$']/df['Distinct'].max().astype(np.float64)
    df['Distinct'] = df['Distinct']/df['Distinct'].max().astype(np.float64)


    for idx, column in enumerate(['$f_1$','Distinct']):
        sns.lineplot(x=df.columns[0], y=column, data=df, label=column, ax=ax)

    ax.set(xlabel='Sample Periods', ylabel='Indicators')

universe = None
if args.ingraph != '':
    # load graph, only need for the titles here
    logging.info("load graph: " + args.ingraph)
    universe = load_graph(args.ingraph)
    q2v = {}
    p2v = {}
    for v in universe.vertices():
        if universe.vp.item[v]: #items => Q
            q2v[universe.vp.q[v]] = v
        else: #property => P
            p2v[universe.vp.q[v]] = v

logging.info( "loading estimates: " + args.infile )
estimates = pickle.load( open( args.infile , "rb" ) )
html = '''
<html>
    <head>
        <title>Non-Parametric Class Completeness Estimators for Collaborative Knowledge Graphs - The Case of Wikidata</title>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container">
            <h1>Non-Parametric Class Completeness Estimators for Collaborative Knowledge Graphs - The Case of Wikidata</h1>
            <h2>Results</h2>'''

for estimate in sorted(estimates):
    try:
        name = ''
        if universe:
            name = universe.vp.label[q2v[estimate]]

        dfEstimate = pd.DataFrame(estimates[estimate], columns=['month','N1‒UNIF','Chao92','SOR','Jack1','Jack2','Distinct','$f_1$'])
        f, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=[8, 4])

        result = plot(dfEstimate, name + " (Q" + str(estimate) + ")", ax1, 0)
        plotInd(dfEstimate, name + " (Q" + str(estimate) + ")", ax2, 0)
        plt.savefig(args.outpath + 'figures/' +str(estimate) + '.pdf')
        plt.savefig(args.outpath + 'figures/' +str(estimate) + '.png')
        logging.info( "saved " + str(estimate) + '.pdf' )
        plt.close()

        html = html + '''
            <h2>Q'+str(estimate)+': '+name+'</h2>
'''
        html = html + result.to_html()
        html = html + '''
            <img src="figures/'+str(estimate)+'.png">
'''

        try:
            results = results.append(result)
        except NameError:
            results = result

    except KeyboardInterrupt:
        break

pickle.dump( results, open( args.results, "wb" ) )

html = html + '''
        </div>
    </body>
</html>'''

with open(args.outpath + "estimates.html", "w") as file:
    file.write(html)
