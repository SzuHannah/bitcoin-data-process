# bitcoin-neo4j-notes
Documenting some useful command for constructing neo4j database for bitcoin data  
## Useful commands  
### pre-processing bitcoin-csv files  
1. from blockxxxx_xxxx.csv to input_rel and output_rel(split transaction records of each block into input and output)  
(1) add transactionID(create with block_id and tran_id)  
(2) split files into input and output(according to tran_type)  
- use command line tool: [Miller](https://miller.readthedocs.io/en/latest/10min.html#min-choices-for-printing-to-files)  
```cmd
#eg. filter input and then add tran_id
mlr --csv filter '$tran_type == "input"' block546634_550000_mapped.csv then put -S '$txID=${block_id}."".${tran_id}' > block546634_550000_tran.csv
```
```cmd
#merge block_info(files with the same headers), ref: http://rolandtanglao.com/2019/02/15/p1-using-miller-aka-mlr-to-combine-selected-fields-from-a-csv-file/
mlr --csv cut -f timestamp,ntxs,nBTC,miner_addr,block_id *.csv > block_info_546634_632887.csv

#add header to a file
mlr -I --csv --implicit-csv-header label walletid,addrnum wallet_summary.csv
```
2. remove header from csv files, [ref](https://stackoverflow.com/questions/9633114/unix-script-to-remove-the-first-line-of-a-csv-file)
```cmd
# remove header for file.csv and store the without-header-file as file2.csv
sed 1d file.csv > file2.csv
```
### [Docker operations](https://neo4j.com/docs/operations-manual/current/docker/operations/)
1. check recommended memory
```cmd
docker exec --interactive --tty testneo4j neo4j-admin memrec --memory=64g --docker
#
# Based on the above, the following memory settings are recommended:
dbms.memory.heap.initial_size=24g
dbms.memory.heap.max_size=24g
dbms.memory.pagecache.size=28g
```
2. run docker and set environmental variables
```cmd
docker run --name testneo4j -p7474:7474 -p7687:7687  -d   -v $HOME/neo4j/data:/data  -v $HOME/neo4j/logs:/logs  -v $HOME/neo4j/import:/var/lib/neo4j/import -v $HOME/neo4j/plugins:/plugins  --env NEO4J_AUTH=neo4j/test --env NEO4J_dbms_memory_heap_initial__size=5g --env NEO4J_dbms_memory_heap_max__size=5g --env NEO4J_dbms_memory_pagecache_size=7g  neo4j:latest 
```
- on peach (container name:bitcoinneo4j; mount /scratch/bitcoin/import/neo4jContainer as container's /var/lib/neo4j/import (if only write /import, it won't mount successfully); mount /scratch/bitcoin/data as container's /data; create docker volume called bticoindblogs and mount it to /logs in bitcoindb container; create docker volume called bitcoindbplugins and mount it to /plugins in bitciondb container; add [apoc plugins](https://neo4j.com/labs/apoc/4.0/installation/#docker))

```
docker run --name bitcoindb -p7474:7474 -p7687:7687  -d -v /scratch/bitcoin/import/neo4jContainer:/var/lib/neo4j/import  -v /scratch/bitcoin/data:/data -v bitcoindblogs:/logs -v /scratch/bitcoin/plugins:/var/lib/neo4j/plugins  --env NEO4J_AUTH=neo4j/test --env NEO4J_dbms_memory_heap_initial__size=24g --env NEO4J_dbms_memory_heap_max__size=24g --env NEO4J_dbms_memory_pagecache_size=28g --env NEO4J_apoc_export_file_enabled=true --env NEO4J_apoc_import_file_enabled=true --env NEO4J_apoc_import_file_use__neo4j__config=true --env NEO4J_dbms_security_procedures_unrestricted=apoc.* --env NEO4J_dbms_recovery_fail__on__missing__files=false --env NEO4JLABS_PLUGINS=\[\"apoc\"\] neo4j:latest
```
- write to docker volume is faster (use this)
```
docker run --name bitcoindb -p7474:7474 -p7687:7687  -d -v /scratch/bitcoin/import/neo4jContainer:/var/lib/neo4j/import  -v bitcoindbdata:/data -v bitcoindblogs:/logs -v /scratch/bitcoin/plugins:/var/lib/neo4j/plugins  --env NEO4J_AUTH=neo4j/test --env NEO4J_dbms_memory_heap_initial__size=24g --env NEO4J_dbms_memory_heap_max__size=24g --env NEO4J_dbms_memory_pagecache_size=28g --env NEO4J_apoc_export_file_enabled=true --env NEO4J_apoc_import_file_enabled=true --env NEO4J_apoc_import_file_use__neo4j__config=true --env NEO4J_dbms_security_procedures_unrestricted=apoc.*,gds.* --env NEO4J_dbms_recovery_fail__on__missing__files=false --env NEO4JLABS_PLUGINS=\[\"apoc\"\,\"graph-data-science\"\] neo4j:latest
```

3. check docker is running
```cmd
docker ps
```
4. copy files from local into docker (this is an example where docker mount import on /var/lib/neo4j/import as specified in step 2
```
docker cp block.csv testneo4j:/var/lib/neo4j/import/
```
5. enter docker bash, and cd into import/ to check the files are in docker
```
docker exec -it testneo4j bash
cd import
```

6. [docker bulk import](https://stackoverflow.com/questions/60372472/neo4j-docker-admin-import-database-not-found)
```cmd
export DATA=import
./bin/neo4j-admin import --database neo4j --nodes=Block="$DATA/block_header.csv,$DATA/block.csv" --nodes=Transaction="$DATA/tx_header.csv,$DATA/containsTx/woh.*" --nodes=Wallet="$DATA/wallet_header.csv,$DATA/wallet.csv" --relationships=CONTAINS="$DATA/contains_rel_header.csv,$DATA/containsTx/woh.*" --relationships=INPUT="$DATA/input_rel_header.csv,$DATA/input/woh.*" --relationships=OUTPUT="$DATA/output_rel_header.csv,$DATA/output/woh.*" --high-io=true --skip-duplicate-nodes=true
```

- import to docker volume is faster (also, exclude block node & contains relationshpi import)
```
export DATA=import
./bin/neo4j-admin import --database neo4j --nodes=Transaction="$DATA/tx_header.csv,$DATA/containsTx/woh.*" --nodes=Wallet="$DATA/wallet_header.csv,$DATA/wallet.csv" --relationships=INPUT="$DATA/input_rel_header.csv,$DATA/input/woh.*" --relationships=OUTPUT="$DATA/output_rel_header.csv,$DATA/output/woh.*" --high-io=true --skip-duplicate-nodes=true
```

7. stop docker 
```
docker stop testneo4j
```

8. remove docker container (no need if the container successfully import all the data)
```
docker rm testneo4j
```
9. trial import on peach: 2021.01.09, it took 1h 4m 20s to import if write directly to docker; however, it took 3h 30m 52s 737ms if I mount the output data/ to local host.

10. start cypher shell
```cmd
cypher-shell -u neo4j -p test
```

11. start an existed docker
```
docker start bitcoindb
docker exec -it bitcoindb bash
```

12. if you need to modify present configurations  
- [ref](https://neo4j.com/developer/docker-run-neo4j/)

13. currently on peach:
the database is up, and the transactions nodes have inherited timestamp from block nodes

14. add sent_to relationship, and remove transaction node adn the input output relationships [detach delete t can achieve this](https://neo4j.com/graphacademy/training-intro-40/11-deleting-nodes-and-relationships/) (use command line, i.e. no need to do cypher-shee -u neo4j -p, you can type the command right after cypher-shell)
```
cypher-shell "call apoc.periodic.iterate('match (w1:Wallet)-[i:INPUT]->(t:Transaction)-[o:OUTPUT]->(w2:Wallet) return w1,i,t,o,w2','create (w1)-[s:SENT_TO{time:t.timestamp,value:(i.value/t.inputTotal)*o.value}]->(w2) detach delete t',{batchSize:10000,iterateList:true,parallel:false});"
```
15. [export database](https://neo4j.com/labs/apoc/4.1/export/csv/), I think it's more reasoanble to use output value as the transactoin value between wallet-wallet, since all inputs of a transaction should come frmo the same wallets, it does not matter the amount each addr in the wallet contributes, so, we don't need (i.value/t.inputTotal)o.value, just use o.value isntead. It took around 1 day 7 hours to export.
```
with "match (w1:Wallet)-[i:INPUT]->(t:Transaction)-[o:OUTPUT]->(w2:Wallet)
      return w1.walletID as sentwallet, w2.walletID as receivewallet, o.value as value, t.timestamp as time" as query
      call apoc.export.csv.query(query,"sent_to.csv",{})
      YIELD file, source, format, nodes, relationships, properties, time, rows, batchSize, batches, done, data
      RETURN file, source, format, nodes, relationships, properties, time, rows, batchSize, batches, done, data;
```
- filter transactinos after 2017.01
```
with "match (w1:Wallet)-[i:INPUT]->(t:Transaction)-[o:OUTPUT]->(w2:Wallet)
             where t.timestamp > datetime({year:2017, month: 1})
             return w1.walletID as sentwallet, w2.walletID as receivewallet, o.value as value, t.timestamp as time" as query
             call apoc.export.csv.query(query,"sent_to_2017.csv",{})
             YIELD file, source, format, nodes, relationships, properties, time, rows, batchSize, batches, done, data
             RETURN file, source, format, nodes, relationships, properties, time, rows, batchSize, batches, done, data;
```

** inside docker, you can do "df -h" to check the filesystems of the docker.  
16. create a second db with container 
- sent_to graph, >600GB, so store data on host, tihs one I need graph-data-science library  
```
docker run --name wallettxdb -p1474:7474 -p1687:7687  -d -v /scratch/bitcoin/import/neo4jContainer:/var/lib/neo4j/import  -v /scratch/bitcoin/wallettxdbdata:/data -v wallettxdblogs:/logs -v /scratch/bitcoin/plugins:/var/lib/neo4j/plugins  --env NEO4J_AUTH=neo4j/test --env NEO4J_dbms_memory_heap_initial__size=24g --env NEO4J_dbms_memory_heap_max__size=24g --env NEO4J_dbms_memory_pagecache_size=28g --env NEO4J_apoc_export_file_enabled=true --env NEO4J_apoc_import_file_enabled=true --env NEO4J_apoc_import_file_use__neo4j__config=true --env NEO4J_dbms_security_procedures_unrestricted=apoc.*,gds.* --env NEO4J_dbms_recovery_fail__on__missing__files=false --env NEO4JLABS_PLUGINS=\[\"apoc\",\"graph-data-science\"\] neo4j:latest
```
- or sent_to_2017 graph (only use transactinos after 2016.12, since it was reported that the right wings became more active after summer 2017, import done in 4h 56m, and took up 368 GB)
```
docker run --name wallettxdb -p1474:7474 -p1687:7687  -d -v /scratch/bitcoin/import/neo4jContainer:/var/lib/neo4j/import  -v /scratch/bitcoin/wallettxdbdata:/data -v wallettxdblogs:/logs -v /scratch/bitcoin/plugins:/var/lib/neo4j/plugins  --env NEO4J_AUTH=neo4j/test --env NEO4J_dbms_memory_heap_initial__size=24g --env NEO4J_dbms_memory_heap_max__size=24g --env NEO4J_dbms_memory_pagecache_size=28g --env NEO4J_apoc_export_file_enabled=true --env NEO4J_apoc_import_file_enabled=true --env NEO4J_apoc_import_file_use__neo4j__config=true --env NEO4J_dbms_security_procedures_unrestricted=apoc.*,gds.* --env NEO4J_dbms_recovery_fail__on__missing__files=false --env NEO4JLABS_PLUGINS=\[\"apoc\",\"graph-data-science\"\] neo4j:latest
```

- or grouped the sent,receive wallets of sent_to_2017(using sqlite) and sum up the tx values after 2017 between each sent,receive pair
```
docker run --name wallettxdb -p7474:7474 -p7687:7687  -d -v /scratch/bitcoin/import/neo4jContainer:/var/lib/neo4j/import  -v wallettxdbdata:/data -v wallettxdblogs:/logs -v /scratch/bitcoin/plugins:/var/lib/neo4j/plugins  --env NEO4J_AUTH=none --env NEO4J_dbms_memory_heap_initial__size=24g --env NEO4J_dbms_memory_heap_max__size=24g --env NEO4J_dbms_memory_pagecache_size=28g --env NEO4J_apoc_export_file_enabled=true --env NEO4J_apoc_import_file_enabled=true --env NEO4J_apoc_import_file_use__neo4j__config=true --env NEO4J_dbms_security_procedures_unrestricted=apoc.*,gds.* --env NEO4J_dbms_recovery_fail__on__missing__files=false --env NEO4JLABS_PLUGINS=\[\"apoc\",\"graph-data-science\"\] --env NEO4J_dbms_connector_https_advertised__address="localhost:7473" --env NEO4J_dbms_connector_http_advertised__address="localhost:7474" --env NEO4J_dbms_connector_bolt_advertised__address="localhost:7687" neo4j:latest

```
- neo4j 3.5.21 version (use this) such that you can use neo4r to connect with neo4j
```
docker run --name wallettxdb -p7474:7474 -p7687:7687  -d -v /scratch/bitcoin/import/neo4jContainer:/var/lib/neo4j/import  -v wallettxdbdata:/data -v wallettxdblogs:/logs -v /scratch/bitcoin/plugins:/var/lib/neo4j/plugins  --env NEO4J_AUTH=neo4j/pass --env NEO4J_dbms_memory_heap_initial__size=24g --env NEO4J_dbms_memory_heap_max__size=24g --env NEO4J_dbms_memory_pagecache_size=28g --env NEO4J_apoc_export_file_enabled=true --env NEO4J_apoc_import_file_enabled=true --env NEO4J_apoc_import_file_use__neo4j__config=true --env NEO4J_dbms_security_procedures_unrestricted=apoc.*,gds.* --env NEO4J_dbms_recovery_fail__on__missing__files=false --env NEO4JLABS_PLUGINS=\[\"apoc\",\"graph-data-science\"\] neo4j:3.5.21
```

- bulk imoprt
```
export DATA=import
./bin/neo4j-admin import --database neo4j --nodes=Wallet="$DATA/wallet_header.csv,$DATA/wallet.csv" --relationships=SENT_TO="$DATA/groupedtx2017_header.csv,$DATA/groupedtx2017.csv" --high-io=true --skip-duplicate-nodes=true
```
- [bulk import neo4j 3.5.21 version (use this)](https://rajfal.github.io/2018/Create-a-clean-Neo4j-database-inside-Docker-container/); [ref2](https://neo4j.com/blog/import-10m-stack-overflow-questions/)
```
exoprt DATA = imoprt
./bin/neo4j-admin import --database graph.db --nodes:Wallet "$DATA/wallet_header.csv,$DATA/wallet.csv" --relationships:SENT_TO "$DATA/groupedtx2017_header.csv,$DATA/groupedtx2017.csv" --high-io=true --ignore-duplicate-nodes=true
```
17. change datatype (took 3 hours)
```
call apoc.periodic.iterate(
             "match (t:Transaction) return t",
             "set t.timestamp=datetime(t.timestamp)",
             {limit:10000})
             ;
```
18. [check metadata node property type](https://community.neo4j.com/t/data-type-of-a-property/1309/2); [wholistic view of the database](https://neo4j.com/blog/data-profiling-holistic-view-neo4j/)
```
call apoc.meta.nodeTypeProperties();
```

19. Projecting graph

- sent_to normal direction
```
call gds.graph.create('txgraph','Wallet','*') yield graphName, nodeCount, relationshipCount;
```
- sent_to reverse directoin
```
call gds.graph.create('txgraph-upstream','Wallet',{RECEIVE_FROM:{type:'SENT_TO',orientation:'REVERSE'}}) yield graphName,nodeCount,relationshipCount;`
```

20. collapse relationship with neo4j
- [ref](https://community.neo4j.com/t/aggregate-collapse-roll-up-relationships-with-cypher/3083)

21. remove self-loop
```
 call apoc.periodic.iterate("match (w:Wallet)-[r:SENT_TO]->(w) return r","delete r",{batchSize:1000}) yield batches, total return batches, total
```

22. remove nodes with degree=0&1, usually ndoes with degree=1 are not that important (might be important sometimes, but it's rare). I want to remove it 'cause it's causing aPPR converge slowly
```
call apoc.periodic.iterate("match(w:Wallet) with w,apoc.node.degree(w) as deg where deg=0 return w","delete w",{batchSize:10000}) yield batches, total return batches, total;
```
- this also deletes the relationship that is connected with the node that only has degree 1; thus, making some nodes with degree 2 become degree-1-node, and then got deleted
```
call apoc.periodic.iterate("match(w:Wallet) with w,apoc.node.degree(w) as deg where deg=1 return w","detach delete w",{batchSize:10000}) yield batches, total return batches, total;
```
23. export csv
```
with "match path=(w:Wallet)-[s:SENT_TO]->(m:Wallet) return w.walletID as source, m.walletID as target" as query call apoc.export.csv.query(query,"sent_to_moredeg.csv",{}) yield file, source, format, nodes, relationships, properties, time, rows, batchSize, batches, done, data return file, source, format, nodes, relationships, properties, time, rows, batchSize, batches, done, data;
```
24. calculate personalized pagerank
- one seed node
```
match(nick:Wallet{walletID:'327466217'}) call gds.pageRank.stream('txgraph',{maxIterations:20,dampingFactor:0.85,sourceNodes:[nick]}) yield nodeId, score return gds.util.asNode(nodeId).walletID as walletID, score order by score desc limit 30;
```
- multiple seed nodes
```
match(w:Wallet) where w.walletID in ['7480','2096025','5279538','327466217','73091417','110567775','781745','347248','155260033','168586723','178055641','183649279'] with collect(w) as seeds call gds.pageRank.stream('txgraph',{maxIterations:20,dampingFactor:0.85,sourceNodes:seeds}) yield nodeId, score return gds.util.asNode(nodeId).walletID as walletID, score order by score desc limit 30;

##if want to export to csv
with "match(w:Wallet) where w.walletID in ['7480','2096025','5279538','327466217','73091417','110567775','781745','347248','155260033','168586723','178055641','183649279'] with collect(w) as seeds call gds.pageRank.stream('txgraph',{maxIterations:20,dampingFactor:0.85,sourceNodes:seeds}) yield nodeId, score return gds.util.asNode(nodeId).walletID as walletID, score order by score desc limit 30;" as query call apoc.export.csv.query(query,"right_activist_downstreamppr.csv",{}) yield file, source, format, nodes, relationships, properties, time, rows, batchSize, batches, done, data return file, source, format, nodes, relationships, properties, time, rows, batchSize, batches, done, data;

```

### neo4j dcoker connection with R
1. use neo4r library
2. use neo4j 3.5.21
3. R codes:
```R
# connect to neo4j
library(noe4r)
cno<-neo4j_api$new(url="http://localhost:7474", user="neo4j", password="pass")
# check connectoin, should return 200
con$ping()
```

### disk space not releasedafter removing files (df -h)
[might be because the process is still open](https://unix.stackexchange.com/questions/34140/tell-fs-to-free-space-from-deleted-files-now)

### bulk import into database
1. [import several files under a directory with regex](https://neo4j.com/docs/operations-manual/current/tools/neo4j-admin-import/#neo4j-admin-import)
2. commands for bulk import
```cmd
#name the DATA variable
 export DATA=/media/hannah/Samsung_T5/bitcoin_txdb/wallet_tx/mapped/test/import
#command for bulk import into database named neo4j(the database name can be found under the dropdown list after starting the database GUI)
./bin/neo4j-admin import --database neo4j --nodes=Block="$DATA/block_header.csv,$DATA/block.csv" --nodes=Transaction="$DATA/tx_header.csv,$DATA/tx.csv" --nodes=Wallet="$DATA/wallet_header.csv,$DATA/wallet.csv" --relationships=CONTAINS="$DATA/contains_rel_header.csv,$DATA/contains_rel.csv" --relationships=INPUT="$DATA/input_rel_header.csv,$DATA/input_rel.csv" --relationships=OUTPUT="$DATA/output_rel_header.csv,$DATA/output_rel.csv" --high-io=true
```
3. [multiple input files](https://neo4j.com/docs/operations-manual/current/tutorial/neo4j-admin-import/#tutorial-neo4j-admin-import)
### add integer addr representation (property name: addr) for existing Address nodes (i.e. add a property for existing nodes)  
1. put 'addr.csv' under import/ directory (in this example, addrID, the addr string representation is the 1st column; addr, the addr integer representaion is the 2nd column)      
2. cypher command 
- when the csv has no header, and when the node does not have the property addr yet: 
[reference for load csv](https://neo4j.com/developer/guide-import-csv/#_optimizing_load_csv_for_performance)  
```cypher
load csv from "file:///addrs.csv" as line
match(n:Address)
where n.addrID=line[0]
set n.addr=line[1]
```  
- when the csv has no header, and when the node already had the property addr:  
```cypher
load csv from "file:///addrs.csv" as line
merge(n:Address{addr:line[1]})
on create set n.addrID=line[0], n.addr=line[1] #create if the node does not exist
on match set n.addr=line[1] #update the addr property if the node exist
```  
- remove a property from one type of node  
[reference for remove](https://www.tutorialspoint.com/neo4j/neo4j_remove_clause.html)
```cypher
match (a:Address) 
remove a.addr
```
- create SENT_TO relationsihp between wallets and at the same time set value and timestamp
```cypher
call apoc.periodic.iterate(
"match (w1:Wallet)-[i:INPUT]->(t:Transaction)-[o:OUTPUT]->(w2:Wallet) return w1,i,t,o,w2",
"create (w1)-[s:SENT_TO{time:t.timestamp,value:(i.value/t.inputTotal)*o.value}]->(w2)",
{batchSize:10000,iterateList:true,parallel:false})
```

- or use this (thuogh this is CPU-intensive)
```cypher
call apoc.periodic.commit(
             "match (w1:Wallet)-[i:INPUT]->(t:Transaction)-[o:OUTPUT]->(w2:Wallet)
             with w1,i,t,o,w2 limit $limit
             create (w1)-[s:SENT_TO{time:t.timestamp,value:(i.value/t.inputTotal)*o.value}]->(w2)",
             {limit:1000})
```
- better, use merge, such that if w1 ever sent to w2, it'll just create one relationship (use this), [ref](https://community.neo4j.com/t/aggregate-collapse-roll-up-relationships-with-cypher/3083)
```
call apoc.periodic.iterate(
"match (w1:Wallet)-[i:INPUT]->(t:Transaction)-[o:OUTPUT]->(w2:Wallet) return w1,i,o,w2",
"merge (w1)-[s:SENT_TO]->(w2) on create set s.value=o.value on match set s.value=s.value+o.value",
{batchSize:10000,iterateList:true,parallel:false})
```

- create SENT_TO relatoinship between addresses (similar for wallets)
```cypher
match (a1:Address)-[:INPUT]->(t:Transaction)-[:OUTPUT]->(a2:Address)
match (t)-[:INCLUDES_IN]->(b:Block)
create (a1)-[s:SENT_TO{time:b.timeStamp}]->(a2)
```
- set property for an existing relatinoship
```cypher
match (a1:Address)-[:INPUT]->(t:Transaction)-[:OUTPUT]->(a2:Address)
match (t)-[:INCLUDES_IN]->(b:Block)
match (a1)-[s]->(a2) #this means that there exists a relationship(s) between a1,a2
set s.time=b.timeStamp
```
- group-by, sum values, and set as a property (here's an example that I summed up the total output value for each transaction, and set it as a property for the 
transaction node)  
```cypher
call apoc.periodic.iterate(
"MATCH (t:Transaction)-[o:OUTPUT]->() return t, sum(o.value) as outval",
"set t.outputTotal=outval",
{batchSize:1000,iterateList:true,parallel:false})
```
- set value for the sent_to relatoinhsip (value was calculated according to the input amount the address contribute to the transaction)  
```cypher
MATCH (a1:Address)-[i:INPUT]->(t:Transaction)-[o:OUTPUT]->(a2:Address)
match (a1)-[s]->(a2)
set s.value=(i.value / t.inputTotal) * t.outputTotal
```
- create new database  
if you have a large amount of data, initialize an empty database through switching to "system" first
[ref](https://community.neo4j.com/t/neo4j-admin-import-successful-but-no-data-shown-in-database/17180/5)

- add timeStamp to transaction node (on peach, this took up around 30%-57% memmory, amd took around 1h physical time)
```cypher
call apoc.periodic.iterate(
"match (b:Block)-[:CONTAINS]->(t:Transaction) return b,t",
"set t.timeStamp=b.timestamp",
{batchSize:10000,iterateList:true,parallel:false})
```

- build wallet-graph:  
(a) match input addresses that are spent together, and create the relationship, :SAME_WALLET    
(b) project ([native projection](https://neo4j.com/docs/graph-data-science/current/management-ops/native-projection/)) the nodes and the spent together addresses to build the wallet graph  
(c) use [weekly connected component algorithm](https://neo4j.com/docs/graph-data-science/current/algorithms/wcc/) to find component id  
```cypher
MATCH (a1:Address)-[:SENDS]->(t:Transaction)<-[:SENDS]-(a2:Address) RETURN a1, a2
MERGE (a1)-[:SAME_WALLET]-(a2)
```
```cypher
#name the projected graph: wallet-graph; take Address node ('Address') and all relationships ('*'))
CALL gds.graph.create('wallet-graph', 'Address', '*')
YIELD graphName, nodeCount, relationshipCount;
```
  
- [write the component ids back to neo4j database](https://neo4j.com/docs/graph-data-science/current/management-ops/graph-catalog-ops/#catalog-graph-write-relationship)   

### Debugging
1. If the process get killed or stuck, it might be because you have too many duplicate rows.  
2. If you fail to start the database (this might happen after logout and relogin to the peach server), and inside debug.log, you saw the message "Mismatching store id. Store StoreId: StoreId{creationTime=1610685843158, randomId=1973819688182322958, storeVersion=7002588545122976007, upgradeTime=1610685843158, upgradeTxId=1}. Transaction log StoreId: StoreId{creationTime=1610685518881, randomId=8344178847567337079, storeVersion=7002588545122976007, upgradeTime=1610685518881, upgradeTxId=1}", try to delete the neo4/ directory under data/transactions. Add dbms.recovery.fail_on_missing_files=false to the neo4j.conf file. Then, restart the container. Or, if you want to remove the container and rebuild:
[ref](https://github.com/neo4j/neo4j/issues/12388#issuecomment-630209019)
```
docker stop bitcoindb
docker run --name bitcoindb -p7474:7474 -p7687:7687  -d -v /scratch/bitcoin/import/neo4jContainer:/var/lib/neo4j/import  -v /scratch/bitcoin/data:/data -v bitcoindblogs:/logs -v /scratch/bitcoin/plugins:/var/lib/neo4j/plugins  --env NEO4J_AUTH=neo4j/test --env NEO4J_dbms_memory_heap_initial__size=25g --env NEO4J_dbms_memory_heap_max__size=25g --env NEO4J_dbms_memory_pagecache_size=25g --env NEO4J_apoc_export_file_enabled=true --env NEO4J_apoc_import_file_enabled=true --env NEO4J_apoc_import_file_use__neo4j__config=true --env NEO4J_dbms_security_procedures_unrestricted=apoc.* --env NEO4J_dbms_recovery_fail__on__missing__files=false neo4j:latest
```
3. About the warnings regarding apoc, shouldn't matter though. [ref](https://community.neo4j.com/t/failed-to-load-apoc/11792/5)
4. [communication between local host and container](https://community.neo4j.com/t/communication-between-neo4j-browser-and-container-not-working/17212)
5. [when query from neo4j is too slow, it might be because the database does not contain indices.](https://stackoverflow.com/questions/32472968/neo4j-match-and-create-takes-too-long-in-a-10000-node-graph)
```
create index on :Wallet(walletID)
```

### External bitcoin info
1. Possible right-wing addresses (derived from the suspective transaction happened on 12.08.2020 (UTC)  
- [the original transactoin](https://www.blockchain.com/btc/tx/05ab9bb347c3bf6b0bb52c9b756a924b5ad5db63f45a885db6b170865fbdb285?page=2)
- [the news](https://news.yahoo.com/exclusive-large-bitcoin-payments-to-rightwing-activists-a-month-before-capitol-riot-linked-to-foreign-account-181954668.html)
- [the addresses](external/rightWingFrom1208.csv)
- [alt-right bitcoin wallets](https://www.splcenter.org/bitcoin-and-alt-right)
- [more info on the addrs](https://kiwifarms.net/threads/ethan-ralphs-december-16th-2020-revenge-porn-arrest.81547/page-84)
- [news on the transaction](https://vosizneias.com/2021/01/21/programmer-bequeaths-500000-in-bitcoins-to-us-right-wing-groups-and-then-commits-suicide/)
- [2017 when alt-right declare bitcoin "the currency of the alt-right"](https://www.washingtonpost.com/business/technology/bitcoins-boom-is-a-boon-for-extremist-groups/2017/12/26/9ca9c124-e59b-11e7-833f-155031558ff4_story.html)
- [right-wing bitcoin tx tracker twitter account](https://twitter.com/NeonaziWallets/with_replies?lang=en); [the news](https://www.salon.com/2017/12/27/is-bitcoin-enabling-alt-right-extremists/)

### Sqlite3 query (on rpi)
1. query blocks that are after 2017.01 (result: from heihg 446033)
```
select * from block_info where timestamp like '2017-01-01%' limit 10;
```

### building applicatino with neo4j
[ref](https://neo4j.com/blog/graph-your-network-neo4j-docker-image/)

### how to handle larger data
- [use hadoop only if you have terabytes of data](https://www.chrisstucchio.com/blog/2013/hadoop_hatred.html)

### after exporting sent_to_2017.csv
1. remove the time column
2. group by sent-receive wallet and sum up the value
3. [export the grouped, sum dataframe to csv, i.e. multilevel series to csv](https://stackoverflow.com/questions/17349574/pandas-write-multiindex-rows-with-to-csv) 

