import requests
import logging

from settings import REDDIO_ENDPOIT

from http_utils import request
from starkex_utils import get_signature_local,get_asset_id


def get_vault_id(stark_key, assetid):
    data = {"asset_id":assetid, "stark_keys": stark_key}
    headers = {'Content-Type': 'application/json'}
    r = requests.get(url = '%s/v1/vaults' % REDDIO_ENDPOIT, params = data, headers = headers)
    vault_id = r.json()['data']['vault_ids'][0]
    return vault_id

def get_order_info(stark_key, contract1Type, contract1Address, contract1TokenID, contract2Type, contract2Address, contract2TokenID):
    uri = '/v1/order/info' + '?stark_key=' + str(stark_key) + '&contract1=' + str(contract1Type) + ':' + str(contract1Address) + ':' + str(contract1TokenID) + '&contract2=' + str(contract2Type) + ':' + str(contract2Address) + ':' + str(contract2TokenID)
    url = REDDIO_ENDPOIT + uri
    headers = {'Content-Type': 'application/json'}
    r = requests.get(url, headers = headers)
    return r.json()['data']


def get_balances(stark_key, page=1, limit=10):
    uri = '/v1/balances' + '?stark_key=' + str(stark_key) + '&page=' + str(page) + '&limit=' + str(limit)
    url = REDDIO_ENDPOIT + uri
    headers = {'Content-Type': 'application/json', "User-Agent":"ReddioFrame"}
    r = requests.get(url, headers = headers)
    return r.json()["data"]["list"]

def get_orders(contract_address):
    uri = '/v1/orders' + '?contract_address=' + str(contract_address)
    url = REDDIO_ENDPOIT + uri
    headers = {'Content-Type': 'application/json'}
    r = requests.get(url, headers = headers)
    order_list = []
    for order in r.json()["data"]["list"]:
        if order["stark_key"] != "":
            order_list.append(order)
    return order_list

def list_nft_by_user(stark_key, contract_address):
    uri = '/v1/balances' + '?stark_key=' + str(stark_key) + '&contract_address=' + str(contract_address) + '&limit=1000'
    url = REDDIO_ENDPOIT + uri
    headers = {'Content-Type': 'application/json'}
    r = requests.get(url, headers = headers)
    return r.json()["data"]["list"]

def list_user_nfts(stark_key, contract_address):
    nfts = list_nft_by_user(stark_key, contract_address)
    nft_list = []
    for nft in nfts:
        if nft["balance_available"] > 0 and int(nft["token_id"]) > 668:
            nft_list.append(nft)
    return nft_list

def get_nonce(stark_key):
    """
    Gets the nonce for a given stark key.
    """
    data = {"stark_key": stark_key}
    headers = {'Content-Type': 'application/json'}
    r = requests.get(url = '%s/v1/nonce' % REDDIO_ENDPOIT , params = data, headers = headers)
    return r.json()['data']['nonce']

def get_transfer_data(data):
    r, s = get_signature_local(data)
    original_transfer_data = {}
    original_transfer_data['amount'] = data['amount']
    original_transfer_data['nonce'] = int(data['nonce'])
    original_transfer_data['vault_id'] = data['sender_vault_id']
    original_transfer_data['receiver_vault_id'] = data['receiver_vault_id']
    original_transfer_data['stark_key'] = data["stark_key"]
    original_transfer_data['receiver'] = data["receiver"]
    original_transfer_data['signature'] = {"r": r, "s": s}
    original_transfer_data['asset_id'] = data['asset_id']
    original_transfer_data['expiration_timestamp'] = int(data['expiration_timestamp'])
    return original_transfer_data
if __name__ == "__main__":
    print(get_balances("0x6ecaebbe5b9486472d964217e5470380782823bb0d865240ba916d01636310a"))