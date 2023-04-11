use std::str::FromStr;

use bitcoin::{secp256k1, PublicKey, PrivateKey};
use secp256k1::SecretKey;

fn main() {


    let key = SecretKey::from_str("0000000000000000000000000000000000000000000000000000000000000001").unwrap();
    let priv: PrivateKey = PrivateKey::new(key, bitcoin::Network::Bitcoin);
    let pub: PublicKey = priv.public_key()
    println!("{}", key.to_bytes())
}
