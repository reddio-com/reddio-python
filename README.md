# red-py-sdk

![](https://img.shields.io/pypi/pyversions/Django.svg)


### install

```
pip3 install redpysdk
```

### Usage

#### Init

```
from redpysdk import Reddio
```

Using 'testnet' or 'mainnet' to init the sdk

```
obj = Reddio("testnet")
```
#### Get Balance

```
obj.get_balances("0x6ecaebbe5b9486472d964217e5470380782823bb0d865240ba916d01636310a")
```

It will return the starkkey('0x6ecaebbe5b9486472d964217e5470380782823bb0d865240ba916d01636310a')'s balance. which including ERC20/ETH/ERC721

the function signature is `get_balances(self, stark_key, page=1, limit=10)`

#### Transfer

```
obj.transferNFT('private_key', '0x6ecaebbe5b9486472d964217e5470380782823bb0d865240ba916d01636310a', '0x1ada455b26b246260b7fd876429289639d7a0ce5fe295ff2355bd4f4da55e2', 'ERC721', '0x941661Bd1134DC7cc3D107BF006B8631F6E65Ad5', '618'))
```

you should replace the 'private_key' to the private key of the starkkey('0x6ecaebbe5b9486472d964217e5470380782823bb0d865240ba916d01636310a')
the function signature is `transferNFT(self, stark_private_key, sender_starkkey, receiver, token_type, contract, tokenID, expiration_timestamp=4194303)`


#### Withdrawal

```
obj.withdrawNFT('private_key', '0x6ecaebbe5b9486472d964217e5470380782823bb0d865240ba916d01636310a', '0xffc882996cFAB2C8B9983394E09bb025a98e52bc', 'ERC721', '0x941661Bd1134DC7cc3D107BF006B8631F6E65Ad5', '663')
```

you should replace the 'private_key' to the private key of the starkkey('0x6ecaebbe5b9486472d964217e5470380782823bb0d865240ba916d01636310a')
the function signature is `withdrawNFT(self, stark_private_key, sender_starkkey, receiver, token_type, contract, tokenID, expiration_timestamp=4194303)`





