import pandas as pd
import numpy as np
import os
#ref: https://algs4.cs.princeton.edu/15uf/
class WalletBuilder:
    '''take an integer to construct a wallet-parent array (a flat & efficient tree structure). this class implements Union-Find algorithm'''
    def __init__(self, walletstrcsv, n):
        #wallet structure and wallet size csv name
        self.walletstrcsv=walletstrcsv
        self.walletszcsv=walletstrcsv.split(".")[0]+"_size.csv"
        #file exists
        if os.path.exists(walletstrcsv):
            print("edit exist wallet structure file: %s"%walletstrcsv)
            #load the data(only need the second column to recover self.par and self.sz)
            self.par=(pd.read_csv(self.walletstrcsv, header=None, usecols=[1]))[1].tolist()
            self.sz=(pd.read_csv(self.walletszcsv,header=None,usecols=[1]))[1].tolist()

            if n != None:
                #append addrs to extend to addr n, initially, each addr's parent is itself
                print("extend to addr %d"%n)
                par_len=len(self.par)
                par_to_append=[a for a in range(par_len,n)]
                sz_to_append=[1]*(n-par_len)
                self.par.extend(par_to_append)
                self.sz.extend(sz_to_append)
        #file does not exist
        else:
            if n != None:
                self.par=[i for i in range(n)]
                self.sz=[1]*n
                print("create a new wallet structure: %s with %d addrs"%(walletstrcsv,n))
            else:
                print("invalid address number n")
    
    #construct a walletbuilder with wallet structure file name and n addrs
    @classmethod
    def new(cls, walletstrcsv, n):
        return cls(walletstrcsv, n)
    
    #construct a walletbuilder with exist wallet wtructure file name
    @classmethod
    def edit(cls, walletstrcsv):
        return cls(walletstrcsv, None)

    #construct a walletbuilder with exist wallet structure file and extend to addr n
    @classmethod
    def edit_and_append(cls, walletstrcsv,n):
        return cls(walletstrcsv, n)
    
    # get root for a specific node i
    def root(self, i):
        while i != self.par[i]:
            # path compression
            self.par[i]=self.par[self.par[i]]
            i=self.par[i]

        return i


    # find if two nodes have the same root
    def find(self, p, q):
        return self.root(p)==self.root(q)

    # weighted quick union
    def unite(self, p, q):
        # find root for the elements p, q
        i=self.root(p)
        j=self.root(q)

        # if they have the same root(i.e. in the same set)
        # no need to unite
        if i == j:
            return 

        # if i's size is less than j's
        # move i under j, increment j's size
        if self.sz[i] < self.sz[j]:
            self.par[i] = j
            self.sz[j] += self.sz[i]

        # else if i's size is not less than j's 
        # move j under i, increment i's size
        else:
            self.par[j] = i
            self.sz[i] += self.sz[j]
    

    #if need to take a rest from union_find process, save the structure and size files 
    def saveProcess(self):
        #export self.sz 
        df_sz=pd.DataFrame(self.sz)
        df_sz.to_csv(self.walletszcsv,index=True,header=False)
        #clear self.sz after saving to csv
        self.sz=[]

        #export self.par
        df_par=pd.DataFrame(self.par)
        df_par.to_csv(self.walletstrcsv,index=True,header=False)
