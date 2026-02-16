# `libfiu` usage on Bitcoin Core


This page describes how to use `libfiu` to inject faults into Bitcoin Core for testing purposes, on ubuntu.

## Steps

Install `libfiu`

```
sudo apt-get install libfiu-dev fiu-utils
```

Download a released bitcoin core

```
wget https://bitcoincore.org/bin/bitcoin-core-30.2/bitcoin-30.2-x86_64-linux-gnu.tar.gz
tar -xzf bitcoin-30.2-x86_64-linux-gnu.tar.gz
```

Using the mainnet or any regular testnet means there will be too many blocks. Use a regtest instead.

Also, we need two nodes. One `generator` and one `victim`. The `generator` will generate blocks and the `victim` will be the one we inject faults into.

First start the good node, the `generator`:
```
rm -rf /tmp/node_generator /tmp/node_victim
mkdir -p /tmp/node_generator /tmp/node_victim
./bitcoin-30.2/bin/bitcoind -regtest -datadir=/tmp/node_generator -port=18444 -bind=127.0.0.1 -daemon
```


Generate some blocks. Helper alias for the generator node's cli:
```
alias cli_gen="./bitcoin-30.2/bin/bitcoin-cli -regtest -datadir=/tmp/node_generator"
```

Create a wallet to mine into
```
cli_gen createwallet "miner"
cli_gen -rpcwallet="miner" getnewaddress
```

Generate 150 blocks (enough to make the chain active and spendable)
```
cli_gen -rpcwallet="miner" generatetoaddress 150 $(cli_gen -rpcwallet="miner" getnewaddress)
```

Launch victim node, connectiong only to the generator node:
```
fiu-run -x -c "enable_random name=posix/io/*,probability=0.005" \
./bitcoin-30.2/bin/bitcoind \
  -regtest \
  -datadir=/tmp/node_victim \
  -connect=127.0.0.1:18444 \
  -port=18445 \
  -rpcport=18446
```

Check if it started
```
./bitcoin-30.2/bin/bitcoin-cli -regtest -datadir=/tmp/node_victim -rpcport=18446 getblockchaininfo
```


Generate more blocks on the generator node, and see if the victim node can keep up with the chain:
```
cli_gen -rpcwallet="miner" generatetoaddress 10 $(cli_gen -rpcwallet="miner" getnewaddress)
```


#### Restart the victim node

Restart the victim node after we have mined some blocks, and see if it can sync up with the chain:
```
pkill -F /tmp/node_victim/regtest/bitcoind.pid 2>/dev/null
sleep 1
rm -rf /tmp/node_victim/*
fiu-run -x -c "enable_random name=posix/io/*,probability=0.01" \
./bitcoin-30.2/bin/bitcoind \
  -regtest \
  -datadir=/tmp/node_victim \
  -connect=127.0.0.1:18444 \
  -port=18445 \
  -rpcport=18446 \
  -daemon
```

tail the log
```
tail -f /tmp/node_victim/regtest/debug.log
```
