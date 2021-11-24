# Algorithms

### Weighted Quick Union with Path Compression (WQUPC)

The address clustering algorithm can be implemented with WQUPC, described in Algorithm 1, and the walletID assignment steps following the clustering result are illustrated in Table 1. Scripts and a python notebook example can be found [here](https://github.com/SzuHannah/bitcoin-data-process/tree/main/csvToWallet).

{% hint style="info" %}
**Appendix 1: WQUPC Algorithm**

Input requirements:

(i) An edge list that recorded addresses that were ever spent together such that we could read in the edge list to do the Union operation (e.g. if address 1 and address 2 were spent together, we will do Union(1,2))

(ii) A list that recorded the parent of each node, and a list that recorded the rank of each node

Note: p in the following procedure means parent

**pseudo-code:**

```
def Make-Set(x):
    x.p=x
    x.rank=0

def Union(x,y):
    Link(Find-Set(x),Find-Set(y))

def Link(x,y):
    if x.rank > y.rank:
        y.p=x
    else x.p=y
    if x.rank == y.rank:
        y.rank = y.rank+1

def Find-Set(x):
    if x != x.p
    x.p = Find-Set(x.p)
    return x.p
```
{% endhint %}

| Table 1 Steps of assigning wallet IDs to addresses                                                                                                                                                          |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| <p>Input requirements:</p><p>(i) An edge list that records addresses that were ever spent together</p><p>(ii) The parent record resulted from the WQUPC Algorithm</p>                                       |
| <p>Step 1: read in edge list and run WQUPC algorithm on all addresses</p><p>Step 2: Use the parent record to find the root for each address</p><p>Step 3: Export the root as wallet ID for each address</p> |

### Approximated Personalized PageRank (PPR)

One way to study entities' transaction behavior is through investigating upstream/downstream critical wallets for those famous wallets in the transaction network. This is equivalent to finding vertices that are most relevant to a specific node in a graph. This kind of problem setup is one of the applications for Personalized PageRank (PPR). As the bitcoin transaction network is large, and running PPR on the whole graph would be inefficient, we adopted a faster modification of PPR, the approximate PPR algorithm\[^1], to solve the problem.

{% hint style="info" %}
**Algorithm 2: Approximate Personalized PageRank Algorithm**

Input requirement: undirected graph G, PPR vector $$p \in [0,1]^{N}$$, preference vector 𝜋, teleportation constant 𝛼, and tolerance 𝜀

**pseudo-code:**

**Initialize **$$p \leftarrow 0$$, $$r \leftarrow \pi$$, $$\alpha' \leftarrow \alpha/(2-\alpha)$$

**while **$$\exists u \in V$$such that $$r_{u} \geq \epsilon d_{u}$$ **do**

&#x20;   uniformly sample a vertex u satisfying $$r_{u} \geq \epsilon d_{u}$$

&#x20;   $$p_{u} \leftarrow p_{u} + \alpha' r_{u}$$****

**     for** $$v:(u,v) \in E$$ do

&#x20;       $$r_{u} \leftarrow r_{v} + (1-\alpha')r_{u}/2d_{u}$$​

**     end for**

&#x20;   $$r_{u} \leftarrow (1-\alpha')r_{u}/2$$

**end while**

**return** $$\epsilon-$$approximate PPR vector $$p$$
{% endhint %}

\[^1]: Chen, F., Zhang, Y. and Rohe, K. (2020), Targeted sampling from massive block model graphs with personalized PageRank. J. R. Stat. Soc. B, 82: 99-126. https://doi.org/10.1111/rssb.12349
