import unittest
import os
import tempfile
from crm.crm import CRM
import time

class TestCRM(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.crm = CRM(self.db_path)

    def tearDown(self):
        """Clean up after each test"""
        # Close the CRM instance
        self.crm.close()
        
        # Wait a moment for the connection to fully close
        time.sleep(0.1)
        
        # Try to remove the test database file
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
        except PermissionError:
            # If we can't remove it now, it will be cleaned up later
            pass

    def test_create_lead(self):
        """Test creating a new lead"""
        lead_data = {
            "name": "Test Lead",
            "email": "test@example.com",
            "status": "new"
        }
        lead_id = self.crm.create_lead(lead_data)
        self.assertIsNotNone(lead_id)
        # Verify lead exists
        lead = self.crm.get_lead(lead_id)
        self.assertEqual(lead["name"], "Test Lead")
        self.assertEqual(lead["email"], "test@example.com")
        self.assertEqual(lead["status"], "new")

    def test_update_lead(self):
        """Test updating an existing lead"""
        lead_data = {
            "name": "Test Lead",
            "email": "test@example.com",
            "status": "new"
        }
        lead_id = self.crm.create_lead(lead_data)
        update_data = {"status": "contacted"}
        self.crm.update_lead(lead_id, update_data)
        lead = self.crm.get_lead(lead_id)
        self.assertEqual(lead["status"], "contacted")

    def test_delete_lead(self):
        """Test deleting a lead"""
        lead_data = {
            "name": "Test Lead",
            "email": "test@example.com",
            "status": "new"
        }
        lead_id = self.crm.create_lead(lead_data)
        self.crm.delete_lead(lead_id)
        lead = self.crm.get_lead(lead_id)
        self.assertIsNone(lead)

    def test_create_action(self):
        """Test creating a new action"""
        lead_data = {
            "name": "Test Lead",
            "email": "test@example.com",
            "status": "new"
        }
        lead_id = self.crm.create_lead(lead_data)
        action_data = {
            "lead_id": lead_id,
            "action_type": "email",
            "details": "Sent initial email"
        }
        action_id = self.crm.create_action(action_data)
        self.assertIsNotNone(action_id)
        # Verify action exists
        action = self.crm.get_action(action_id)
        self.assertEqual(action["lead_id"], lead_id)
        self.assertEqual(action["action_type"], "email")
        self.assertEqual(action["details"], "Sent initial email")

    def test_create_process(self):
        """Test creating a new process"""
        lead_data = {
            "name": "Test Lead",
            "email": "test@example.com",
            "status": "new"
        }
        lead_id = self.crm.create_lead(lead_data)
        action_data = {
            "lead_id": lead_id,
            "action_type": "email",
            "details": "Sent initial email"
        }
        action_id = self.crm.create_action(action_data)
        process_data = {
            "lead_id": lead_id,
            "channel": "email",
            "last_action_id": action_id,
            "next_followup_datetime": "2023-10-01 10:00:00",
            "status": "active"
        }
        process_id = self.crm.create_process(process_data)
        self.assertIsNotNone(process_id)
        # Verify process exists
        process = self.crm.get_process(process_id)
        self.assertEqual(process["lead_id"], lead_id)
        self.assertEqual(process["channel"], "email")
        self.assertEqual(process["last_action_id"], action_id)
        self.assertEqual(process["next_followup_datetime"], "2023-10-01 10:00:00")
        self.assertEqual(process["status"], "active")

    def test_search_leads(self):
        """Test searching leads with filters"""
        lead_data1 = {
            "name": "Test Lead 1",
            "email": "test1@example.com",
            "status": "new"
        }
        lead_data2 = {
            "name": "Test Lead 2",
            "email": "test2@example.com",
            "status": "contacted"
        }
        self.crm.create_lead(lead_data1)
        self.crm.create_lead(lead_data2)
        # Search for leads with status "new"
        leads = self.crm.search_leads({"status": "new"})
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0]["name"], "Test Lead 1")

    def test_search_actions(self):
        """Test searching actions with filters"""
        lead_data = {
            "name": "Test Lead",
            "email": "test@example.com",
            "status": "new"
        }
        lead_id = self.crm.create_lead(lead_data)
        action_data1 = {
            "lead_id": lead_id,
            "action_type": "email",
            "details": "Sent initial email"
        }
        action_data2 = {
            "lead_id": lead_id,
            "action_type": "follow-up",
            "details": "Sent follow-up email"
        }
        self.crm.create_action(action_data1)
        self.crm.create_action(action_data2)
        # Search for actions with action_type "email"
        actions = self.crm.search_actions({"action_type": "email"})
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["details"], "Sent initial email")

    def test_search_processes(self):
        """Test searching processes with filters"""
        lead_data = {
            "name": "Test Lead",
            "email": "test@example.com",
            "status": "new"
        }
        lead_id = self.crm.create_lead(lead_data)
        action_data = {
            "lead_id": lead_id,
            "action_type": "email",
            "details": "Sent initial email"
        }
        action_id = self.crm.create_action(action_data)
        # Do NOT manually create a process; it should be created by create_action
        # Search for processes with status "active"
        processes = self.crm.search_processes({"status": "active"})
        self.assertEqual(len(processes), 1)
        self.assertEqual(processes[0]["channel"], "email")
        self.assertEqual(processes[0]["lead_id"], lead_id)
        self.assertEqual(processes[0]["last_action_id"], action_id)

    def test_only_one_process_per_lead(self):
        """Test that there is only one process per lead, even after multiple actions"""
        lead_data = {
            "name": "Test Lead",
            "email": "test@example.com",
            "status": "new"
        }
        lead_id = self.crm.create_lead(lead_data)
        # First action
        action_data1 = {
            "lead_id": lead_id,
            "action_type": "email",
            "details": "Initial contact"
        }
        self.crm.create_action(action_data1)
        # Second action
        action_data2 = {
            "lead_id": lead_id,
            "action_type": "phone",
            "details": "Phone follow-up"
        }
        self.crm.create_action(action_data2)
        # Third action
        action_data3 = {
            "lead_id": lead_id,
            "action_type": "meeting",
            "details": "In-person meeting"
        }
        self.crm.create_action(action_data3)
        # There should still be only one process for this lead
        processes = self.crm.search_processes({"lead_id": lead_id})
        self.assertEqual(len(processes), 1)

    def test_new_lead_has_no_actions_or_process(self):
        """Test that a new lead has no actions or process"""
        lead_data = {
            "name": "Test Lead",
            "email": "test@example.com",
            "status": "new"
        }
        lead_id = self.crm.create_lead(lead_data)
        
        # Check no actions exist
        actions = self.crm.search_actions({"lead_id": lead_id})
        self.assertEqual(len(actions), 0)
        
        # Check no process exists
        processes = self.crm.search_processes({"lead_id": lead_id})
        self.assertEqual(len(processes), 0)

    def test_first_action_creates_process(self):
        """Test that creating first action for a lead automatically creates a process"""
        # Create lead
        lead_data = {
            "name": "Test Lead",
            "email": "test@example.com",
            "status": "new"
        }
        lead_id = self.crm.create_lead(lead_data)
        
        # Create first action
        action_data = {
            "lead_id": lead_id,
            "action_type": "email",
            "details": "Initial contact"
        }
        action_id = self.crm.create_action(action_data)
        
        # Verify process was created
        processes = self.crm.search_processes({"lead_id": lead_id})
        self.assertEqual(len(processes), 1)
        process = processes[0]
        
        # Verify process details
        self.assertEqual(process["lead_id"], lead_id)
        self.assertEqual(process["last_action_id"], action_id)
        self.assertEqual(process["channel"], "email")
        self.assertEqual(process["status"], "active")
        
        # Verify next_followup_datetime is set to 7 days from now
        from datetime import datetime, timedelta
        expected_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        actual_date = datetime.strptime(process["next_followup_datetime"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        self.assertEqual(actual_date, expected_date)

    def test_subsequent_action_updates_process(self):
        """Test that creating subsequent actions updates the existing process"""
        # Create lead and first action
        lead_data = {
            "name": "Test Lead",
            "email": "test@example.com",
            "status": "new"
        }
        lead_id = self.crm.create_lead(lead_data)
        
        # Create first action
        action_data1 = {
            "lead_id": lead_id,
            "action_type": "email",
            "details": "Initial contact"
        }
        action_id1 = self.crm.create_action(action_data1)
        
        # Create second action
        action_data2 = {
            "lead_id": lead_id,
            "action_type": "follow-up",
            "details": "Follow-up contact"
        }
        action_id2 = self.crm.create_action(action_data2)
        
        # Verify process was updated
        processes = self.crm.search_processes({"lead_id": lead_id})
        self.assertEqual(len(processes), 1)
        process = processes[0]
        
        # Verify process was updated with new action
        self.assertEqual(process["last_action_id"], action_id2)
        self.assertEqual(process["channel"], "follow-up")
        
        # Verify next_followup_datetime is still 7 days from now
        from datetime import datetime, timedelta
        expected_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        actual_date = datetime.strptime(process["next_followup_datetime"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        self.assertEqual(actual_date, expected_date)

    def test_lead_with_url(self):
        """Test creating and managing a lead with URL field"""
        # Create lead with URL
        lead_data = {
            "name": "Test Lead",
            "email": "test@example.com",
            "status": "new",
            "url": "https://example.com/profile"
        }
        lead_id = self.crm.create_lead(lead_data)
        
        # Verify lead was created with URL
        lead = self.crm.get_lead(lead_id)
        self.assertEqual(lead["name"], "Test Lead")
        self.assertEqual(lead["email"], "test@example.com")
        self.assertEqual(lead["url"], "https://example.com/profile")
        
        # Test updating URL
        update_data = {"url": "https://example.com/updated-profile"}
        self.crm.update_lead(lead_id, update_data)
        
        # Verify URL was updated
        updated_lead = self.crm.get_lead(lead_id)
        self.assertEqual(updated_lead["url"], "https://example.com/updated-profile")
        
        # Test searching by URL
        search_results = self.crm.search_leads({"url": "https://example.com/updated-profile"})
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0]["id"], lead_id)

    def test_lead_status_default_and_mandatory(self):
        """Test that lead status defaults to 'new' and is mandatory"""
        # Test creating lead without status (should default to 'new')
        lead_data = {
            "name": "Test Lead",
            "email": "test@example.com"
        }
        lead_id = self.crm.create_lead(lead_data)
        lead = self.crm.get_lead(lead_id)
        self.assertEqual(lead["status"], "new")

        # Test that status cannot be set to None
        with self.assertRaises(ValueError):
            self.crm.update_lead(lead_id, {"status": None})

    def test_action_timestamp(self):
        """Test that actions have a timestamp field"""
        # Create lead
        lead_data = {
            "name": "Test Lead",
            "email": "test@example.com"
        }
        lead_id = self.crm.create_lead(lead_data)

        # Create action
        action_data = {
            "lead_id": lead_id,
            "action_type": "email",
            "details": "Initial contact"
        }
        action_id = self.crm.create_action(action_data)

        # Verify action has timestamp
        action = self.crm.get_action(action_id)
        self.assertIn("timestamp", action)
        self.assertIsNotNone(action["timestamp"])

    def test_process_followup_datetime(self):
        """Test that process followup datetime is set to 7 days after last action"""
        # Create lead
        lead_data = {
            "name": "Test Lead",
            "email": "test@example.com"
        }
        lead_id = self.crm.create_lead(lead_data)

        # Create first action
        action_data = {
            "lead_id": lead_id,
            "action_type": "email",
            "details": "Initial contact"
        }
        action_id = self.crm.create_action(action_data)

        # Get the process that was created
        processes = self.crm.search_processes({"lead_id": lead_id})
        self.assertEqual(len(processes), 1)
        process = processes[0]

        # Get the action to check its timestamp
        action = self.crm.get_action(action_id)
        action_timestamp = action["timestamp"]

        # Calculate expected followup datetime (7 days after action timestamp)
        from datetime import datetime, timedelta
        expected_followup = datetime.strptime(action_timestamp, "%Y-%m-%d %H:%M:%S") + timedelta(days=7)
        actual_followup = datetime.strptime(process["next_followup_datetime"], "%Y-%m-%d %H:%M:%S")

        # Verify followup datetime is set correctly
        self.assertEqual(actual_followup, expected_followup)

if __name__ == '__main__':
    unittest.main() 