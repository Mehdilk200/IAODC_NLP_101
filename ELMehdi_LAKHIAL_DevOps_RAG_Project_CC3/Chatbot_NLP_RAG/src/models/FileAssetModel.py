from .BaseDataModel import BaseDataModel
from database.db_schema.files import FileAsset
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from typing import List, Optional

class FileAssetModel(BaseDataModel):

    def __init__(self, db_client):
        super().__init__(db_client=db_client)
        self.collection = self.db[DataBaseEnum.collection_metadata_name.value]

    @classmethod
    async def instance(cls, db_client: object):
        instance = cls(db_client=db_client) 
        await instance.init_collection()
        return instance

    async def init_collection(self):
        self.collection = self.db[DataBaseEnum.collection_metadata_name.value]
        indexes = FileAsset.get_indexes()
        
        for index in indexes:
            try:
                await self.collection.create_index(
                    index["key"], 
                    unique=index.get("unique", False), 
                    name=index.get("name")
                )
                print(f"DEBUG: FileAsset Index {index.get('name')} verified.") 
            except Exception as e:
                print(f"ERROR: Failed to create metadata index: {e}")

    async def create_asset(self, asset: FileAsset):

        asset_dict = asset.model_dump(exclude_unset=True, by_alias=True)
        
        if "_id" in asset_dict and asset_dict["_id"] is None:
            del asset_dict["_id"]

        result = await self.collection.insert_one(asset_dict)
        asset.id = str(result.inserted_id)
        
        print(f"DEBUG: Metadata saved for file {asset.name_file} with ID: {asset.id}")
        return asset

    async def get_asset_by_name(self, file_name: str):

        asset_data = await self.collection.find_one({"name_file": file_name})
        if asset_data:
            asset_data['id'] = str(asset_data['_id'])
            return FileAsset(**asset_data)
        return None

    async def get_all_assets_by_project(self, project_id: str) -> List[FileAsset]:
        
        docs = await self.collection.find({"project_id": ObjectId(project_id) if isinstance(project_id, str) else project_id}).to_list(length=None)

        assets = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            assets.append(FileAsset(**doc))
        return assets

    async def delete_asset_by_name(self, file_name: str) -> bool:
        
        result = await self.collection.delete_one({"name_file": file_name})
        return result.deleted_count > 0