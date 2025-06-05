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
            "status": "TEXT"
        })

        # Create actions table
        self.db.create_collection("actions", {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "lead_id": "INTEGER",
            "action_type": "TEXT",
            "details": "TEXT"  # Revert to details for compatibility
        })

        # Create processes table
        self.db.create_collection("processes", {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT",  # Add back name for compatibility
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
        return self.db.insert("leads", lead_data)

    def get_lead(self, lead_id: int) -> Optional[Dict]:
        """Retrieve a lead by its ID."""
        results = self.db.get("leads", {"id": lead_id})
        return results[0] if results else None

    def update_lead(self, lead_id: int, lead_data: Dict[str, Union[str, int, float]]) -> None:
        """Update an existing lead."""
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
        return self.db.insert("actions", action_data)

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