from .base import BaseController
from fastapi import UploadFile
from models.enums import Const
from models.enums.roles import roles
import os

class ProjectController(BaseController):
        
        def __init__(self):
                super().__init__()
        
        def create_project(self, project_id: roles):
                # Logic to create a new project
                return {"project_id ": project_id.value, "status": "created"}
        
        def get_project_path(self, project_id: roles):
                project_id_val = project_id.value if hasattr(project_id, 'value') else project_id
                project_dir = os.path.join(self.files_dir, project_id_val)
                

                if os.path.exists(project_dir):
                        
                        return project_dir
                else: 
                        os.makedirs(project_dir)

                        return project_dir