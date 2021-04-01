import pandas as pd
import os
import json
import gzip
import datetime
import time
import numpy as np
import warnings
import logging
import gc

warnings.filterwarnings("ignore")

#json_dir = '../../fixed/' #directory of json
json_dir = '../../../hannah/fixed/'
block_dir = './batch7_csv_2' #directory to save the block csv
#addr_info_file='./dic_fast2.json' #address and its info
addr_info_dir='./batch7_addr_2'
#addr_info_dir='./trial_sets/'
block_info_file='./block_info_batch7.csv' #block_data
multi_sig='./multi-sig_batch2.csv' #store multi-sig address
need_reparse='./re-parse_list_batch7.csv'

#log exception, i.e. when the block contains only one coin-base tx
logging.basicConfig(filename="gz_csv_df_07.log",format='%(message)s',filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.ERROR)

#read/create need_reparse
if os.path.exists(need_reparse):
    reparse = pd.read_csv(need_reparse)
else:
    reparse=pd.DataFrame({'height':[]})

#read/create addr_info_file
#if os.path.exists(addr_info_file):
    #with open(addr_info_file,'r',encoding='utf-8') as f:
        #dic=json.load(f)
#else:
    #dic={}

#read/create block_info_file
if os.path.exists(block_info_file):
    block_info_data=pd.read_csv(block_info_file)
else:
    block_info_data=pd.DataFrame({'timestamp':[],'ntxs':[],'nBTC':[],'miner_addr':[]})

def save_block_info():
    '''save the block info'''
    block_info_data.to_csv(block_info_file,index=None)

def mark_multi_sig(df):
    '''save multi_sig info'''
    df.rename(columns={'block_id':'height'},inplace=True)
    if os.path.exists(multi_sig):        
        multi_sig_info=pd.read_csv(multi_sig)
    else:
        multi_sig_info=pd.DataFrame({'height':[],'tran_id':[],'tran_type':[],'multi-sig':[]})

    multi_sig_info=multi_sig_info.append(df,ignore_index=True)
    multi_sig_info.to_csv(multi_sig,index=None,float_format='%.0f')

def save_block_data(height,timestamp,ntx,values,miners):
    '''save the block data'''

    global block_info_data
    block_info_data=block_info_data.append({'height':height,'timestamp':timestamp,'ntxs':ntx,'nBTC':values,'miner_addr':' '.join(miners)},ignore_index=True)
    block_info_data.to_csv(block_info_file,index=None)

next_block=601049 #the first block to parse
end_block= 601050 #the last block to parse

