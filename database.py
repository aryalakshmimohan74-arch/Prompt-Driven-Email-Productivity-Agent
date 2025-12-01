import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Get absolute path to database
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            db_dir = os.path.join(project_root, "database")
            
            # Create database directory if it doesn't exist
            os.makedirs(db_dir, exist_ok=True)
            
            db_path = os.path.join(db_dir, "emails.db")
        
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Create a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Emails table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                category TEXT,
                action_items TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Prompts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                description TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Drafts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Email operations
    def insert_email(self, sender: str, subject: str, body: str, 
                     timestamp: str, category: str = None, 
                     action_items: str = None) -> int:
        """Insert a new email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO emails (sender, subject, body, timestamp, category, action_items)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (sender, subject, body, timestamp, category, action_items))
        email_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return email_id
    
    def get_all_emails(self) -> List[Dict]:
        """Get all emails"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM emails ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_email_by_id(self, email_id: int) -> Optional[Dict]:
        """Get a specific email by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM emails WHERE id = ?', (email_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def update_email_category(self, email_id: int, category: str):
        """Update email category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE emails SET category = ? WHERE id = ?', 
                      (category, email_id))
        conn.commit()
        conn.close()
    
    def update_email_action_items(self, email_id: int, action_items: str):
        """Update email action items"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE emails SET action_items = ? WHERE id = ?', 
                      (action_items, email_id))
        conn.commit()
        conn.close()
    
    def delete_all_emails(self):
        """Delete all emails"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM emails')
        conn.commit()
        conn.close()
    
    # Prompt operations
    def upsert_prompt(self, name: str, content: str, description: str = ""):
        """Insert or update a prompt"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO prompts (name, content, description, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                content = excluded.content,
                description = excluded.description,
                updated_at = excluded.updated_at
        ''', (name, content, description, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_prompt(self, name: str) -> Optional[Dict]:
        """Get a prompt by name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prompts WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_all_prompts(self) -> List[Dict]:
        """Get all prompts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prompts')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # Draft operations
    def insert_draft(self, email_id: Optional[int], subject: str, 
                     body: str, metadata: str = None) -> int:
        """Insert a new draft"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO drafts (email_id, subject, body, metadata)
            VALUES (?, ?, ?, ?)
        ''', (email_id, subject, body, metadata))
        draft_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return draft_id
    
    def get_all_drafts(self) -> List[Dict]:
        """Get all drafts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM drafts ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_draft_by_id(self, draft_id: int) -> Optional[Dict]:
        """Get a specific draft by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM drafts WHERE id = ?', (draft_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def delete_draft(self, draft_id: int):
        """Delete a draft"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM drafts WHERE id = ?', (draft_id,))
        conn.commit()
        conn.close()
