import pandas as pd
import numpy as np

class Wallet:
    '''read in the wallet structure csv file, to construct wallet id csv'''
    def __init__(self, walletstrcsv, walletcsv):
        #rget wallet structure csv name  and the wallet csv file name to export to
        self.walletstrcsv=walletstrcsv
        self.walletcsv= walletcsv

        #file exists
        try:    
            #load the data(only need the second column) to recover self.par as a numpy array
            self.par=(pd.read_csv(walletstrcsv, header=None, usecols=[1]))[1].tolist()
            print("find walletID from exist wallet structure file: %s"%walletstrcsv)
        except Exception as e:
            print(e)
    
    # get root for a specific node i
    def root(self, i):
        while i != self.par[i]:
            # path compression
            self.par[i]=self.par[self.par[i]]
            i=self.par[i]

        return i

    #get root for each element np.vectorize version, too slow..
    def getRoots(self):
        #pars=np.array(self.par)
        vroot=np.vectorize(self.root)
        roots=vroot(self.par)
        return roots

    # export the wallet array, given a file name
    def constructWalletCSV(self):
        #get roots for each parent to build wallet_id        
        #np.vectorize version, kinda slow
        #wallet_ids=self.getRoots()
        #list comprehensive version
        wallet_ids=[self.root(p) for p in self.par]
        #convert to csv
        wallet_ids_pd=pd.DataFrame(wallet_ids)
        wallet_ids_pd.to_csv(self.walletcsv,index=True,header=False)






