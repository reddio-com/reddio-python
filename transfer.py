def transferNFT(sender_starkkey,stark_private_key, receiver, token_type, contract, tokenID, expiration_timestamp=4194303):
    quantum = 1
    asset_id =  hex(get_asset_id(token_type, contract, quantum, tokenID))
    vault_id = get_vault_id(sender_starkkey, asset_id)
    receiver_vault_id = get_vault_id(receiver, asset_id)
    nonce = get_nonce(sender_starkkey)
    data = {}
    data['asset_id'] = str(asset_id)
    data['receiver_vault_id'] = str(receiver_vault_id)
    data['sender_vault_id'] = str(vault_id)
    data['nonce'] = str(nonce)
    data['sender_private_key'] = str(stark_private_key)
    data['amount'] = "1"
    data['receiver'] = str(receiver)
    data['expiration_timestamp'] = str(expiration_timestamp)
    data['stark_key'] = str(sender_starkkey)

    transfer_data = get_transfer_data(data)

    url = REDDIO_ENDPOIT + '/v1/transfers'
    headers = {'Content-Type': 'application/json'}
    x = request(url, transfer_data, headers)
    return x.json()

def withdrawNFT(sender_starkkey,stark_private_key, receiver, token_type, contract, tokenID, expiration_timestamp=4194303):
    quantum = 1
    asset_id =  hex(get_asset_id(token_type, contract, quantum, tokenID))
    vault_id = get_vault_id(sender_starkkey, asset_id)
    receiver_vault_id = get_vault_id(receiver, asset_id)
    nonce = get_nonce(sender_starkkey)
    data = {}
    data['asset_id'] = str(asset_id)
    data['receiver_vault_id'] = str(receiver_vault_id)
    data['sender_vault_id'] = str(vault_id)
    data['nonce'] = str(nonce)
    data['sender_private_key'] = str(stark_private_key)
    data['amount'] = "1"
    data['receiver'] = str(receiver)
    data['expiration_timestamp'] = str(expiration_timestamp)
    data['stark_key'] = str(sender_starkkey)

    transfer_data = get_transfer_data(data)

    url = REDDIO_ENDPOIT + '/v1/withdrawalto'
    headers = {'Content-Type': 'application/json'}
    x = request(url, transfer_data, headers)
    return x.json()

def balance():
    pass