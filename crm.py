from typing import Dict, List, Optional, Union
from .database import Database

class CRM:
    def __init__(self, db_path: str):
        """Initialize the CRM with a database connection."""
        self.db = Database(db_path)
        self._init_db()

    def _init_db(self):
        """Initialize the database with required tables"""
        # Create leads table
        self.db.create_collection("leads", {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT",
            "email": "TEXT",
            "status": "TEXT NOT NULL DEFAULT 'new'",
            "url": "TEXT"
        })

        # Create actions table
        self.db.create_collection("actions", {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "lead_id": "INTEGER",
            "action_type": "TEXT",
            "details": "TEXT",
            "timestamp": "TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))"
        })

        # Create processes table
        self.db.create_collection("processes", {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT",
            "lead_id": "INTEGER",
            "channel": "TEXT",
            "last_action_id": "INTEGER",
            "next_followup_datetime": "TEXT",
            "status": "TEXT"
        })

    def close(self):
        """Close the database connection."""
        self.db.close()

    # Lead operations
    def create_lead(self, lead_data: Dict[str, Union[str, int, float]]) -> int:
        """Create a new lead and return its ID."""
        # Default status to 'new' if not provided
        if "status" not in lead_data or lead_data["status"] is None:
            lead_data["status"] = "new"
        if lead_data["status"] is None:
            raise ValueError("Lead status cannot be None")
        return self.db.insert("leads", lead_data)

    def get_lead(self, lead_id: int) -> Optional[Dict]:
        """Retrieve a lead by its ID."""
        results = self.db.get("leads", {"id": lead_id})
        return results[0] if results else None

    def update_lead(self, lead_id: int, lead_data: Dict[str, Union[str, int, float]]) -> None:
        """Update an existing lead."""
        if "status" in lead_data and lead_data["status"] is None:
            raise ValueError("Lead status cannot be None")
        self.db.update("leads", lead_data, {"id": lead_id})

    def delete_lead(self, lead_id: int) -> None:
        """Delete a lead by its ID."""
        self.db.delete("leads", {"id": lead_id})

    def search_leads(self, filters: Dict[str, Union[str, int, float]] = None) -> List[Dict]:
        """Search for leads based on filters."""
        return self.db.search("leads", filters)

    # Action operations
    def create_action(self, action_data: Dict[str, Union[str, int, float]]) -> int:
        """Create a new action and return its ID."""
        from datetime import datetime, timedelta
        # Insert action with timestamp
        if "timestamp" not in action_data or not action_data["timestamp"]:
            action_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        action_id = self.db.insert("actions", action_data)
        # Get the action's timestamp (from DB, in case DB sets it)
        action = self.get_action(action_id)
        action_timestamp = action["timestamp"]
        # Check if a process already exists for this lead
        existing_processes = self.db.search("processes", {"lead_id": action_data["lead_id"]})
        # Calculate next followup datetime (7 days after action's timestamp)
        next_followup = (datetime.strptime(action_timestamp, "%Y-%m-%d %H:%M:%S") + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        if not existing_processes:
            # Create new process for first action
            process_data = {
                "lead_id": action_data["lead_id"],
                "channel": action_data["action_type"],
                "last_action_id": action_id,
                "next_followup_datetime": next_followup,
                "status": "active"
            }
            self.db.insert("processes", process_data)
        else:
            # Update existing process
            process = existing_processes[0]
            update_data = {
                "channel": action_data["action_type"],
                "last_action_id": action_id,
                "next_followup_datetime": next_followup
            }
            self.db.update("processes", update_data, {"id": process["id"]})
        return action_id

    def get_action(self, action_id: int) -> Optional[Dict]:
        """Retrieve an action by its ID."""
        results = self.db.get("actions", {"id": action_id})
        return results[0] if results else None

    def search_actions(self, filters: Dict[str, Union[str, int, float]] = None) -> List[Dict]:
        """Search for actions based on filters."""
        return self.db.search("actions", filters)

    # Process operations
    def create_process(self, process_data: Dict[str, Union[str, int, float]]) -> int:
        """Create a new process and return its ID."""
        return self.db.insert("processes", process_data)

    def get_process(self, process_id: int) -> Optional[Dict]:
        """Retrieve a process by its ID."""
        results = self.db.get("processes", {"id": process_id})
        return results[0] if results else None

    def search_processes(self, filters: Dict[str, Union[str, int, float]] = None) -> List[Dict]:
        """Search for processes based on filters."""
        return self.db.search("processes", filters) 