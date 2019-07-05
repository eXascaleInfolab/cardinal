#Estimators
from collections import Counter
import numpy as np
import copy

# Prep tools
unravel = lambda l: [item for sublist in l for item in sublist]

class Estimate:
    def __init__(self, samples):
        self.K = len(samples) # number of samples
        self.samples = unravel(samples) # oberservations from all samples (fas)
        self.S = len(self.samples) # number of observations fas
        self.observed = dict(Counter(self.samples)) # frequency of observations fas
        self.distinct = len(self.observed) # distinct number of observations        
        self.ff = dict(Counter(self.observed.values())) # frequency of the frequency of observations fas

    #Chao based 
    def chao_estimates(self):
        if 1 in self.ff and self.ff[1] == self.S:
            return [self.distinct,self.distinct]
        
        turing_est = 1        

        if 1 in self.ff:
            turing_est = 1 - ( float(self.ff[1]) / float(self.S) )    
            #clamp while sufficient sample number is reached
            turing_est = min(1, turing_est + max(self.distinct / (self.S - self.ff[1]) - 1, 0))

        N1 = self.distinct / turing_est

        tmp = 0.0
        for i in range(1, self.S + 1):
            if i in self.ff:
                tmp += i * (i-1) * self.ff[i]
                
        cv_est = max(0.0, ((N1 * tmp) / float(self.S * (self.S-1))) - 1)
        
        N2 = N1  + ( self.S * ( (1 - turing_est) / turing_est ) * cv_est )
        # N1-UNIF, Chao92
        return [N1, N2]

    
    #Singleton Outlier Detection 
    def sor_estimates(self):  
        if 1 in self.ff and self.ff[1] == self.S:
            distinct = len(set(self.samples))
            return [self.distinct]
        turing_est = 1

        ff_ = copy.deepcopy(self.ff)
        if 1 in ff_:
            del ff_[1]
        ff_np = np.array(list(ff_.values()), dtype=np.int32)
        tmp = min(self.ff[1] if 1 in self.ff else 0, np.mean(ff_np) + 3*np.std(ff_np))        
        
        if 1 in self.ff:
            turing_est = 1 - float(tmp / float(self.S))        
            
        N1 = len(self.observed) / turing_est
        
        
        tmp = 0.0
        for i in range(1, self.S + 1):
            if i in self.ff:
                tmp += i * (i-1) * self.ff[i]
                
        cv_est = max(0.0, ((N1 * tmp) / float(self.S * (self.S-1))) - 1)
        
        N2 = N1  + ( self.S * ( (1 - turing_est) / turing_est ) * cv_est )
        #SOR 
        return [N2]
    
    def jack_estimates(self, order = 1):
        J1 = len(self.observed) + \
            ( ( float ((self.K -1) / self.K) * self.ff[1]) if 1 in self.ff else 0 )
        J2 = len(self.observed) + \
            ( ((2*self.K - 3) * self.ff[1] / self.K ) if 1 in self.ff else 0 ) - \
            ( ((self.K-2)**2 * self.ff[2] / ((self.K - 1) * self.K)) if 2 in self.ff else 0 )

        #jack1, jack2
        return [max(J1, self.distinct), max(J2, self.distinct)]
