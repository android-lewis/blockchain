## To install do:

```
pip install -r requirements.txt
```

First run 

```
python wallet.py
```

Pick option 1 to generate a new wallet and update your wallet address in the mining_config.py file

Change the MINER_NODE_URL to a port on localhost that is free

Run app.py in the background

```
python app.py -p YOUR_CHOSEN_PORT
```

Now you can play with the API in Postman to mine blocks, or use the wallet.py utility to send transactions.

# Sending through the API will not work as you need to sign each transaction, this is done for you in wallet.py