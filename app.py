import streamlit as st
import requests, json
from web3 import Web3
import pandas as pd
import os
from os.path import join, dirname
from dotenv import load_dotenv
from Crypto.Hash import keccak
import time
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
OPENSEA_CONTRACT = '0x7f268357a8c2552623316e2562d90e642bb538e5'
WETH_CONTRACT = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
TRANSFER_METHOD = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'


def render_asset(asset):
    if asset['name'] is not None:
        st.subheader(asset['name'])
    else:
        st.subheader(f"{asset['collection']['name']} #{asset['token_id']}")

    if asset['description'] is not None:
        st.write(asset['description'])
    else:
        st.write(asset['collection']['description'])

    if asset['image_url'].endswith('mp4') or asset['image_url'].endswith('mov'):
        st.video(asset['image_url'])
    elif asset['image_url'].endswith('svg'):
        svg = requests.get(asset['image_url']).content.decode()
        st.image(svg)
    elif asset['image_url']:
        st.image(asset['image_url'])


def get_transaction_receipt(txn):
    url = 'https://api.etherscan.io/api'
    params = {
        'module': 'proxy',
        'action': 'eth_getTransactionReceipt',
        'apikey': os.environ.get("ETHERSCAN_KEY"),
        'txhash' : txn['transactionHash']
    }
    r = requests.get(url, params=params)
    try:
        json_data = json.loads(r.text)["result"]
        return json_data
    except:
        return None


def determine_currency(txn):
    # mentioned earlier function
    transaction_receipt = get_transaction_receipt(txn) 
    
    currency = 'ETH'

    # OrdersMatched will always be the last element in receipt array
    price_hex = transaction_receipt['logs'][-1]['data'][-64:]
    for s in transaction_receipt['logs']:
        if s['topics'][0] == TRANSFER_METHOD:
              # check if price in Transfer event parameters
            if price_hex in s['data']:
                  # additional check if currenct is Wrapped ETH
                if s['address'] == WETH_CONTRACT:
                    currency = 'WETH'
                else:
                    currency = 'NONETH-' +s['address']

    return currency

def determine_collection_contract(txn):
    transaction_receipt = get_transaction_receipt(txn) 
    if transaction_receipt is None:
        return
    price_hex = transaction_receipt['logs'][-1]['data'][-64:]
    collection_contract = ''
    for s in transaction_receipt['logs']:
        if (s['topics'][0] == TRANSFER_METHOD):
            if price_hex not in s['data']:
                collection_contract = s['address']
        
    return collection_contract

def get_collection_name(contract_adress):
    url = 'https://blockscout.com/eth/mainnet/api'
    params = {
        'module' : 'token',
        'action' : 'getToken',
        'contractaddress' : contract_adress
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        json_data = json.loads(r.text)
        if (json_data != None) and (json_data['message'] == 'OK'):
            return json_data['result']['symbol']
        else:
            return "None"
    else:
        return "None"


def test():
    url = 'https://api.etherscan.io/api'

    params = {
    'module': 'block',
    'action': 'getblocknobytime',
    'timestamp' : int(time.time() // 1),
    'closest': 'before',
    'apikey': os.environ.get("ETHERSCAN_KEY")
    }
    r = requests.get(url, params=params)
    json_data = json.loads(r.text)["result"]

    LATEST_BLOCK = int(json_data)
    print(f"LATEST_BLOCK: {LATEST_BLOCK}")
    params = {
    'module': 'logs',
    'action': 'getLogs',
    'fromBlock' : LATEST_BLOCK - 10,
    'toBlock': 'latest',
    'address': OPENSEA_CONTRACT,
    'apikey': os.environ.get("ETHERSCAN_KEY")
    }
    r = requests.get(url, params=params)
    json_data = json.loads(r.text)['result']


    method = b'OrdersMatched(bytes32,bytes32,address,address,uint256,bytes32)'
    k = keccak.new(digest_bits=256)
    k.update(method)
    OrdersMatchedSig = '0x'+k.hexdigest()

    DIVIDER = 10**18

    transactions_processed = []
    for tr in json_data:
        result = {}
        # print(tr)
        # print(get_transaction_receipt(tr))
        if tr['topics'][0] == OrdersMatchedSig:
            result['maker'] = '0x' + (tr['topics'][1])[26:]
            result['txn_hash'] = tr['transactionHash']
            result['taker'] = '0x' + (tr['topics'][2])[26:]
            result['price'] = int('0x' + tr['data'][-32:], 16) / DIVIDER       
            result['collection'] = get_collection_name(determine_collection_contract(tr))
            if result['collection'] is None:
                continue
       
            transactions_processed.append(result)

    print(transactions_processed)
    with open('app.json', 'w', encoding='utf-8') as f:
        json.dump(transactions_refactored, f)


def main():
    # # Page setup
    # st.set_page_config(
    #     page_title="NFT Data - Project2",
    #     page_icon="🧊",
    #     layout="wide",
    #     initial_sidebar_state="expanded",
    # )
    # st.sidebar.header("Pages")
    # page_choices = ['Asset Explorer', 'Analysis']
    # page = st.sidebar.selectbox("Choose a Page", page_choices)
    # st.title(f"Project 2 - {page}")



    # if page == 'Asset Explorer':
    #     st.sidebar.header('Filters')
    #     owner = st.sidebar.text_input("Owner")
    #     collection = st.sidebar.text_input("Collection")
    #     params = {'owner': owner}
    #     if collection:
    #         params['collection'] = collection

    #     if len(owner) > 0:
    #         r = requests.get(f"https://api.opensea.io/api/v1/assets?collection={collection}&owner={owner}", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'})

    #         assets = r.json()['assets']
    #         for asset in assets:                
    #             render_asset(asset)

    #         st.subheader("Raw JSON Data")
    #         st.write(r.json())
    #     else:
    #         st.write("Put in some fields")


    test()




if __name__ == '__main__':
    main()