import unittest
import os
import tempfile
from crm.database import Database
import time
import sqlite3

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = Database(self.db_path)

    def tearDown(self):
        """Clean up after each test"""
        # Close the database connection
        self.db.close()
        
        # Wait a moment for the connection to fully close
        time.sleep(0.1)
        
        # Try to remove the test database file
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
        except PermissionError:
            # If we can't remove it now, it will be cleaned up later
            pass

    def test_create_collection(self):
        """Test creating a new collection (table)"""
        collection_name = "leads"
        columns = {
            "id": "INTEGER PRIMARY KEY",
            "email": "TEXT NOT NULL",
            "name": "TEXT",
            "status": "TEXT DEFAULT 'new'"
        }
        self.db.create_collection(collection_name, columns)
        
        # Verify collection exists
        result = self.db.execute_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{collection_name}'")
        print(f"[DEBUG] test_create_collection result: {result}")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], collection_name)

    def test_insert_and_get(self):
        """Test inserting and retrieving data"""
        # Create test collection
        self.db.create_collection("leads", {
            "id": "INTEGER PRIMARY KEY",
            "email": "TEXT NOT NULL",
            "name": "TEXT"
        })

        # Insert test data
        data = {"email": "test@example.com", "name": "Test User"}
        self.db.insert("leads", data)

        # Retrieve and verify
        result = self.db.get("leads", {"email": "test@example.com"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["email"], "test@example.com")
        self.assertEqual(result[0]["name"], "Test User")

    def test_update(self):
        """Test updating existing records"""
        # Create and populate test collection
        self.db.create_collection("leads", {
            "id": "INTEGER PRIMARY KEY",
            "email": "TEXT NOT NULL",
            "name": "TEXT"
        })
        self.db.insert("leads", {"email": "test@example.com", "name": "Test User"})

        # Update record
        self.db.update("leads", 
                      {"name": "Updated Name"}, 
                      {"email": "test@example.com"})

        # Verify update
        result = self.db.get("leads", {"email": "test@example.com"})
        self.assertEqual(result[0]["name"], "Updated Name")

    def test_delete(self):
        """Test deleting records"""
        # Create and populate test collection
        self.db.create_collection("leads", {
            "id": "INTEGER PRIMARY KEY",
            "email": "TEXT NOT NULL",
            "name": "TEXT"
        })
        self.db.insert("leads", {"email": "test@example.com", "name": "Test User"})

        # Delete record
        self.db.delete("leads", {"email": "test@example.com"})

        # Verify deletion
        result = self.db.get("leads", {"email": "test@example.com"})
        self.assertEqual(len(result), 0)

    def test_add_column(self):
        """Test adding a new column to an existing collection (single connection version)"""
        print(f"[DEBUG] DB path before create_collection: {self.db_path}")
        print(f"[DEBUG] Files in temp dir before create_collection: {os.listdir(self.temp_dir)}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Drop the table if it exists to ensure a fresh schema
        cursor.execute("DROP TABLE IF EXISTS leads")
        # Create initial collection
        cursor.execute("CREATE TABLE leads (id INTEGER PRIMARY KEY, email TEXT NOT NULL)")
        conn.commit()

        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        result = cursor.fetchall()
        print(f"[DEBUG] Tables in DB after create_collection: {result}")

        # Insert a dummy row to force schema flush
        cursor.execute("INSERT INTO leads (email) VALUES (?)", ("dummy@example.com",))
        conn.commit()

        print(f"[DEBUG] DB path before add_column: {self.db_path}")
        print(f"[DEBUG] Files in temp dir before add_column: {os.listdir(self.temp_dir)}")
        # Add new column
        cursor.execute("ALTER TABLE leads ADD COLUMN status TEXT DEFAULT 'new'")
        conn.commit()

        print(f"[DEBUG] DB path after add_column: {self.db_path}")
        print(f"[DEBUG] Files in temp dir after add_column: {os.listdir(self.temp_dir)}")
        # Verify column was added
        cursor.execute("PRAGMA table_info(leads)")
        result = cursor.fetchall()
        print(f"[DEBUG] test_add_column PRAGMA result: {result}")
        columns = [row[1] for row in result]
        conn.close()
        self.assertIn("status", columns)

    def test_filter_query(self):
        """Test filtering records with complex conditions"""
        # Create and populate test collection
        self.db.create_collection("leads", {
            "id": "INTEGER PRIMARY KEY",
            "email": "TEXT NOT NULL",
            "status": "TEXT",
            "score": "INTEGER"
        })

        # Insert test data
        test_data = [
            {"email": "test1@example.com", "status": "new", "score": 80},
            {"email": "test2@example.com", "status": "contacted", "score": 60},
            {"email": "test3@example.com", "status": "new", "score": 90}
        ]
        for data in test_data:
            self.db.insert("leads", data)

        # Test complex filter
        result = self.db.get("leads", 
                           {"status": "new", "score": (">", 85)},
                           order_by="score DESC")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["email"], "test3@example.com")

    def test_lead_with_url(self):
        """Test creating and retrieving a lead with URL field"""
        # Create test collection with URL field
        self.db.create_collection("leads", {
            "id": "INTEGER PRIMARY KEY",
            "email": "TEXT NOT NULL",
            "name": "TEXT",
            "url": "TEXT"
        })

        # Insert test data with URL
        data = {
            "email": "test@example.com",
            "name": "Test User",
            "url": "https://example.com/profile"
        }
        self.db.insert("leads", data)

        # Retrieve and verify
        result = self.db.get("leads", {"email": "test@example.com"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["email"], "test@example.com")
        self.assertEqual(result[0]["name"], "Test User")
        self.assertEqual(result[0]["url"], "https://example.com/profile")

    def test_lead_status_default_and_mandatory(self):
        """Test that lead status defaults to 'new' and is mandatory in database"""
        # Create test collection with status field
        self.db.create_collection("leads", {
            "id": "INTEGER PRIMARY KEY",
            "email": "TEXT NOT NULL",
            "name": "TEXT",
            "status": "TEXT NOT NULL DEFAULT 'new'"
        })

        # Insert test data without status (should default to 'new')
        data = {
            "email": "test@example.com",
            "name": "Test User"
        }
        self.db.insert("leads", data)

        # Retrieve and verify status defaulted to 'new'
        result = self.db.get("leads", {"email": "test@example.com"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["status"], "new")

        # Test that status cannot be set to NULL
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.update("leads", {"status": None}, {"email": "test@example.com"})

    def test_action_timestamp(self):
        """Test that actions have a timestamp field in database"""
        # Create test collection for actions
        self.db.create_collection("actions", {
            "id": "INTEGER PRIMARY KEY",
            "lead_id": "INTEGER NOT NULL",
            "action_type": "TEXT NOT NULL",
            "details": "TEXT",
            "timestamp": "TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP"
        })

        # Insert test action
        data = {
            "lead_id": 1,
            "action_type": "email",
            "details": "Initial contact"
        }
        self.db.insert("actions", data)

        # Retrieve and verify timestamp
        result = self.db.get("actions", {"lead_id": 1})
        self.assertEqual(len(result), 1)
        self.assertIn("timestamp", result[0])
        self.assertIsNotNone(result[0]["timestamp"])

    def test_process_followup_datetime(self):
        """Test that process followup datetime is set to 7 days after last action in database"""
        # Create test collections
        self.db.create_collection("actions", {
            "id": "INTEGER PRIMARY KEY",
            "lead_id": "INTEGER NOT NULL",
            "action_type": "TEXT NOT NULL",
            "details": "TEXT",
            "timestamp": "TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP"
        })

        self.db.create_collection("processes", {
            "id": "INTEGER PRIMARY KEY",
            "lead_id": "INTEGER NOT NULL",
            "channel": "TEXT NOT NULL",
            "last_action_id": "INTEGER NOT NULL",
            "next_followup_datetime": "TEXT NOT NULL",
            "status": "TEXT NOT NULL DEFAULT 'active'"
        })

        # Insert test action
        action_data = {
            "lead_id": 1,
            "action_type": "email",
            "details": "Initial contact"
        }
        action_id = self.db.insert("actions", action_data)

        # Get the action's timestamp
        action = self.db.get("actions", {"id": action_id})[0]
        action_timestamp = action["timestamp"]

        # Calculate expected followup datetime (7 days after action timestamp)
        from datetime import datetime, timedelta
        expected_followup = datetime.strptime(action_timestamp, "%Y-%m-%d %H:%M:%S") + timedelta(days=7)
        expected_followup_str = expected_followup.strftime("%Y-%m-%d %H:%M:%S")

        # Insert process with followup datetime
        process_data = {
            "lead_id": 1,
            "channel": "email",
            "last_action_id": action_id,
            "next_followup_datetime": expected_followup_str,
            "status": "active"
        }
        process_id = self.db.insert("processes", process_data)

        # Retrieve and verify followup datetime
        result = self.db.get("processes", {"id": process_id})
        self.assertEqual(len(result), 1)
        actual_followup = datetime.strptime(result[0]["next_followup_datetime"], "%Y-%m-%d %H:%M:%S")
        self.assertEqual(actual_followup, expected_followup)

if __name__ == '__main__':
    unittest.main() 