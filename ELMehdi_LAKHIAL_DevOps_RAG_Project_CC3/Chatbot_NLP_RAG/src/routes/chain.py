from fastapi import FastAPI
from fastapi import APIRouter
from dotenv import load_dotenv
from helpers.config import  get_settings
import os
from models.enums import roles
from fastapi import APIRouter, Depends, Request
from .schema.ChatRequest import ChatRequest
from helpers.config import settings
from database.db_schema.project_s import Project
from models.ProjectModel import ProjectModel
from countroller.RetrievalController import RAGController
from fastapi import HTTPException

chain_router = APIRouter()

@chain_router.get("/chain")
def read_chain():
        app_name = get_settings().APP_NAME
        app_version = get_settings().APP_VERSION
        return {"Chain": "This is the chain route",
                "message": f"App Name: {app_name}, App Version: {app_version}"} 


@chain_router.post("/chat/{id_load}")
async def chat_with_docs(
    request: Request,
    id_load: roles,
    payload: ChatRequest
):

    
    project_model = await ProjectModel.instance(
        db_client=request.app.mongodb_client
    )

    project = await project_model.get_project_by_id(
        role = id_load.value
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    
    
    rag_controller = RAGController(
        db_client=request.app.mongodb_client
    )
    
    try:
        
        answer = await rag_controller.ask_question(
            query=payload.question,
            project_id=str(project.id),
            role = id_load.value
        )

        return {
            "allowed_roles": id_load.value,
            "question": payload.question,
            "answer": answer,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))