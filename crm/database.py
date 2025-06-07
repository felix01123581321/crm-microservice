import sqlite3
from typing import Dict, List, Tuple, Union, Optional
import time

class Database:
    def __init__(self, db_path: str):
        """Initialize database connection"""
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a SQL query and return results as a list of dictionaries"""
        print(f"\n[DEBUG] Executing query: {query}")
        print(f"[DEBUG] With params: {params}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # For non-SELECT queries, commit changes
            if not query.strip().upper().startswith('SELECT'):
                conn.commit()
                return []
            
            # For SELECT queries, return results as list of dicts
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            print(f"[DEBUG] Query results: {results}")
            return results

    def create_collection(self, collection_name: str, columns: Dict[str, str]):
        """Create a new collection (table) with specified columns"""
        column_defs = [f"{col_name} {col_type}" for col_name, col_type in columns.items()]
        query = f"CREATE TABLE IF NOT EXISTS {collection_name} ({', '.join(column_defs)})"
        self.execute_query(query)

    def insert(self, collection_name: str, data: Dict[str, Union[str, int, float]]) -> int:
        """Insert a new record into the collection"""
        print(f"\n[DEBUG] Inserting into {collection_name}:")
        print(f"[DEBUG] Data: {data}")
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {collection_name} ({columns}) VALUES ({placeholders})"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return cursor.lastrowid

    def get(self, collection_name: str, 
            filters: Optional[Dict[str, Union[str, int, float, Tuple[str, Union[str, int, float]]]]] = None,
            order_by: Optional[str] = None) -> List[Dict]:
        """Retrieve records from the collection with optional filtering and ordering"""
        print(f"\n[DEBUG] Getting from {collection_name}:")
        print(f"[DEBUG] Filters: {filters}")
        query = f"SELECT * FROM {collection_name}"
        params = []

        if filters:
            conditions = []
            for key, value in filters.items():
                if isinstance(value, tuple):
                    operator, val = value
                    conditions.append(f"{key} {operator} ?")
                    params.append(val)
                else:
                    conditions.append(f"{key} = ?")
                    params.append(value)
            query += " WHERE " + " AND ".join(conditions)

        if order_by:
            query += f" ORDER BY {order_by}"

        results = self.execute_query(query, tuple(params))
        print(f"[DEBUG] Get results: {results}")
        return results if results else []

    def update(self, collection_name: str, 
              updates: Dict[str, Union[str, int, float]],
              filters: Dict[str, Union[str, int, float]]):
        """Update records in the collection"""
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        where_clause = ' AND '.join([f"{key} = ?" for key in filters.keys()])
        query = f"UPDATE {collection_name} SET {set_clause} WHERE {where_clause}"
        params = list(updates.values()) + list(filters.values())
        self.execute_query(query, tuple(params))

    def delete(self, collection_name: str, filters: Dict[str, Union[str, int, float]]):
        """Delete records from the collection"""
        where_clause = ' AND '.join([f"{key} = ?" for key in filters.keys()])
        query = f"DELETE FROM {collection_name} WHERE {where_clause}"
        self.execute_query(query, tuple(filters.values()))

    def add_column(self, collection_name: str, column_name: str, column_type: str):
        """Add a new column to an existing collection"""
        query = f"ALTER TABLE {collection_name} ADD COLUMN {column_name} {column_type}"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
        # Wait a moment to ensure the file system is updated (for test environments)
        time.sleep(0.05)

    def search(self, collection_name: str, filters: Dict[str, Union[str, int, float]] = None) -> List[Dict]:
        query = f"SELECT * FROM {collection_name}"
        if filters:
            where_clause = " AND ".join([f"{key} = ?" for key in filters.keys()])
            query += f" WHERE {where_clause}"
            return self.execute_query(query, tuple(filters.values()))
        return self.execute_query(query)

    def close(self):
        """Close the database connection"""
        if hasattr(self, '_connection') and self._connection:
            self._connection.close()
            self._connection = None

    def _set_connection(self, conn):
        self._connection = conn 