---
name: crypto-wallet
version: 1.0.0
description: Multi-chain blockchain wallet operations — read balances, token holdings, transaction history for EVM chains (Ethereum, Polygon, Base, Arbitrum) and Solana. Supports ENS/SNS resolution, gas estimation, and portfolio tracking.
tags: [crypto, blockchain, ethereum, solana, web3, defi, wallet, evm, polygon, base]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Crypto Wallet Skill

## Setup

```bash
# EVM chains
pip install web3 python-dotenv requests

# Solana
pip install solders solana

# Multi-chain portfolio
pip install web3 solders requests pandas
```

`.env`:
```
ETHEREUM_RPC=https://mainnet.infura.io/v3/YOUR_KEY
POLYGON_RPC=https://polygon-mainnet.infura.io/v3/YOUR_KEY
BASE_RPC=https://mainnet.base.org
ARBITRUM_RPC=https://arb1.arbitrum.io/rpc
ALCHEMY_KEY=your_alchemy_key
ETHERSCAN_API_KEY=your_etherscan_key
```

## EVM Chain Setup

```python
from web3 import Web3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Chain configurations
CHAINS = {
    "ethereum": {
        "rpc": os.getenv("ETHEREUM_RPC", "https://eth.llamarpc.com"),
        "chain_id": 1,
        "native": "ETH",
        "explorer_api": "https://api.etherscan.io/api",
        "explorer_key": os.getenv("ETHERSCAN_API_KEY", ""),
        "symbol": "ETH"
    },
    "polygon": {
        "rpc": os.getenv("POLYGON_RPC", "https://polygon.llamarpc.com"),
        "chain_id": 137,
        "native": "MATIC",
        "explorer_api": "https://api.polygonscan.com/api",
        "explorer_key": os.getenv("POLYGONSCAN_API_KEY", ""),
        "symbol": "MATIC"
    },
    "base": {
        "rpc": os.getenv("BASE_RPC", "https://mainnet.base.org"),
        "chain_id": 8453,
        "native": "ETH",
        "explorer_api": "https://api.basescan.org/api",
        "explorer_key": os.getenv("BASESCAN_API_KEY", ""),
        "symbol": "ETH"
    },
    "arbitrum": {
        "rpc": os.getenv("ARBITRUM_RPC", "https://arb1.arbitrum.io/rpc"),
        "chain_id": 42161,
        "native": "ETH",
        "explorer_api": "https://api.arbiscan.io/api",
        "explorer_key": os.getenv("ARBISCAN_API_KEY", ""),
        "symbol": "ETH"
    }
}

def get_web3(chain: str = "ethereum") -> Web3:
    """Get a Web3 connection for any EVM chain."""
    rpc = CHAINS[chain]["rpc"]
    w3 = Web3(Web3.HTTPProvider(rpc))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to {chain} RPC: {rpc}")
    return w3
```

## Native Token Balances

```python
def get_native_balance(address: str, chain: str = "ethereum") -> dict:
    """Get native token balance (ETH, MATIC, etc.)."""
    w3 = get_web3(chain)
    checksum = Web3.to_checksum_address(address)
    balance_wei = w3.eth.get_balance(checksum)
    balance = w3.from_wei(balance_wei, "ether")
    
    return {
        "chain": chain,
        "address": address,
        "balance": float(balance),
        "symbol": CHAINS[chain]["symbol"]
    }

def get_balances_all_chains(address: str) -> list[dict]:
    """Get native balance across all configured chains."""
    results = []
    for chain in CHAINS:
        try:
            bal = get_native_balance(address, chain)
            if bal["balance"] > 0:
                results.append(bal)
        except Exception as e:
            results.append({"chain": chain, "error": str(e)})
    return results
```

## ERC-20 Token Balances

```python
# Minimal ERC-20 ABI
ERC20_ABI = [
    {"inputs": [{"name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
]

def get_token_balance(wallet_address: str, token_address: str, chain: str = "ethereum") -> dict:
    """Get an ERC-20 token balance."""
    w3 = get_web3(chain)
    token = w3.eth.contract(
        address=Web3.to_checksum_address(token_address),
        abi=ERC20_ABI
    )
    
    balance_raw = token.functions.balanceOf(Web3.to_checksum_address(wallet_address)).call()
    decimals = token.functions.decimals().call()
    symbol = token.functions.symbol().call()
    name = token.functions.name().call()
    
    balance = balance_raw / (10 ** decimals)
    
    return {
        "token": name,
        "symbol": symbol,
        "address": token_address,
        "balance": balance,
        "chain": chain
    }

# Common token addresses (Ethereum mainnet)
COMMON_TOKENS = {
    "USDC":  "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "USDT":  "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "WETH":  "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "DAI":   "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "LINK":  "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "UNI":   "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
}
```

## Transaction History via Etherscan API

