import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from web3 import Web3
import pandas as pd
from config import ETHERSCAN_API_KEY, TENDERLY_API_KEY, RPC_URL

class ContractMonitor:
    def _init_(self):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        self.etherscan_base = "https://api-sepolia.etherscan.io/api"
        self.tenderly_base = "https://api.tenderly.co/api/v1"
    
    def get_recent_transactions(self, address: str, limit: int = 20) -> List[Dict]:
        """Get recent transactions for a contract"""
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'desc',
            'apikey': ETHERSCAN_API_KEY
        }
        
        try:
            response = requests.get(self.etherscan_base, params=params)
            data = response.json()
            
            if data['status'] == '1':
                transactions = data['result'][:limit]
                # Process transactions
                processed_txs = []
                for tx in transactions:
                    processed_txs.append({
                        'hash': tx['hash'],
                        'from': tx['from'],
                        'to': tx['to'],
                        'value': str(Web3.from_wei(int(tx['value']), 'ether')),
                        'gas_used': tx['gasUsed'],
                        'timestamp': datetime.fromtimestamp(int(tx['timeStamp'])).isoformat(),
                        'method': tx.get('functionName', 'Unknown')
                    })
                return processed_txs
            else:
                return []
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return []
    
    def get_activity_data(self, address: str) -> pd.DataFrame:
        """Get transaction activity data for charts"""
        transactions = self.get_recent_transactions(address, limit=100)
        
        if not transactions:
            return pd.DataFrame()
        
        # Group by hour
        df = pd.DataFrame(transactions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.floor('H')
        
        activity = df.groupby('hour').size().reset_index(name='tx_count')
        return activity
    
    def get_security_alerts(self, address: str) -> List[Dict]:
        """Check for security alerts"""
        alerts = []
        
        # Check for large transfers
        transactions = self.get_recent_transactions(address, limit=50)
        for tx in transactions:
            value = float(tx['value'])
            if value > 10:  # More than 10 ETH
                alerts.append({
                    'type': 'warning',
                    'message': f"Large transfer detected: {value} ETH in tx {tx['hash'][:10]}...",
                    'timestamp': tx['timestamp']
                })
        
        # Check for high gas usage
        high_gas_txs = [tx for tx in transactions if int(tx['gas_used']) > 1000000]
        if high_gas_txs:
            alerts.append({
                'type': 'warning',
                'message': f"High gas usage detected in {len(high_gas_txs)} transactions",
                'timestamp': datetime.now().isoformat()
            })
        
        # Simulate some alerts for demo
        alerts.extend([
            {
                'type': 'info',
                'message': 'Contract monitoring started successfully',
                'timestamp': datetime.now().isoformat()
            }
        ])
        
        return alerts
    
    def get_gas_analytics(self, address: str) -> pd.DataFrame:
        """Get gas usage analytics"""
        transactions = self.get_recent_transactions(address, limit=100)
        
        if not transactions:
            return pd.DataFrame()
        
        # Group by function
        function_gas = {}
        for tx in transactions:
            func = tx.get('method', 'Unknown').split('(')[0]
            if func not in function_gas:
                function_gas[func] = []
            function_gas[func].append(int(tx['gas_used']))
        
        # Calculate averages
        data = []
        for func, gas_values in function_gas.items():
            data.append({
                'function': func,
                'avg_gas': sum(gas_values) / len(gas_values),
                'max_gas': max(gas_values),
                'call_count': len(gas_values)
            })
        
        return pd.DataFrame(data)
    
    def get_value_flow(self, address: str) -> pd.DataFrame:
        """Get value flow data"""
        transactions = self.get_recent_transactions(address, limit=100)
        
        if not transactions:
            return pd.DataFrame()
        
        inflow = sum(float(tx['value']) for tx in transactions if tx['to'].lower() == address.lower())
        outflow = sum(float(tx['value']) for tx in transactions if tx['from'].lower() == address.lower())
        
        data = pd.DataFrame([
            {'direction': 'Inflow', 'amount': inflow},
            {'direction': 'Outflow', 'amount': outflow}
        ])
        
        return data

# Module-level functions
monitor_instance = ContractMonitor()

def get_recent_transactions(address: str, limit: int = 20) -> List[Dict]:
    return monitor_instance.get_recent_transactions(address, limit)

def get_activity_data(address: str) -> pd.DataFrame:
    return monitor_instance.get_activity_data(address)

def get_security_alerts(address: str) -> List[Dict]:
    return monitor_instance.get_security_alerts(address)

def get_gas_analytics(address: str) -> pd.DataFrame:
    return monitor_instance.get_gas_analytics(address)

def get_value_flow(address: str) -> pd.DataFrame:
    return monitor_instance.get_value_flow(address)