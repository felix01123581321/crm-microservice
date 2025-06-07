import unittest
from fastapi.testclient import TestClient
from crm.api import create_app_with_db
import os
import sys
import tempfile

class TestCRMAPI(unittest.TestCase):
    def setUp(self):
        # Create a unique temporary database file for each test
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_api.db")
        # Patch the app to use this db_path
        from crm.api import create_app_with_db
        self.app = create_app_with_db(self.db_path)
        global client
        client = TestClient(self.app)

    def tearDown(self):
        # Clean up the temporary database file and directory
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            if os.path.exists(self.temp_dir):
                os.rmdir(self.temp_dir)
        except Exception:
            pass

    def test_create_lead(self):
        response = client.post("/leads/", json={"name": "Test Lead", "email": "test@example.com", "status": "new"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())

    def test_get_lead(self):
        # First create a lead
        create_response = client.post("/leads/", json={"name": "Test Lead", "email": "test@example.com", "status": "new"})
        lead_id = create_response.json()["id"]

        # Now get the lead
        response = client.get(f"/leads/{lead_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Test Lead")

    def test_update_lead(self):
        # First create a lead
        create_response = client.post("/leads/", json={"name": "Test Lead", "email": "test@example.com", "status": "new"})
        lead_id = create_response.json()["id"]

        # Now update the lead
        response = client.put(f"/leads/{lead_id}", json={"name": "Updated Lead", "email": "updated@example.com", "status": "contacted"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Updated Lead")

    def test_delete_lead(self):
        # First create a lead
        create_response = client.post("/leads/", json={"name": "Test Lead", "email": "test@example.com", "status": "new"})
        lead_id = create_response.json()["id"]

        # Now delete the lead
        response = client.delete(f"/leads/{lead_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Lead deleted")

    def test_search_leads(self):
        # First create a lead
        client.post("/leads/", json={"name": "Test Lead", "email": "test@example.com", "status": "new"})

        # Now search for leads
        response = client.get("/leads/", params={"status": "new"})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_create_action(self):
        # Create a lead first
        lead_response = client.post("/leads/", json={"name": "Test Lead", "email": "test@example.com", "status": "new"})
        lead_id = lead_response.json()["id"]
        response = client.post("/actions/", json={"lead_id": lead_id, "action_type": "email", "description": "Send welcome email"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())

    def test_get_action(self):
        # First create a lead and an action
        lead_response = client.post("/leads/", json={"name": "Test Lead", "email": "test@example.com", "status": "new"})
        lead_id = lead_response.json()["id"]
        create_response = client.post("/actions/", json={"lead_id": lead_id, "action_type": "email", "description": "Send welcome email"})
        action_id = create_response.json()["id"]

        # Now get the action
        response = client.get(f"/actions/{action_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["action_type"], "email")

    def test_search_actions(self):
        # First create a lead and an action
        lead_response = client.post("/leads/", json={"name": "Test Lead", "email": "test@example.com", "status": "new"})
        lead_id = lead_response.json()["id"]
        client.post("/actions/", json={"lead_id": lead_id, "action_type": "email", "description": "Send welcome email"})

        # Now search for actions
        response = client.get("/actions/", params={"action_type": "email"})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_create_process(self):
        # Create a lead first
        lead_response = client.post("/leads/", json={"name": "Test Lead", "email": "test@example.com", "status": "new"})
        lead_id = lead_response.json()["id"]
        
        # Create an action which should automatically create a process
        action_response = client.post("/actions/", json={"lead_id": lead_id, "action_type": "email", "description": "Initial action"})
        self.assertEqual(action_response.status_code, 200)
        
        # Verify that a process was created automatically
        processes = client.get("/processes/").json()
        self.assertEqual(len(processes), 1)
        process = processes[0]
        self.assertEqual(process["lead_id"], lead_id)
        self.assertEqual(process["channel"], "email")
        self.assertEqual(process["status"], "active")

    def test_get_process(self):
        # Create a lead and an action first
        lead_response = client.post("/leads/", json={"name": "Test Lead", "email": "test@example.com", "status": "new"})
        lead_id = lead_response.json()["id"]
        action_response = client.post("/actions/", json={"lead_id": lead_id, "action_type": "email", "description": "Initial action"})
        
        # Get the automatically created process
        processes = client.get("/processes/").json()
        self.assertEqual(len(processes), 1)
        process_id = processes[0]["id"]

        # Now get the process
        response = client.get(f"/processes/{process_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["lead_id"], lead_id)
        self.assertEqual(response.json()["channel"], "email")
        self.assertEqual(response.json()["status"], "active")

    def test_search_processes(self):
        # Create a lead and an action first
        lead_response = client.post("/leads/", json={"name": "Test Lead", "email": "test@example.com", "status": "new"})
        lead_id = lead_response.json()["id"]
        client.post("/actions/", json={"lead_id": lead_id, "action_type": "email", "description": "Initial action"})

        # Now search for processes
        response = client.get("/processes/", params={"status": "active"})
        self.assertEqual(response.status_code, 200)
        processes = response.json()
        self.assertIsInstance(processes, list)
        self.assertEqual(len(processes), 1)
        self.assertEqual(processes[0]["lead_id"], lead_id)
        self.assertEqual(processes[0]["status"], "active")

    def test_lead_with_url(self):
        """Test creating and managing a lead with URL field through the API"""
        # Create lead with URL
        create_response = client.post("/leads/", json={
            "name": "Test Lead",
            "email": "test@example.com",
            "status": "new",
            "url": "https://example.com/profile"
        })
        self.assertEqual(create_response.status_code, 200)
        lead_id = create_response.json()["id"]
        
        # Verify lead was created with URL
        get_response = client.get(f"/leads/{lead_id}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["url"], "https://example.com/profile")
        
        # Test updating URL
        update_response = client.put(f"/leads/{lead_id}", json={
            "name": "Test Lead",
            "email": "test@example.com",
            "status": "new",
            "url": "https://example.com/updated-profile"
        })
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["url"], "https://example.com/updated-profile")
        
        # Test searching by URL
        search_response = client.get("/leads/", params={"url": "https://example.com/updated-profile"})
        self.assertEqual(search_response.status_code, 200)
        results = search_response.json()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], lead_id)

    def test_lead_status_default_and_mandatory(self):
        """Test that lead status defaults to 'new' and is mandatory through the API"""
        # Test creating lead without status (should default to 'new')
        create_response = client.post("/leads/", json={
            "name": "Test Lead",
            "email": "test@example.com"
        })
        self.assertEqual(create_response.status_code, 200)
        lead_id = create_response.json()["id"]

        # Verify status defaulted to 'new'
        get_response = client.get(f"/leads/{lead_id}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["status"], "new")

        # Test that status cannot be set to None (FastAPI returns 422 for invalid request body)
        update_response = client.put(f"/leads/{lead_id}", json={
            "name": "Test Lead",
            "email": "test@example.com",
            "status": None
        })
        self.assertEqual(update_response.status_code, 422)

    def test_action_timestamp(self):
        """Test that actions have a timestamp field through the API"""
        # Create lead
        lead_response = client.post("/leads/", json={
            "name": "Test Lead",
            "email": "test@example.com"
        })
        lead_id = lead_response.json()["id"]

        # Create action
        action_response = client.post("/actions/", json={
            "lead_id": lead_id,
            "action_type": "email",
            "details": "Initial contact"
        })
        self.assertEqual(action_response.status_code, 200)
        action_id = action_response.json()["id"]

        # Verify action has timestamp
        get_response = client.get(f"/actions/{action_id}")
        self.assertEqual(get_response.status_code, 200)
        action = get_response.json()
        self.assertIn("timestamp", action)
        self.assertIsNotNone(action["timestamp"])

    def test_process_followup_datetime(self):
        """Test that process followup datetime is set to 7 days after last action through the API"""
        # Create lead
        lead_response = client.post("/leads/", json={
            "name": "Test Lead",
            "email": "test@example.com"
        })
        lead_id = lead_response.json()["id"]

        # Create action
        action_response = client.post("/actions/", json={
            "lead_id": lead_id,
            "action_type": "email",
            "details": "Initial contact"
        })
        action_id = action_response.json()["id"]

        # Get the process that was created
        process_response = client.get("/processes/", params={"lead_id": lead_id})
        self.assertEqual(process_response.status_code, 200)
        processes = process_response.json()
        self.assertEqual(len(processes), 1)
        process = processes[0]

        # Get the action to check its timestamp
        action_response = client.get(f"/actions/{action_id}")
        action = action_response.json()
        action_timestamp = action["timestamp"]

        # Calculate expected followup datetime (7 days after action timestamp)
        from datetime import datetime, timedelta
        expected_followup = datetime.strptime(action_timestamp, "%Y-%m-%d %H:%M:%S") + timedelta(days=7)
        actual_followup = datetime.strptime(process["next_followup_datetime"], "%Y-%m-%d %H:%M:%S")

        # Verify followup datetime is set correctly
        self.assertEqual(actual_followup, expected_followup)

    def test_lead_email_validation(self):
        """Test email validation and formatting"""
        # Test creating lead with uppercase email (should be converted to lowercase)
        create_response = client.post("/leads/", json={
            "name": "Test Lead",
            "email": "TEST@EXAMPLE.COM"
        })
        self.assertEqual(create_response.status_code, 200)
        lead_id = create_response.json()["id"]

        # Verify email was converted to lowercase
        get_response = client.get(f"/leads/{lead_id}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["email"], "test@example.com")

        # Test creating lead with invalid email format
        invalid_response = client.post("/leads/", json={
            "name": "Test Lead",
            "email": "invalid-email"
        })
        self.assertEqual(invalid_response.status_code, 422)

    def test_lead_duplicate_prevention(self):
        """Test that duplicate leads (same email) are not allowed"""
        # Create first lead
        create_response = client.post("/leads/", json={
            "name": "Test Lead 1",
            "email": "test@example.com"
        })
        self.assertEqual(create_response.status_code, 200)

        # Try to create second lead with same email (case insensitive)
        duplicate_response = client.post("/leads/", json={
            "name": "Test Lead 2",
            "email": "TEST@EXAMPLE.COM"
        })
        self.assertEqual(duplicate_response.status_code, 400)
        self.assertIn("email already exists", duplicate_response.json()["detail"].lower())

        # Try to create lead with different email (should succeed)
        different_response = client.post("/leads/", json={
            "name": "Test Lead 3",
            "email": "different@example.com"
        })
        self.assertEqual(different_response.status_code, 200)

if __name__ == "__main__":
    unittest.main() 