```python
def get_transactions(address: str, chain: str = "ethereum", limit: int = 20) -> list[dict]:
    """Get recent transactions from Etherscan-compatible explorer."""
    config = CHAINS[chain]
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": limit,
        "sort": "desc",
        "apikey": config["explorer_key"]
    }
    
    response = requests.get(config["explorer_api"], params=params)
    data = response.json()
    
    if data["status"] != "1":
        return []
    
    txs = []
    for tx in data["result"]:
        txs.append({
            "hash": tx["hash"],
            "from": tx["from"],
            "to": tx["to"],
            "value_eth": float(tx["value"]) / 1e18,
            "timestamp": tx["timeStamp"],
            "status": "✅" if tx["isError"] == "0" else "❌",
            "gas_used": tx["gasUsed"],
        })
    return txs

def get_token_transfers(address: str, chain: str = "ethereum", limit: int = 20) -> list[dict]:
    """Get ERC-20 token transfer history."""
    config = CHAINS[chain]
    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "page": 1,
        "offset": limit,
        "sort": "desc",
        "apikey": config["explorer_key"]
    }
    
    response = requests.get(config["explorer_api"], params=params)
    data = response.json()
    
    if data["status"] != "1":
        return []
    
    transfers = []
    for tx in data["result"]:
        decimals = int(tx["tokenDecimal"])
        transfers.append({
            "hash": tx["hash"],
            "token": tx["tokenSymbol"],
            "from": tx["from"],
            "to": tx["to"],
            "amount": int(tx["value"]) / (10 ** decimals),
            "timestamp": tx["timeStamp"],
        })
    return transfers
```

## ENS Name Resolution

```python
def resolve_ens(name: str, chain: str = "ethereum") -> str:
    """Resolve an ENS name to an address (e.g., 'vitalik.eth')."""
    w3 = get_web3(chain)
    return w3.ens.address(name)

def reverse_ens(address: str, chain: str = "ethereum") -> str:
    """Get ENS name for an address (reverse lookup)."""
    w3 = get_web3(chain)
    return w3.ens.name(address)
```

## Gas Estimation

```python
def get_gas_prices(chain: str = "ethereum") -> dict:
    """Get current gas prices."""
    w3 = get_web3(chain)
    gas_price_wei = w3.eth.gas_price
    gas_price_gwei = w3.from_wei(gas_price_wei, "gwei")
    
    # Estimate cost of common operations at current gas price
    eth_transfer_gas = 21000
    token_transfer_gas = 65000
    uniswap_swap_gas = 150000
    
    eth_price_usd = get_eth_price_usd()  # optional
    
    def cost_usd(gas_units):
        eth_cost = float(gas_price_gwei) * gas_units * 1e-9
        return eth_cost * eth_price_usd if eth_price_usd else None
    
    return {
        "gas_price_gwei": float(gas_price_gwei),
        "eth_transfer": {"gas": eth_transfer_gas, "cost_usd": cost_usd(eth_transfer_gas)},
        "token_transfer": {"gas": token_transfer_gas, "cost_usd": cost_usd(token_transfer_gas)},
        "uniswap_swap": {"gas": uniswap_swap_gas, "cost_usd": cost_usd(uniswap_swap_gas)},
    }

def get_eth_price_usd() -> float:
    """Get ETH price in USD from Coingecko (no API key needed)."""
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd", timeout=5)
        return r.json()["ethereum"]["usd"]
    except:
        return None
```

## Solana Wallet

```python
from solders.pubkey import Pubkey
from solana.rpc.api import Client as SolanaClient

SOLANA_RPC = "https://api.mainnet-beta.solana.com"

def get_sol_balance(address: str) -> dict:
    """Get SOL balance for a Solana wallet."""
    client = SolanaClient(SOLANA_RPC)
    pubkey = Pubkey.from_string(address)
    result = client.get_balance(pubkey)
    balance_sol = result.value / 1e9  # lamports to SOL
    return {"address": address, "balance": balance_sol, "symbol": "SOL", "chain": "solana"}

def get_spl_tokens(address: str) -> list[dict]:
    """Get SPL token balances using Solana RPC."""
    client = SolanaClient(SOLANA_RPC)
    pubkey = Pubkey.from_string(address)
    
    result = client.get_token_accounts_by_owner_json_parsed(
        pubkey,
        opts={"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}
    )
    
    tokens = []
    for account in result.value:
        info = account.account.data.parsed["info"]
        mint = info["mint"]
        amount = info["tokenAmount"]
        if float(amount["uiAmount"] or 0) > 0:
            tokens.append({
                "mint": mint,
                "amount": amount["uiAmount"],
                "decimals": amount["decimals"],
            })
    return tokens
```

## Portfolio Summary

```python
def get_portfolio_summary(address: str) -> dict:
    """Get a complete portfolio overview across all EVM chains + Solana."""
    portfolio = {"address": address, "chains": {}, "total_usd": 0}
    eth_price = get_eth_price_usd() or 0
    
    # EVM chains
    for chain in CHAINS:
        try:
            bal = get_native_balance(address, chain)
            usd = bal["balance"] * eth_price if eth_price else 0
            portfolio["chains"][chain] = {
                "native_balance": bal["balance"],
                "symbol": bal["symbol"],
                "usd_value": usd
            }
            portfolio["total_usd"] += usd
        except:
            pass
    
    # Solana
    try:
        sol_balance = get_sol_balance(address)
        sol_price = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd").json().get("solana", {}).get("usd", 0)
        portfolio["chains"]["solana"] = {
            "native_balance": sol_balance["balance"],
            "symbol": "SOL",
            "usd_value": sol_balance["balance"] * sol_price
        }
        portfolio["total_usd"] += portfolio["chains"]["solana"]["usd_value"]
    except:
        pass
    
    return portfolio
```

## References
- [Web3.py](https://web3py.readthedocs.io/) — Python EVM library
- [Etherscan API](https://docs.etherscan.io/) — Transaction history
- [Solana Python SDK](https://michaelhly.github.io/solana-py/) — Solana integration
- [CoinGecko API](https://www.coingecko.com/en/api) — Free price feeds
- [Alchemy](https://www.alchemy.com/) — Premium RPC provider
- [Public RPC endpoints](https://chainlist.org/) — Free RPC list
