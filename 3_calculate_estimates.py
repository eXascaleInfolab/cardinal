import pickle
import os
import logging
import argparse
from datetime import datetime
from itertools import groupby
from collections import Counter
from estimators import Estimate, unravel

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

#parse the input
parser = argparse.ArgumentParser(description='Run the estimators on observations.')
parser.add_argument('--infile', '-g', default="data/mentions.pickle", help='the observations to load')
parser.add_argument('--outfile', '-eo', default="data/estimations.pickle", help='the estimations outfile')

args = parser.parse_args()

def dateConverter(x):
    if type(x) is datetime:
        return x
    else:
        return datetime.strptime(str(x), '%Y%m%d%H%M%S')

    
minDate = dateConverter(20130101000000)
def estimateMonth(data, window_length=30):
    #data (P, Q, timestamp, user) (31, 8138.0, 20130702231612, '**Romina**', True => Q == to)
    obs = [(int(x[1]), (dateConverter(x[2]) - minDate).days // window_length ) for x in data]
    #obs (Q, sampleWindow) (8138, 6) sampleWindow based on window_length
    obs = [list(set([i[0] for i in x[1]])) for x in groupby(obs, lambda x : x[1])]
    #obs [[samples of window 1], [samples of window 2], ...] [[8138], [8577, 8456, 8088, 18
    chunks = [obs[:i+1] for i in range(0, len(obs))]
    #chunks [[[sample1], [[sample1], [sample2]], [[sample1],[sample2],[sample3]]]]

    for idx, chunk in enumerate(chunks):
        est = Estimate(chunk)
        ff = Counter(Counter(unravel(chunk)).values())  
        yield (idx, *est.chao_estimates(), *est.chao_estimatesNew(), *est.jack_estimates(), len(set(unravel(chunk))), ff[1])

logging.info( "load observations: " + args.infile )
observations = pickle.load( open( args.infile , "rb" ) )

logging.info( "calculating estimates ..." )
estimates = {} 
for x in observations:
    n_observations = len(observations[x])
    if n_observations >= 5000: 
        logging.info( "Q" + str(x) )
        estimates[x] = list(estimateMonth(observations[x], 30))

pickle.dump( estimates, open( args.outfile, "wb" ) )
logging.info( "saved estimates: " + args.outfile )
