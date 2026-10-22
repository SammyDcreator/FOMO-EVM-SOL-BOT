import sqlite3
import json
import threading
from dataclasses import dataclass, asdict
from typing import Optional, List
from datetime import datetime
from config.settings import config


@dataclass
class User:
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_verified: bool = False
    captcha_code: Optional[str] = None
    captcha_expires: Optional[datetime] = None
    wallet_address: Optional[str] = None
    private_key_encrypted: Optional[str] = None
    evm_address: Optional[str] = None
    evm_private_key_encrypted: Optional[str] = None
    sol_balance: float = 0.0
    usd_balance: float = 0.0
    settings: str = "{}"
    created_at: datetime = None
    updated_at: datetime = None
    last_activity: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()
    
    def get_settings(self) -> dict:
        return json.loads(self.settings) if self.settings else {}
    
    def set_settings(self, settings: dict):
        self.settings = json.dumps(settings)
        self.updated_at = datetime.now()


@dataclass
class Position:
    id: Optional[int] = None
    user_id: int = 0
    token_mint: str = ""
    token_symbol: str = ""
    token_name: str = ""
    amount: float = 0.0
    entry_price_sol: float = 0.0
    entry_price_usd: float = 0.0
    current_price_sol: float = 0.0
    current_price_usd: float = 0.0
    pnl_sol: float = 0.0
    pnl_usd: float = 0.0
    pnl_percent: float = 0.0
    tx_signature: str = ""
    created_at: datetime = None
    updated_at: datetime = None
    is_closed: bool = False
    closed_at: Optional[datetime] = None
    exit_price_sol: float = 0.0
    exit_price_usd: float = 0.0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class Transaction:
    id: Optional[int] = None
    user_id: int = 0
    tx_type: str = ""
    token_mint: str = ""
    token_symbol: str = ""
    amount: float = 0.0
    price_sol: float = 0.0
    price_usd: float = 0.0
    sol_amount: float = 0.0
    tx_signature: str = ""
    status: str = "pending"
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class CopyTradeWallet:
    id: Optional[int] = None
    user_id: int = 0
    wallet_address: str = ""
    wallet_name: str = ""
    is_active: bool = True
    buy_percentage: float = 100.0
    sell_percentage: float = 100.0
    max_buy_sol: float = 1.0
    min_buy_sol: float = 0.01
    created_at: datetime = None
    last_trade_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class LimitOrder:
    id: Optional[int] = None
    user_id: int = 0
    token_mint: str = ""
    token_symbol: str = ""
    side: str = ""
    target_price_sol: float = 0.0
    target_price_usd: float = 0.0
    amount: float = 0.0
    sol_amount: float = 0.0
    is_active: bool = True
    is_triggered: bool = False
    created_at: datetime = None
    triggered_at: Optional[datetime] = None
    tx_signature: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class AutoSellRule:
    id: Optional[int] = None
    user_id: int = 0
    token_mint: str = ""
    token_symbol: str = ""
    rule_type: str = ""
    target_percent: float = 0.0
    stop_loss_percent: float = 0.0
    take_profit_percent: float = 0.0
    trailing_stop_percent: float = 0.0
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class AdminNotification:
    id: Optional[int] = None
    user_id: int = 0
    username: str = ""
    action: str = ""
    details: str = ""
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class Database:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.conn = sqlite3.connect(config.DATABASE_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_verified BOOLEAN DEFAULT 0,
                captcha_code TEXT,
                captcha_expires TIMESTAMP,
                wallet_address TEXT,
                private_key_encrypted TEXT,
                evm_address TEXT,
                evm_private_key_encrypted TEXT,
                sol_balance REAL DEFAULT 0,
                usd_balance REAL DEFAULT 0,
                settings TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                token_mint TEXT,
                token_symbol TEXT,
                token_name TEXT,
                amount REAL,
                entry_price_sol REAL,
                entry_price_usd REAL,
                current_price_sol REAL,
                current_price_usd REAL,
                pnl_sol REAL,
                pnl_usd REAL,
                pnl_percent REAL,
                tx_signature TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_closed BOOLEAN DEFAULT 0,
                closed_at TIMESTAMP,
                exit_price_sol REAL,
                exit_price_usd REAL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tx_type TEXT,
                token_mint TEXT,
                token_symbol TEXT,
                amount REAL,
                price_sol REAL,
                price_usd REAL,
                sol_amount REAL,
                tx_signature TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                action TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def get_user(self, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return User(**dict(row))
        return None
    
    def create_user(self, user: User) -> User:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO users (user_id, username, first_name, last_name, is_verified, 
                              captcha_code, captcha_expires, wallet_address, private_key_encrypted,
                              evm_address, evm_private_key_encrypted, sol_balance, usd_balance, settings, created_at, updated_at, last_activity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user.user_id, user.username, user.first_name, user.last_name, user.is_verified,
              user.captcha_code, user.captcha_expires, user.wallet_address, user.private_key_encrypted,
              user.evm_address, user.evm_private_key_encrypted, user.sol_balance, user.usd_balance, user.settings, user.created_at, user.updated_at, user.last_activity))
        self.conn.commit()
        return user
    
    def update_user(self, user: User):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE users SET username=?, first_name=?, last_name=?, is_verified=?,
                            captcha_code=?, captcha_expires=?, wallet_address=?, private_key_encrypted=?,
                            evm_address=?, evm_private_key_encrypted=?,
                            sol_balance=?, usd_balance=?, settings=?, updated_at=?, last_activity=?
            WHERE user_id=?
        """, (user.username, user.first_name, user.last_name, user.is_verified,
              user.captcha_code, user.captcha_expires, user.wallet_address, user.private_key_encrypted,
              user.evm_address, user.evm_private_key_encrypted,
              user.sol_balance, user.usd_balance, user.settings, user.updated_at, user.last_activity, user.user_id))
        self.conn.commit()
    
    def add_admin_notification(self, notification: AdminNotification):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO admin_notifications (user_id, username, action, details, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (notification.user_id, notification.username, notification.action, notification.details, notification.created_at))
        self.conn.commit()


db = Database()


def init_db():
    """Initialize database (called on bot start)"""
    pass  # Tables already created on first DB connection


init_db()