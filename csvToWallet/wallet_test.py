from wallet import Wallet

walletstrcsv="walletstr_test.csv"
walletcsv="wallet_test.csv"

w=Wallet(walletstrcsv,walletcsv)
w.constructWalletCSV()
