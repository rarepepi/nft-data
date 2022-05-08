import streamlit as st
import requests, json
from web3 import Web3
import pandas as pd
import os
from os.path import join, dirname
from dotenv import load_dotenv
from Crypto.Hash import keccak
from time import time
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

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


def test():
    OPENSEA_CONTRACT = '0x7Be8076f4EA4A4AD08075C2508e481d6C946D12b'
    url = '<https://api.etherscan.io/api>'
    params = {
    'module': 'logs',
    'action': 'getLogs',
    'fromBlock' : BLOCK_START,
    'toBlock': 'latest',
    'address': OPENSEA_CONTRACT,
    'apikey': API_KEY
    }
    r = requests.get(url, params=params)
    json_data = json.loads(r.text)["result"]

    params = {
    'module': 'block',
    'action': 'getblocknobytime',
    'timestamp' : int(time.time() // 1),
    'closest': 'before',
    'apikey': API_KEY
    }
    r = requests.get(url, params=params)
    json_data = json.loads(r.text)["result"]
    LATEST_BLOCK = int(json_data)

    method = b'OrdersMatched(bytes32,bytes32,address,address,uint256,bytes32)'

    k = keccak.new(digest_bits=256)
    k.update(method)


def main():
    # Page setup
    st.set_page_config(
        page_title="NFT Data - Project2",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.sidebar.header("Pages")
    page_choices = ['Asset Explorer', 'Analysis']
    page = st.sidebar.selectbox("Choose a Page", page_choices)
    st.title(f"Project 2 - {page}")



    if page == 'Asset Explorer':
        st.sidebar.header('Filters')
        owner = st.sidebar.text_input("Owner")
        collection = st.sidebar.text_input("Collection")
        params = {'owner': owner}
        if collection:
            params['collection'] = collection

        if len(owner) > 0:
            r = requests.get(f"https://api.opensea.io/api/v1/assets?collection={collection}&owner={owner}", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'})

            assets = r.json()['assets']
            for asset in assets:                
                render_asset(asset)

            st.subheader("Raw JSON Data")
            st.write(r.json())
        else:
            st.write("Put in some fields")




if __name__ == '__main__':
    main()