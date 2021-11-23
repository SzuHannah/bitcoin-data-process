## csvToWallet
You'll need this whole folder to aggregate addresses into wallets with the transitive closure heuristic. It can be used to convert block csv files (the ones that already mapped string address to integer address) to edge csv files. And then, convert from edge csv files to a walletID csv file. Users can modify the code in driver.py to suit their needs. For detailed example and documentation, please see [this python notebook](csvToWalletExample.ipynb)