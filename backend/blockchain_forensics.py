import requests
from web3 import Web3
from typing import Dict, List, Any
from datetime import datetime, timedelta
from config import ETHERSCAN_API_KEY, RPC_URL

class BlockchainForensics:
    """Forensic analysis of on-chain data"""
    
    def _init_(self):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        self.etherscan_base = "https://api.etherscan.io/api"
    
    def trace_funds(self, address: str, tx_hash: str = None) -> Dict[str, Any]:
        """Trace fund movements from an address"""
        if tx_hash:
            # Trace specific transaction
            return self._trace_transaction(tx_hash)
        else:
            # Trace all fund movements
            return self._trace_address_funds(address)
    
    def _trace_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Deep dive into a specific transaction"""
        try:
            # Get transaction details
            tx = self.w3.eth.get_transaction(tx_hash)
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            # Decode logs
            decoded_logs = self._decode_logs(receipt['logs'])
            
            # Get internal transactions
            internal_txs = self._get_internal_transactions(tx_hash)
            
            # Analyze gas usage
            gas_analysis = {
                'gas_used': receipt['gasUsed'],
                'gas_price': tx['gasPrice'],
                'total_cost_wei': receipt['gasUsed'] * tx['gasPrice'],
                'total_cost_eth': Web3.from_wei(receipt['gasUsed'] * tx['gasPrice'], 'ether')
            }
            
            return {
                'transaction': {
                    'hash': tx_hash,
                    'from': tx['from'],
                    'to': tx['to'],
                    'value': str(Web3.from_wei(tx['value'], 'ether')),
                    'block': tx['blockNumber']
                },
                'status': 'Success' if receipt['status'] == 1 else 'Failed',
                'logs': decoded_logs,
                'internal_transactions': internal_txs,
                'gas_analysis': gas_analysis
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _trace_address_funds(self, address: str) -> Dict[str, Any]:
        """Trace all fund movements for an address"""
        # Get transaction history
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'sort': 'desc',
            'apikey': ETHERSCAN_API_KEY
        }
        
        response = requests.get(self.etherscan_base, params=params)
        transactions = response.json().get('result', [])[:100]  # Last 100 txs
        
        # Analyze fund flow
        total_in = 0
        total_out = 0
        unique_interactors = set()
        
        for tx in transactions:
            value = int(tx['value'])
            if tx['to'].lower() == address.lower():
                total_in += value
                unique_interactors.add(tx['from'])
            else:
                total_out += value
                unique_interactors.add(tx['to'])
        
        # Get current balance
        current_balance = self.w3.eth.get_balance(address)
        
        return {
            'address': address,
            'current_balance_eth': str(Web3.from_wei(current_balance, 'ether')),
            'total_received_eth': str(Web3.from_wei(total_in, 'ether')),
            'total_sent_eth': str(Web3.from_wei(total_out, 'ether')),
            'unique_addresses_interacted': len(unique_interactors),
            'transaction_count': len(transactions),
            'first_transaction': transactions[-1]['timeStamp'] if transactions else None,
            'last_transaction': transactions[0]['timeStamp'] if transactions else None
        }
    
    def detect_suspicious_patterns(self, address: str) -> List[Dict[str, Any]]:
        """Detect suspicious transaction patterns"""
        suspicious_patterns = []
        
        # Get recent transactions
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'sort': 'desc',
            'apikey': ETHERSCAN_API_KEY
        }
        
        response = requests.get(self.etherscan_base, params=params)
        transactions = response.json().get('result', [])[:500]
        
        # Pattern 1: Rapid transactions (possible bot)
        rapid_txs = self._detect_rapid_transactions(transactions)
        if rapid_txs:
            suspicious_patterns.append({
                'type': 'Rapid Transactions',
                'severity': 'Medium',
                'description': f'Found {len(rapid_txs)} transactions within 1 minute',
                'evidence': rapid_txs[:5]  # First 5 examples
            })
        
        # Pattern 2: Round number transfers (possible mixing)
        round_transfers = self._detect_round_transfers(transactions)
        if round_transfers:
            suspicious_patterns.append({
                'type': 'Round Number Transfers',
                'severity': 'Low',
                'description': f'Found {len(round_transfers)} transfers with round amounts',
                'evidence': round_transfers[:5]
            })
        
        # Pattern 3: Contract creation followed by immediate drain
        drain_pattern = self._detect_drain_pattern(transactions)
        if drain_pattern:
            suspicious_patterns.append({
                'type': 'Possible Rug Pull',
                'severity': 'Critical',
                'description': 'Contract creation followed by fund extraction',
                'evidence': drain_pattern
            })
        
        return suspicious_patterns
    
    def _detect_rapid_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Detect transactions occurring in rapid succession"""
        rapid_txs = []
        
        for i in range(len(transactions) - 1):
            time_diff = int(transactions[i]['timeStamp']) - int(transactions[i+1]['timeStamp'])
            if time_diff < 60:  # Less than 1 minute
                rapid_txs.append({
                    'tx1': transactions[i]['hash'],
                    'tx2': transactions[i+1]['hash'],
                    'time_diff_seconds': time_diff
                })
        
        return rapid_txs
    
    def _detect_round_transfers(self, transactions: List[Dict]) -> List[Dict]:
        """Detect transfers with suspiciously round numbers"""
        round_transfers = []
        
        for tx in transactions:
            value_eth = Web3.from_wei(int(tx['value']), 'ether')
            if value_eth > 0 and value_eth == int(value_eth):  # Whole number ETH
                round_transfers.append({
                    'hash': tx['hash'],
                    'value_eth': str(value_eth),
                    'to': tx['to']
                })
        
        return round_transfers
    
    def _detect_drain_pattern(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Detect contract creation followed by drain"""
        # Look for contract creation
        creation_tx = None
        for tx in transactions:
            if tx['to'] == '':  # Contract creation
                creation_tx = tx
                break
        
        if not creation_tx:
            return None
        
        # Look for large withdrawals after creation
        creation_time = int(creation_tx['timeStamp'])
        drain_txs = []
        
        for tx in transactions:
            if int(tx['timeStamp']) > creation_time and int(tx['value']) > 0:
                drain_txs.append(tx)
        
        if drain_txs:
            total_drained = sum(int(tx['value']) for tx in drain_txs)
            return {
                'creation_tx': creation_tx['hash'],
                'drain_transactions': len(drain_txs),
                'total_drained_eth': str(Web3.from_wei(total_drained, 'ether'))
            }
        
        return None
    
    def _decode_logs(self, logs: List[Dict]) -> List[Dict]:
        """Decode event logs"""
        decoded_logs = []
        
        for log in logs:
            decoded = {
                'address': log['address'],
                'topics': log['topics'],
                'data': log['data']
            }
            
            # Common event signatures
            if log['topics']:
                topic0 = log['topics'][0].hex()
                
                # Transfer event
                if topic0 == '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
                    decoded['event'] = 'Transfer'
                    if len(log['topics']) >= 3:
                        decoded['from'] = '0x' + log['topics'][1].hex()[26:]
                        decoded['to'] = '0x' + log['topics'][2].hex()[26:]
                # Approval event
                elif topic0 == '0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925':
                    decoded['event'] = 'Approval'
                else:
                    decoded['event'] = 'Unknown'
            
            decoded_logs.append(decoded)
        
        return decoded_logs
    
    def _get_internal_transactions(self, tx_hash: str) -> List[Dict]:
        """Get internal transactions"""
        params = {
            'module': 'account',
            'action': 'txlistinternal',
            'txhash': tx_hash,
            'apikey': ETHERSCAN_API_KEY
        }
        
        response = requests.get(self.etherscan_base, params=params)
        return response.json().get('result', [])

# Module-level functions
forensics = BlockchainForensics()

def trace_transaction(tx_hash: str) -> Dict[str, Any]:
    return forensics.trace_funds(None, tx_hash)

def trace_address(address: str) -> Dict[str, Any]:
    return forensics.trace_funds(address)

def detect_suspicious(address: str) -> List[Dict[str, Any]]:
    return forensics.detect_suspicious_patterns(address)