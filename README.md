# red-py-sdk
reddio python sdk

### install
pip install -r requirements.txt

### sign transfer message
```
python3 sign.py --stark_key stark_key \
    --amount amount \
    --nonce nonce \
    --asset_id asset_id \
    --sender_vault_id sendeer_vault_id \
    --receiver_public_key receiver_public_key \
    --receiver_vault_id receiver_vault_id \
    --expiration_timestamp expiration_timestamp \
    --sender_private_key sender_private_key
```



