from edge_list_builder import EdgeListBuilder
from wallet_builder import WalletBuilder
from wallet import Wallet
import datetime
import csv
import gzip
""" for current use, it's recommended to build edge list for all block files first; then, collect all generated edge.csv files into a list, to read into a wallet builder to build the wallet. In the future, if we only have a few files, then, 
we can do all 3 steps at once for one block file."""
start=datetime.datetime.now()
## 1. build edge list:
#mappedcsvdir="../mapped/"
#mappedcsv_ls=["block546634_546636_mapped.csv","block546637_546639_mapped.csv"]
#for m in mappedcsv_ls:
#    mappedcsv=mappedcsvdir+m
#    eb=EdgeListBuilder.fromWhole(mappedcsv)
#    eb.constructEdgeListCSV()
#    print("yielded edgecsv for  %s"%m)
#

## 2. build wallet structure:
wallet_structure_file="walletStructure_fromeg.csv"
wb=WalletBuilder.new(wallet_structure_file,3000000)
# wb=WalletBuilder.edit(wallet_structure_file)
# (1) read edgcsv to build wallet
edgecsvdir="../edgecsv/"
edgecsvs=["block546634_546636_edge.gz","block546637_546639_edge.gz"]
for ec in edgecsvs:
    ecpath=edgecsvdir+ec
    with gzip.open(ecpath,"rt") as f:
        readCSV=csv.reader(f,delimiter=',')
        for row in readCSV:
            i=int(row[0])
            j=int(row[1])
            wb.unite(i,j)
        print("finish reading %s"%ec)


# print("start to save the process")
# (2) save process if want to take a break (make take a while if you have many addrs)
wb.saveProcess()

## 3. create wallet id csv:
# input wallet structure file (only need the one that stores the parent id) as above: wallet_structure_file
# desired output wallet id csv file name
#walletcsv="wallet.csv"
# wallet object
#w=Wallet(wallet_structure_file,walletcsv)
#w.constructWalletCSV()

end=datetime.datetime.now()
elapsed=end-start
print(elapsed)
