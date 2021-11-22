# Bitcoin transaction graph

Each transaction was composed of inputs and outputs. Outputs contain information such as the amount of money and the addresses that the money was sent. Inputs were references to previous unspent outputs. Thus, by extracting the address information from inputs and outputs, we can construct a directed transaction graph.

## Address-Transaction-Address Graph

Multiple input and output addresses may be involved in one transaction. As shown in [Figure 2](bitcoin-transaction-graph.md#fig2), $$t_{1}$$and $$t_{2}$$ each represents one transaction; $$t_{1}$$has $$a_{1}$$, $$a_{2}$$ as its input addresses, and $$a_{3}$$, $$a_{2}$$ as output addresses; $$t_{2}$$ has $$a_{2}$$, $$a_{4}$$ as input addresses, and $$a_{3}$$, $$a_{4}$$ as output addresses. In our transaction graph, we also included the transaction timestamp, which was inherited from the block, illustrating when the block was mined. Thus, all transactions within one specific block would have the same timestamp.

![Figure 2 Bitcoin transaction graph](../.gitbook/assets/add-tran-add-graph)

## Wallet-Wallet Graph

Every user has pairs of public key (i.e. hash of an address) and private key to engage in transactions, and the former is derived from the latter. To create one valid transaction, a sender needs to use his/her private key to redeem a yet spent output from previous transactions as the input. After collecting enough inputs (i.e. sufficient amount of bitcoins), the sender will lock them with the receiver's public key and send them to the receiver as the output. The receiver can use his/her private key to unlock this output later on.

Intuitively, we assume that one user can control the balances in his/her addresses. This mechanism allows us to cluster multiple addresses as one single wallet through running heuristics on the transaction record despite false positives. Common heuristics include Peeling Chain, Change Closure, Idioms of Use, Transitive Closure, Ip Clustering, and Temporal Clustering. In this study, we will focus on Transitive Closure.

Let $$B=\{b_{1},b_{2},...,b_{N}\}$$ be the set of blocks in the blockchain; $$T=\{t_{1},t_{2},...,t_{N}\}$$ be the set of transactions within a block, and $$T_{b_{i}}$$ defines a transaction set within block $$b_{i}$$; $$A=\{a_{1}, a_{2}, ..., a_{N}\}$$ be the set of addresses in all transactions. Therefore, transactions in [Figure 2](bitcoin-transaction-graph.md#fig2), presumably both came from $$b_{k}$$ block can be illustrated as the following: $$T_{b_{k}}=\{t_{1}(a_{1}+a_{2}a_{3}+a_{2}), t_{2}(a_{2}+a_{4}a_{3}+a_{4})\}$$.

Transitive closure is a heuristic that clusters addresses that can be spent together into one wallet. For example, in [Figure 2](#fig2), $$a_{1}$$, $$a_{2}$$ were spent together, and $$a_{2}$$, $$a_{4}$$ were spent together, and thus by transitivity, we have wallet $$W_{1}=\{a_{1}, a_{2}, a_{4}\}$$ because these three addresses can be spent together. Moreover, as we yet have information of what addresses can be spent with $$a_{3}$$ or $$a_{5}$$, they respectively form one wallet, i.e. we have $$W_{2}=\{a_{3}\}$$; $$W_{3}=\{a_{5}\}$$. [Figure 3](#fig3) is the resulting Wallet-Wallet graph derived from the Address-Transaction-Address graph in [Figure 2](#fig2).

![Figure 3 Derived wallet graph](../.gitbook/assets/wallet-wallet-graph)

If we define one user as an entity that can control the addresses, compared to the address graph, one node in the wallet graph is closer to the concept of one user in reality. Thus, the aggregation not only largely accelerates computation efficiency but it has the potential to make user transaction behavior study more interpretable.
