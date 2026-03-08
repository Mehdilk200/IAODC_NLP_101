from fastapi import APIRouter, FastAPI , Depends , UploadFile , status , Request
from helpers.config import settings , get_settings
from fastapi.responses import JSONResponse
from database.db_schema.files import FileAsset
import os
from datetime import datetime
from countroller.data import DataController 
from countroller.project import ProjectController
from countroller.procces import ProcessController
from routes.schema.data_validation import DataValidationRequest
import aiofiles 
from models.enums import Const
from models.enums import roles
from models.ProjectModel import ProjectModel
from database.db_schema.project_s import Project
from database.db_schema.chunk_rag import DataChunk , ChunkMetadata
from models.chunkModel import chunkModel
from middlewares.auth_guard import get_current_user
from typing import Optional
from bson import ObjectId



data_load_router = APIRouter()


@data_load_router.post("/data-load/{id_load}")

async def read_data_load(request: Request, id_load: roles , file: UploadFile, app_settings: settings = Depends(get_settings)):

        project_model =  await ProjectModel.instance(db_client=request.app.mongodb_client)

        project = await project_model.get_project_by_id(role=id_load.value)

        validation , signal_ms = DataController().validate_file(file=file)

        if not validation:

                return JSONResponse(content={"status": signal_ms}, status_code=status.HTTP_400_BAD_REQUEST)
        
        await file.seek(0)

        project_dir_path = ProjectController().get_project_path(project_id=id_load.value)

        file_name = DataController().file_name_generator(file_origin=file.filename, project_id=id_load.value)

        file_location = os.path.join(project_dir_path, file_name)

        try:
                async with aiofiles.open(file_location, 'wb') as f:
                        while content_chunk := await file.read(app_settings.FILE_UPLOAD_CHANK_SIZE)  :# Read the file content asynchronously
                              await f.write(content_chunk)  # Write the content to the destination file asynchronously
        except Exception as e:
                return JSONResponse(
                        content={
                                "status": f"{Const.file_upload_error.value} : {str(e)}"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:   
                metadata = FileAsset(
                        name_file=file_name,
                        path_file=file_location,
                        type_file=file.content_type,
                        project_id=str(project.id),
                        size_file=os.path.getsize(file_location)
                )
                file_metadata = metadata.model_dump(exclude_unset=True , by_alias=True)
                
                print(f"DEBUG: Saving metadata for project {project.id}...", flush=True)
                
                result = await request.app.mongodb_client[app_settings.MONGODB_DB_NAME][app_settings.MONGODB_COLLECTION_NAME].insert_one(file_metadata)
                print(f"DEBUG: Inserted with ID: {result.inserted_id}", flush=True)
                

                return JSONResponse(
                        content={
                                "status": Const.Data_load_success.value, 
                                "file_name": file_name, 
                                "project_id": str(project.id), 
                                "saved_to_db": True,
                                "role": id_load.value,
                                "metadata_id": str(result.inserted_id)
                                }, 
                        status_code=status.HTTP_200_OK)

        except Exception as e:
                print(f"ERROR: Failed to save metadata to DB: {str(e)}", flush=True)
                
                return JSONResponse(
                        content={
                                "status": "File saved but failed to insert metadata into DB",
                                "error": str(e)
                                }, 
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@data_load_router.post("/proccese/{id_load}")
async def validate_data_load(request: Request ,id_load: roles , payload: DataValidationRequest ):
        
        file_id = payload.file_name
        Process_controller = ProcessController(project_id=id_load)
        file_content = Process_controller.get_content_file(file_name=file_id)
        do_reset = payload.re_set

        project_model = await ProjectModel.instance(db_client=request.app.mongodb_client)
        project = await project_model.get_project_by_id(role=id_load.value)
        
        chun_model = await chunkModel.instance(db_client=request.app.mongodb_client) 
        
        


        chunks = Process_controller.process_file(
                file_name=file_id , 
                chunk_size=payload.chunk_size , 
                overlap_size=payload.overlap_size , 
                file_content=file_content
                )

        if chunks is None or len(chunks) == 0:

                return JSONResponse(content={"status": Const.file_not_found.value}, status_code=status.HTTP_404_NOT_FOUND)
        record = [
                DataChunk(
                        file_name=file_id,
                        chunk_project_id=str(project.id),
                        chunk_order=i,
                        chunk_text=chunk.page_content if hasattr(chunk, 'page_content') else str(chunk),
                        metadata=ChunkMetadata(
                                source=file_id,
                                section=f"Section {i+1}",
                                has_code=Process_controller.has_code(chunk),
                                allowed_roles=id_load.value
                        )
                ) for i, chunk in enumerate(chunks)
        ]

        if do_reset == 1 :
              delete = await chun_model.delete_chunks_by_project_id(project_id=project.id)
              return JSONResponse(content={"status": f"Deleted {delete} chunks for project {project.id}"}, status_code=status.HTTP_200_OK)      
        else :  
                db = request.app.mongodb
                ready = await db["files_metadata"].update_one({"name_file": file_id}, {"$set": {"status_chunk": True}} )
                                                              
        no_chunks = await chun_model.create_chunks_batch(chunks=record)

        return JSONResponse(content={"status": f"Chunks created: \n {no_chunks}  \n {Const.procceing_file_success}"}, status_code=status.HTTP_200_OK)



@data_load_router.get("/files-metadata", summary="List uploaded files (hierarchy)")
async def list_files(
    request:     Request,
    owner_only:  bool           = False,
    type_filter: Optional[str]  = None,
    current=Depends(get_current_user),
):
    caller_role = current.get("role")
    caller_id   = current.get("user_id")

    db    = request.app.mongodb
    query = {}

    if caller_role == "admin":
        # admin yshof ga3 les fichiers
        if owner_only:
            # filter b path_file li fih role=admin
            query["path_file"] = {"$regex": f"/{caller_role}/", "$options": "i"}

    elif caller_role == "manager":
        # manager yshof f9at les fichiers li upload b id_load=manager
        query["path_file"] = {"$regex": "/manager/", "$options": "i"}

    elif caller_role == "user":
        # user yshof f9at les fichiers li upload b id_load=user
        query["path_file"] = {"$regex": "/user/", "$options": "i"}

    # filter b type
    if type_filter:
        type_map = {
            "pdf":   "application/pdf",
            "excel": "application/vnd",
            "word":  "application/msword",
            "csv":   "text/csv",
        }
        mapped = type_map.get(type_filter.lower())
        if mapped:
            query["type_file"] = {"$regex": mapped, "$options": "i"}

    cursor = db["files_metadata"].find(query, {
        "_id":        1,
        "project_id": 1,
        "name_file":  1,
        "path_file":  1,
        "type_file":  1,
        "size_file":  1,
        "status_chunk": 1,
    })

    items = []
    async for doc in cursor:
        # extract id_load from path_file
        # path format: /app/src/assets/upload_file/{id_load}/{filename}
        path  = doc.get("path_file", "")
        parts = path.split("/")
        # id_load is the folder just before the filename
        id_load = parts[-2] if len(parts) >= 2 else "unknown"

        # check if processed — look in chunks_rag collection
        chunk_count = await db["chunks_rag"].count_documents({
            "project_id": doc.get("project_id")
        })

        items.append({
            "id":          str(doc["_id"]),
            "project_id":  doc.get("project_id", ""),
            "file_name":   doc.get("name_file", ""),
            "path_file":   path,
            "type_file":   doc.get("type_file", ""),
            "size":        doc.get("size_file", 0),
            "id_load":     id_load,
            "processed":   chunk_count > 0,
            "chunk_count": chunk_count,
            "processed":   bool(doc.get("status_chunk", False)),
        })

    return {
        "total": len(items),
        "items": items,
    }