from fastapi import FastAPI, HTTPException
from typing import Dict, List, Optional, Union
from .crm import CRM
from .models import LeadCreate, LeadUpdate, Lead
import os

def create_app():
    app = FastAPI(title="CRM API", description="REST API for CRM operations")
    db_path = os.environ.get("DATABASE_URL")
    if not db_path:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "crm.db")
    crm = CRM(db_path)

    # Lead endpoints
    @app.post("/leads/", response_model=Lead)
    def create_lead(lead_data: LeadCreate):
        # Check for duplicate email
        existing_leads = crm.search_leads({"email": lead_data.email.lower()})
        if existing_leads:
            raise HTTPException(status_code=400, detail="A lead with this email already exists")
        
        try:
            lead_id = crm.create_lead(lead_data.model_dump())
            return {**lead_data.model_dump(), "id": lead_id}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/leads/{lead_id}", response_model=Lead)
    def get_lead(lead_id: int):
        lead = crm.get_lead(lead_id)
        if lead is None:
            raise HTTPException(status_code=404, detail="Lead not found")
        return lead

    @app.put("/leads/{lead_id}", response_model=Lead)
    def update_lead(lead_id: int, update_data: LeadUpdate):
        # Check if lead exists
        lead = crm.get_lead(lead_id)
        if lead is None:
            raise HTTPException(status_code=404, detail="Lead not found")

        # Check for duplicate email if email is being updated
        if update_data.email.lower() != lead["email"].lower():
            existing_leads = crm.search_leads({"email": update_data.email.lower()})
            if existing_leads:
                raise HTTPException(status_code=400, detail="A lead with this email already exists")

        try:
            crm.update_lead(lead_id, update_data.model_dump())
            return crm.get_lead(lead_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.delete("/leads/{lead_id}", response_model=Dict)
    def delete_lead(lead_id: int):
        lead = crm.get_lead(lead_id)
        if lead is None:
            raise HTTPException(status_code=404, detail="Lead not found")
        crm.delete_lead(lead_id)
        return {"message": "Lead deleted"}

    @app.get("/leads/", response_model=List[Lead])
    def search_leads(status: Optional[str] = None, url: Optional[str] = None):
        filters = {}
        if status:
            filters["status"] = status
        if url:
            filters["url"] = url
        return crm.search_leads(filters)

    # Action endpoints
    @app.post("/actions/", response_model=Dict)
    def create_action(action_data: Dict[str, Union[str, int, float]]):
        # Map 'description' to 'details' for compatibility
        if 'description' in action_data:
            action_data['details'] = action_data.pop('description')
        action_id = crm.create_action(action_data)
        # Return both fields for compatibility
        action = crm.get_action(action_id)
        result = {"id": action_id, **action}
        if 'details' in result:
            result['description'] = result['details']
        return result

    @app.get("/actions/{action_id}", response_model=Dict)
    def get_action(action_id: int):
        action = crm.get_action(action_id)
        if action is None:
            raise HTTPException(status_code=404, detail="Action not found")
        return action

    @app.get("/actions/", response_model=List[Dict])
    def search_actions(action_type: Optional[str] = None):
        filters = {}
        if action_type:
            filters["action_type"] = action_type
        return crm.search_actions(filters)

    # Process endpoints
    @app.get("/processes/{process_id}", response_model=Dict)
    def get_process(process_id: int):
        process = crm.get_process(process_id)
        if process is None:
            raise HTTPException(status_code=404, detail="Process not found")
        return process

    @app.get("/processes/", response_model=List[Dict])
    def search_processes(status: Optional[str] = None):
        filters = {}
        if status:
            filters["status"] = status
        return crm.search_processes(filters)

    return app

def create_app_with_db(db_path: str):
    app = FastAPI(title="CRM API", description="REST API for CRM operations (test db)")
    crm = CRM(db_path)

    # Lead endpoints
    @app.post("/leads/", response_model=Lead)
    def create_lead(lead_data: LeadCreate):
        # Check for duplicate email
        existing_leads = crm.search_leads({"email": lead_data.email.lower()})
        if existing_leads:
            raise HTTPException(status_code=400, detail="A lead with this email already exists")
        
        try:
            lead_id = crm.create_lead(lead_data.model_dump())
            return {**lead_data.model_dump(), "id": lead_id}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/leads/{lead_id}", response_model=Lead)
    def get_lead(lead_id: int):
        lead = crm.get_lead(lead_id)
        if lead is None:
            raise HTTPException(status_code=404, detail="Lead not found")
        return lead

    @app.put("/leads/{lead_id}", response_model=Lead)
    def update_lead(lead_id: int, update_data: LeadUpdate):
        # Check if lead exists
        lead = crm.get_lead(lead_id)
        if lead is None:
            raise HTTPException(status_code=404, detail="Lead not found")

        # Check for duplicate email if email is being updated
        if update_data.email.lower() != lead["email"].lower():
            existing_leads = crm.search_leads({"email": update_data.email.lower()})
            if existing_leads:
                raise HTTPException(status_code=400, detail="A lead with this email already exists")

        try:
            crm.update_lead(lead_id, update_data.model_dump())
            return crm.get_lead(lead_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.delete("/leads/{lead_id}", response_model=Dict)
    def delete_lead(lead_id: int):
        lead = crm.get_lead(lead_id)
        if lead is None:
            raise HTTPException(status_code=404, detail="Lead not found")
        crm.delete_lead(lead_id)
        return {"message": "Lead deleted"}

    @app.get("/leads/", response_model=List[Lead])
    def search_leads(status: Optional[str] = None, url: Optional[str] = None):
        filters = {}
        if status:
            filters["status"] = status
        if url:
            filters["url"] = url
        return crm.search_leads(filters)

    # Action endpoints
    @app.post("/actions/", response_model=Dict)
    def create_action(action_data: Dict[str, Union[str, int, float]]):
        # Map 'description' to 'details' for compatibility
        if 'description' in action_data:
            action_data['details'] = action_data.pop('description')
        action_id = crm.create_action(action_data)
        # Return both fields for compatibility
        action = crm.get_action(action_id)
        result = {"id": action_id, **action}
        if 'details' in result:
            result['description'] = result['details']
        return result

    @app.get("/actions/{action_id}", response_model=Dict)
    def get_action(action_id: int):
        action = crm.get_action(action_id)
        if action is None:
            raise HTTPException(status_code=404, detail="Action not found")
        return action

    @app.get("/actions/", response_model=List[Dict])
    def search_actions(action_type: Optional[str] = None):
        filters = {}
        if action_type:
            filters["action_type"] = action_type
        return crm.search_actions(filters)

    # Process endpoints
    @app.get("/processes/{process_id}", response_model=Dict)
    def get_process(process_id: int):
        process = crm.get_process(process_id)
        if process is None:
            raise HTTPException(status_code=404, detail="Process not found")
        return process

    @app.get("/processes/", response_model=List[Dict])
    def search_processes(status: Optional[str] = None):
        filters = {}
        if status:
            filters["status"] = status
        return crm.search_processes(filters)

    return app

app = create_app() 