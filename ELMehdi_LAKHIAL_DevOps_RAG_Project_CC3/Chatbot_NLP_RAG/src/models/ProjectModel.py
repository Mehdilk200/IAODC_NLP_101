from .BaseDataModel import BaseDataModel
from database.db_schema import Project
from bson.objectid import ObjectId
from typing import  List
from models.enums.roles import roles
from .enums.DataBaseEnum import DataBaseEnum


class ProjectModel(BaseDataModel):

        def __init__(self, db_client):
                super().__init__(db_client = db_client)
                self.collection = self.db[DataBaseEnum.collection_project_name.value]

        @classmethod
        async def instance(cls, db_client: object):
                instance = cls(db_client=db_client) 
                await instance.init_collection()
                return instance
        
        async def init_collection(self):
                self.collection = self.db[DataBaseEnum.collection_project_name.value]
                indexes = Project.get_indexes()
                for index in indexes:
                        try:
                                await self.collection.create_index(
                                        index["key"], 
                                        unique=index.get("unique", False), 
                                        name=index.get("name")
                                )
                                print(f"DEBUG: Index {index.get('name')} checked/created.")
                        except Exception as e:
                                print(f"ERROR: Failed to create index: {e}")
                
        async def create_project(self, project: Project):

                project_dict = project.model_dump(exclude_unset=True , by_alias=True)
                if "_id" in project_dict and project_dict["_id"] is None:
                       del project_dict["_id"]

                result = await self.collection.insert_one(project_dict)

                project.id = str(result.inserted_id)
                
                print(f"DEBUG: New Project Created with ID: {project.id}", flush=True)
                return project
        
        async def get_project_by_id(self, role: roles):

                role_val = role.value if hasattr(role, 'value') else role

                project_data = await self.collection.find_one({"project_id": role_val})

                if project_data is  None:
                        project_r = Project(project_id = role_val)
                        project = await self.create_project(project=project_r)
                        return project
                else:
                        project_data['id'] = str(project_data['_id']) 
                        project_data.pop('_id', None)
                        if 'project_id' not in project_data:
                              project_data['project_id'] = project_data.get('project_id', role_val)
                        return Project(**project_data)

        async def get_all_projects(self, page: int = 1, page_size: int = 10) -> List[Project]:

                total_projects = await self.collection.count_documents({})
                total_pages = total_projects  // page_size
                if total_pages % page_size > 0:
                        total_pages += 1
                cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)
                projects = []
                async for doc in cursor:
                        projects.append(Project(**doc))
                return projects, total_pages
