"""Blockchain Integration for Daur-AI v2.0"""
import logging
import json
import hashlib
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from web3 import Web3
    ETHEREUM_AVAILABLE = True
except ImportError:
    ETHEREUM_AVAILABLE = False
    logger.warning("web3 not available")

try:
    from solders.keypair import Keypair
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False
    logger.warning("solders not available")


class BlockchainType(Enum):
    ETHEREUM = "ethereum"
    SOLANA = "solana"
    LOCAL = "local"


@dataclass
class BlockchainLog:
    log_id: str
    user_id: int
    action: str
    details: Dict[str, Any]
    timestamp: str
    hash: str
    tx_hash: Optional[str] = None
    verified: bool = False


class EthereumLogger:
    def __init__(self, rpc_url: str = "http://localhost:8545",
                 contract_address: Optional[str] = None,
                 private_key: Optional[str] = None):
        if not ETHEREUM_AVAILABLE:
            raise ImportError("web3 is required")
        
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract_address = contract_address
        self.private_key = private_key
        self.account = None
        
        if private_key:
            self.account = self.web3.eth.account.from_key(private_key)
        
        if self.web3.is_connected():
            logger.info(f"Connected to Ethereum: {rpc_url}")
        else:
            logger.warning(f"Failed to connect to Ethereum: {rpc_url}")
    
    def log_action(self, user_id: int, action: str, details: Dict) -> Optional[str]:
        try:
            log_data = {
                "user_id": user_id,
                "action": action,
                "details": details,
                "timestamp": datetime.now().isoformat()
            }
            
            log_json = json.dumps(log_data)
            log_hash = hashlib.sha256(log_json.encode()).hexdigest()
            
            logger.info(f"Ethereum log: {log_hash}")
            return log_hash
        except Exception as e:
            logger.error(f"Error logging to Ethereum: {e}")
            return None


class SolanaLogger:
    def __init__(self, rpc_url: str = "http://localhost:8899"):
        if not SOLANA_AVAILABLE:
            raise ImportError("solders is required")
        
        self.rpc_url = rpc_url
        logger.info(f"Solana Logger initialized: {rpc_url}")
    
    def log_action(self, user_id: int, action: str, details: Dict) -> Optional[str]:
        try:
            log_data = {
                "user_id": user_id,
                "action": action,
                "details": details,
                "timestamp": datetime.now().isoformat()
            }
            
            log_json = json.dumps(log_data)
            log_hash = hashlib.sha256(log_json.encode()).hexdigest()
            
            logger.info(f"Solana log hash: {log_hash}")
            return log_hash
        except Exception as e:
            logger.error(f"Error logging to Solana: {e}")
            return None


class LocalBlockchain:
    def __init__(self):
        self.chain: List[BlockchainLog] = []
        logger.info("Local Blockchain initialized")
    
    def log_action(self, user_id: int, action: str, details: Dict) -> str:
        log_data = {
            "user_id": user_id,
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        log_json = json.dumps(log_data)
        log_hash = hashlib.sha256(log_json.encode()).hexdigest()
        
        log_id = f"local_{len(self.chain)}"
        
        blockchain_log = BlockchainLog(
            log_id=log_id,
            user_id=user_id,
            action=action,
            details=details,
            timestamp=log_data["timestamp"],
            hash=log_hash,
            verified=True
        )
        
        self.chain.append(blockchain_log)
        logger.info(f"Local log added: {log_id}")
        
        return log_hash
    
    def verify_integrity(self) -> bool:
        for i, log in enumerate(self.chain):
            log_data = {
                "user_id": log.user_id,
                "action": log.action,
                "details": log.details,
                "timestamp": log.timestamp
            }
            
            log_json = json.dumps(log_data)
            expected_hash = hashlib.sha256(log_json.encode()).hexdigest()
            
            if log.hash != expected_hash:
                logger.error(f"Integrity check failed at log {i}")
                return False
        
        logger.info("Integrity check passed")
        return True
    
    def get_logs(self, user_id: Optional[int] = None) -> List[BlockchainLog]:
        if user_id:
            return [log for log in self.chain if log.user_id == user_id]
        return self.chain


class BlockchainAuditTrail:
    def __init__(self, blockchain_type: BlockchainType = BlockchainType.LOCAL,
                 **kwargs):
        self.blockchain_type = blockchain_type
        self.logger_instance = None
        
        if blockchain_type == BlockchainType.ETHEREUM:
            try:
                self.logger_instance = EthereumLogger(**kwargs)
            except Exception as e:
                logger.error(f"Failed to initialize Ethereum: {e}")
                self.logger_instance = LocalBlockchain()
        
        elif blockchain_type == BlockchainType.SOLANA:
            try:
                self.logger_instance = SolanaLogger(**kwargs)
            except Exception as e:
                logger.error(f"Failed to initialize Solana: {e}")
                self.logger_instance = LocalBlockchain()
        
        else:
            self.logger_instance = LocalBlockchain()
        
        logger.info(f"Blockchain Audit Trail: {blockchain_type.value}")
    
    def log_user_action(self, user_id: int, action: str, **details) -> Optional[str]:
        return self.logger_instance.log_action(user_id, action, details)
    
    def log_security_event(self, user_id: int, event_type: str, **details) -> Optional[str]:
        return self.logger_instance.log_action(
            user_id,
            f"security:{event_type}",
            details
        )
    
    def log_api_call(self, user_id: int, endpoint: str, method: str, **details) -> Optional[str]:
        return self.logger_instance.log_action(
            user_id,
            f"api:{method}:{endpoint}",
            details
        )
    
    def get_audit_trail(self, user_id: Optional[int] = None) -> List[Dict]:
        if isinstance(self.logger_instance, LocalBlockchain):
            logs = self.logger_instance.get_logs(user_id)
            return [
                {
                    "log_id": log.log_id,
                    "user_id": log.user_id,
                    "action": log.action,
                    "timestamp": log.timestamp,
                    "hash": log.hash,
                    "verified": log.verified
                }
                for log in logs
            ]
        return []
    
    def verify_integrity(self) -> bool:
        if isinstance(self.logger_instance, LocalBlockchain):
            return self.logger_instance.verify_integrity()
        return True
