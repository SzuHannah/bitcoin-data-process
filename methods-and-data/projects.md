# Architecture design

[Figure 4](projects.md#fig4) illustrates the architecture design of the whole parser, file, and database system we used to decode the Bitcoin blockchain ledger into a simple wallet graph for analysis. The Blockchain Parser was Python-based, and it decoded the blockchain. The blockchain is encoded in bytes and split into multiple .dat files. The Parser converted bytes into readable JSONs. Each block generated one JSON file that contained information such as block height, block timestamp, block difficulty, number of transactions within the block, and detailed transaction records.

Further, each JSON was split into multiple CSV files by the CSV Parser, and we processed the JSONs (i.e. blocks) in batches. For each batch, there were thousands of blocks. This specific batch would result in: one blocks.csv that contained the information of all blocks in the batch; thousands of transactions.csvs and addresses.csvs - every block would be split into one transactions.csv and one addresses.csv, while the former recorded all transactions included in the block, the latter recorded all addresses appeared in the block. The resulting CSVs were further inserted into a SQLite database.

The addresses.csvs were uniquely imported into the database such that we created an address-ID lookup table. Originally, addresses were represented in long strings within transactions. Thus, we assigned address IDs to replace the address strings for computation efficiency. As we were not interested in the all-time transaction pattern, we let transaction tables inherit the timestamp information from block tables for later time-range filteration.

![Figure 4 Architechture design](../.gitbook/assets/Architecture-of-the-system)

The address-ID lookup table and transaction tables with mapped address IDs were then exported. We built an Edge-list Parser with Python to read in transaction tables and creat edge lists that represented the spent-together history of addresses. That is, there would be an edge between address ID = 1 and address ID = 2 if they could be spent together; thus, every transaction could produce one edge list. The Address Clusterizer then took the address-ID lookup table as an input and streamed the edge-lists through to link address-IDs into clusters of wallets. As a result, the Clusterizer would generate an addressID-walletID lookup table. The Address Clusterizer was implemented with Weighted Quick Union with Path Compression (WQUPC) algorithm that were described in the Algorithm section.

After the addressID-walletID lookup table was generated, we inserted it back into the SQLite database. Further, we mutated a walletID column and mapped the walletIDs for each transaction table. Then, the transaction tables were exported and imported into a Neo4j graph database. Every row of the transaction tables was represented in a walletID-transactionID-walletID graph illustrated in [Figure 2](projects.md#fig2). We leveraged the built-in graph database commands to merge the inputs and outputs into one edge called “sent\_to” using the heuristic described in [Figure 3](projects.md#fig3). Finally, this simplified walletID-walletID graph was used for analysis.

### Commnads for construction Neo4j database

{% tabs %}
{% tab title="run neo4j with docker" %}
```
# construct a neo4j db called bitcoindb 
docker run --name bitcoindb -p7474:7474 -p7687:7687  -d -v /scratch/bitcoin/import/neo4jContainer:/var/lib/neo4j/import  -v bitcoindbdata:/data -v bitcoindblogs:/logs -v /scratch/bitcoin/plugins:/var/lib/neo4j/plugins  --env NEO4J_AUTH=neo4j/test --env NEO4J_dbms_memory_heap_initial__size=24g --env NEO4J_dbms_memory_heap_max__size=24g --env NEO4J_dbms_memory_pagecache_size=28g --env NEO4J_apoc_export_file_enabled=true --env NEO4J_apoc_import_file_enabled=true --env NEO4J_apoc_import_file_use__neo4j__config=true --env NEO4J_dbms_security_procedures_unrestricted=apoc.*,gds.* --env NEO4J_dbms_recovery_fail__on__missing__files=false --env NEO4JLABS_PLUGINS=\[\"apoc\"\,\"graph-data-science\"\] neo4j:latest

#execute and use docker command interface
docker start bitcoindb
docker exec -it bitcoindb bash
#go to import to check data 
cd import 
```
{% endtab %}

{% tab title="import wallet-tx-wallet graph" %}

{% endtab %}

{% tab title="" %}

{% endtab %}
{% endtabs %}