while next_block != end_block+1 and next_block != -1:
    start = time.time()
    if os.path.exists(json_dir+str(next_block)+'.gz'):
        with gzip.open(json_dir+str(next_block)+'.gz','rt') as pf:
            json_data = json.loads(pf.read())

        #dic=set()
        #dic={}
        tran_data = json_data['tx']
        miners=[]
        split_reward=[]
        height=json_data['height']
        for i in range(len(tran_data)):
            tran_data[i]['tran_id']=i

        ntx=json_data['nTx']
        try:
            inputs=pd.io.json.json_normalize(tran_data,record_path='vin',meta='tran_id')[['tran_id','txvoutinfo.value','txvoutinfo.addresses']]
        except Exception as e:
            errormes = "at block height %s, encounter error %s"%(height,e)
            logger.error(errormes)
            inputs=pd.io.json.json_normalize(tran_data,record_path='vin',meta='tran_id')
            pass
        out=pd.io.json.json_normalize(tran_data,record_path='vout',meta='tran_id')[['tran_id','value','scriptPubKey.addresses']]
        timestamp=json_data['time']
        ntx=json_data['nTx']
        
        #miners
        for i in range(len(tran_data[0]['vout'])):
            if 'addresses' in tran_data[0]['vout'][i]['scriptPubKey'] and len(tran_data[0]['vout'][i]['scriptPubKey']['addresses'])==1:
                miners.append(tran_data[0]['vout'][i]['scriptPubKey']['addresses'][0])
                split_reward.append(float(tran_data[0]['vout'][i]['value']))# the proportion of block reward for each miner
        
        reward=sum(split_reward)
        for i in range(len(split_reward)):
            split_reward[i]/=reward

        #merge inputs and outputs
        inputs.columns=['tran_id','value','addr']
        out.columns=['tran_id','value','addr']
        inputs['tran_type']='input'
        out['tran_type']='output'
        t=inputs.append(out,ignore_index=True)
        t['block_id']=json_data['height']
        t=t.drop(index=0)
        t=t.sort_values(axis=0,ascending=True,by=['tran_id','tran_type'])
        t=t.reset_index(drop=True)

        #store address info
        multisig=pd.DataFrame({})
        #get txs that only contain list-type addresses
        t=t.loc[t.addr.apply(type)==list]
        #get multisig rows
        multisigdf=t.loc[t.addr.apply(len)>1]

        #mark multisig if multisigdf is not empty 
        if not multisigdf.empty:
            #multisigdf.apply(lambda row: mark_multi_sig_helper(row),axis=1)
            multisigdf['multi-sig']=multisigdf['addr'].str.len()
            multisigdf['value']=pd.to_numeric(multisigdf['value'])/multisigdf['addr'].str.len()
            mark_multi_sig(multisigdf[['block_id','tran_id','tran_type','multi-sig']])
            #spread multisigdf
            multisigdf=multisigdf[['tran_id','value','addr','tran_type','block_id']]
            multisig=multisigdf.explode('addr')
        
        #drop OP_RETURN and multisig rows
        t=t.loc[t.addr.apply(len)==1]
        #convert value column to numeric
        t['value']=pd.to_numeric(t['value'])
        t['addr']=t['addr'].str.get(0)
        #rejoin multisig rows
        t=t.append(multisig,ignore_index=True)

        #map the dic with addresses
        #t['int']=t['addr'].map(dic)
        #addr to add, drop duplicates
        #addr_to_add=t.loc[t['int'].isnull()][['addr']].drop_duplicates()
        #if len(dic) is not zero, add the len(dic) to index, to keep indexing(bug here, the index column is not correc) 
        #addr_to_add=addr_to_add.reset_index(drop=True)
        #addr_to_add['id']=len(dic)+addr_to_add.index
        #make addr into row name
        #addr_to_add=addr_to_add.set_index('addr')
        #addr_to_add.index.names=[None]

        #convert to dic
        #new_dic=addr_to_add['id'].to_dict()
        #dic.update(new_dic)
        
        #dic.update(t['addr'])
        #addrdic=dict.fromkeys(dic,0)
        uniqueaddr=t[['addr']].drop_duplicates()
        #t=t.drop(['int'],axis=1)
        t=t.dropna()

        #about the transaction fee
        total_in=sum(t[t['tran_type']=='input']['value'])
        total_out=sum(t[t['tran_type']=='output']['value'])
        #fee=total_in-total_out+t.iloc[0]['value'] #this is transaction fee, but a buggy one, since there may be multiple miners, t.iloc[0]['value'] only covers the first miner 
        #fee=t.iloc[0]['value'] #the total reward the first miner got (block reward+transaction fee)
        fee=total_in-total_out+t.iloc[0]['value']

        for j in range(len(miners)):
            t=t.append({'tran_id':i,'value':fee*split_reward[j],'addr':miners[j],'tran_type':'miner','block_id':json_data['height']},ignore_index=True)

        #save the files
        t.to_csv(block_dir+'/block'+str(next_block)+'.csv',index=None)
        pf.close()
        save_block_data(json_data['height'],timestamp,ntx,total_in,miners)
        
        #save the addresses
        uniqueaddr.to_csv(addr_info_dir+'/addr'+str(next_block)+'.csv',index=None)
        #with open('dic_fast.json','w',encoding='utf-8') as f:
            #json.dump(dic,f,ensure_ascii=False,indent=4)
        
        #dicfile=addr_info_dir+('dic%s.json'%height)
        #dicfile = addr_info_dir+('dic%s.txt'%height)
        
        #with open(dicfile,'w',encoding='utf-8') as f:
            #json.dump(addrdic,f,ensure_ascii=False, indent=4)
            #f.write(str(dic))

        end=time.time()
        print('Successfully saved block {} taking {}s'.format(height,end-start))
        print('======================================')
        next_block += 1
        if next_block == end_block +1:
            print('Congrats! You have parsed all json files!')
            collected=gc.collect()

    else:
        print('Cannot find block {}.'.format(next_block))
        next_block=-1
        
        
