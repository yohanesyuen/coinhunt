from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey

target = '1CfZWK1QTQE3eS9qn61dQjV89KDjZzfNcv'

def get_address(exp=1):
    priv = PrivateKey(secret_exponent = exp)
    pub = priv.get_public_key()
    address = pub.get_address()
    return (priv.to_wif(compressed=True), address.to_string())

def search_range(start, end):
    setup('mainnet')
    for i in range(start, end):
        wif, pub = get_address(i)
        if pub == target:
            return {
                'status': 'Found',
                'wif': wif,
                'pub': pub,
            }
    return {
        'status': 'Not found',
        'start': start,
        'end': end
    }