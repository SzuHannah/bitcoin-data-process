# Run PPR in Neo4j

To investigate the behaviors of the wallets of our interest, we leveraged the PPR algorithm described in the "Algorithms" section. In particular, we examined the downstream and upstream PPR, the former uncovered who those wallets often sent money to, while the latter helped us understand who the wallets often received money from.

Downstream PPR and upstream PPR are similar, here we would mainly illustrate the setting for the downstream PPR.

(1) create an in-memory graph that encodes SENT\_TO as SENT (for upstream, encodes SENT_TO as RECEIVE\_FROM_)&#x20;

```
//down-stream
call gds.graph.create('txgraph','Wallet','*') yield graphName, nodeCount, relationshipCount;
//up-stream
call gds.graph.create('txgraph-upstream','Wallet',{RECEIVE_FROM:{type:'SENT_TO',orientation:'REVERSE'}}) yield graphName,nodeCount,relationshipCount;`
```

(2) for eachwallet of our interest, treat it as the seed node, and run PPR with 𝛼=0.15, and iteration=20&#x20;

```
match(w:Wallet) where w.walletID in ['7480','2096025','5279538','327466217','73091417','110567775','781745','347248','155260033','168586723','178055641','183649279'] with collect(w) as seeds call gds.pageRank.stream('txgraph',{maxIterations:20,dampingFactor:0.85,sourceNodes:seeds}) yield nodeId, score return gds.util.asNode(nodeId).walletID as walletID, score order by score desc limit 30;

//if want to export to csv
with "match(w:Wallet) where w.walletID in ['7480','2096025','5279538','327466217','73091417','110567775','781745','347248','155260033','168586723','178055641','183649279'] with collect(w) as seeds call gds.pageRank.stream('txgraph',{maxIterations:20,dampingFactor:0.85,sourceNodes:seeds}) yield nodeId, score return gds.util.asNode(nodeId).walletID as walletID, score order by score desc limit 30;" as query call apoc.export.csv.query(query,"right_activist_downstreamppr.csv",{}) yield file, source, format, nodes, relationships, properties, time, rows, batchSize, batches, done, data return file, source, format, nodes, relationships, properties, time, rows, batchSize, batches, done, data;
```

(3) return wallet IDs with PPR score ranked top 10
