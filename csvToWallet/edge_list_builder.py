import pandas as pd
import numpy as np
import re
import os

#directory to store the export edgecsv, change accordingly
directory='../edgecsv'
if not os.path.exists(directory):
    os.makedirs(directory)
    
class EdgeListBuilder:
    '''take a xxx_mapped.csv file to construct an edge-list csv'''
    def __init__(self, mappedcsv, start, end, partial):
        self.mappedcsv=mappedcsv
        self.start=start
        self.end=end
        self.partial=partial
        self.edgeData=[]
        #self.edgecsv=directory+"/block%d_%d_edge.csv"%(start,end)
        self.edgecsv=directory+"/block_%d_edge.gz"%(start,end)

    #construct an EdgeListBuilder from the whole xxx_mapped.csv file
    @classmethod
    def fromWhole(cls, mappedcsv):
        #get the start and end
        range_ls=re.findall(r"\d+",mappedcsv)
        start=int(range_ls[0])
        if len(range_ls) == 1:
            end=start
        else:
            end=int(range_ls[1])
        return cls(mappedcsv,start,end,False)

    #construct an EdgeListBuilder from part of the xxx_mapped.csv file
    #can use this when the file is too large
    @classmethod
    def fromPartial(cls, mappedcsv, start, end):
        return cls(mappedcsv,start,end,True)

    def dataOfInterest(self):
        blk=pd.read_csv(self.mappedcsv)
        blk_in=blk.loc[blk.tran_type=="input"].drop(columns=['value','tran_type'])
        
        if self.partial:
            #filter the partial range
            height=(blk_in['block_id']>=self.start) & (blk_in['block_id']<=self.end)
            blk_in_g=(blk_in.loc[height]).groupby(['tran_id','block_id'])
        else: 
            #use the whole data
            blk_in_g=blk_in.groupby(['tran_id','block_id'])

        return blk_in_g

    #get edges for each txid-blockid group
    def getEdges(self, group):
        unique_arr=np.unique(group['addr'])
        i,j=np.triu_indices(len(unique_arr),1)
        arr=np.stack([unique_arr[i],unique_arr[j]]).T
        if arr.size != 0:
            self.edgeData.append(arr)

    def exportToCSV(self):
        #stack the list of ndarray
        dataStack=np.vstack(self.edgeData)
        #clear edgeData
        self.edgeData=[]
        #convert stack of ndarray to dataframe
        dataDF=pd.DataFrame(dataStack)
        #dataDF.to_csv(self.edgecsv,header=False,index=False)
        dataDF.to_csv(self.edgecsv,header=False,index=False,compression='gzip')

    def constructEdgeListCSV(self):
        blk_in_g=self.dataOfInterest()
        blk_in_g.apply(lambda x: self.getEdges(x))
        self.exportToCSV()

    def getCSVFileName(self):
        return self.edgecsv
