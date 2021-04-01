from wallet_builder import WalletBuilder
import csv, gzip

#test constructor: new
#wb=WalletBuilder.new("wallet_test.csv",26)

#test constructor: edit, i.e. build on previous wallet.csv, just add more edges
#wb=WalletBuilder.edit("wallet_test.csv")

#test constructor: edit and append
#wb=WalletBuilder.edit_and_append("wallet_test.csv",30)

#test continuous read files to build wallet structure
#wb=WalletBuilder.new("walletstr_test.csv",30)
wb=WalletBuilder.edit("walletstr_test.csv")


#read test data to build wallet
directory="./testdata/"
##when edgecsv is in csv form
#edgecsv=dir+"testdata/test_edge3.csv"
#edgecsvs=["test_edge.csv","test_edge2.csv","test_edge3.csv"]
#edgecsvs=["test_edge4.csv","test_edge5.csv"]

#for ec in edgecsvs:
    #ecpath=directory+ec
    #with open(ecpath) as f:
        #readCSV=csv.reader(f,delimiter=',')
        #for row in readCSV:
            #i=int(row[0])
            #j=int(row[1])
            #wb.unite(i,j)

##when edgecsv is in gz form
#edgecsvs=["test_edge.gz","test_edge2.gz","test_edge3.gz"]
edgecsvs=["test_edge4.gz","test_edge5.gz"]
for ec in edgecsvs:
    ecpath=directory+ec
    with gzip.open(ecpath,"rt") as f:
        readCSV=csv.reader(f,delimiter=',')
        for row in readCSV:
            i=int(row[0])
            j=int(row[1])
            wb.unite(i,j)


#construct walletcsv after all edgecsvs are read
#print(wb.getRoots)
wb.saveProcess()
