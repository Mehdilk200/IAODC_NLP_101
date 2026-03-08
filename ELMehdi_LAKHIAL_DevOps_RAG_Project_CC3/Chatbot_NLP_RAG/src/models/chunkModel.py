from .BaseDataModel import BaseDataModel
from database.db_schema import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne
from typing import Optional
from langchain_chroma import Chroma

class chunkModel(BaseDataModel):

        def __init__(self, db_client):
                super().__init__(db_client = db_client)
                self.collection = self.db[DataBaseEnum.collection_chunks_name.value]

        @classmethod
        async def instance(cls, db_client: object):
                instance = cls(db_client=db_client) 
                await instance.init_collection()
                return instance

        async def init_collection(self):

                self.collection = self.db[DataBaseEnum.collection_chunks_name.value]
                
                indexes = DataChunk.get_indexes()
                
                for index in indexes:
                        try:
                                await self.collection.create_index(
                                        index["key"], 
                                        unique=index.get("unique", False), 
                                        name=index.get("name")
                                )
                                print(f"DEBUG: Chunk Index {index.get('name')} verified.") 
                        except Exception as e:
                                print(f"ERROR: Failed to create chunk index: {e}")

        async def create_chunk(self, chunk: DataChunk):

                resulta = await self.collection.insert_one(chunk.model_dump(exclude_unset=True , by_alias=True))
                chunk.id = str(resulta.inserted_id)
                return chunk
        
        async def get_chunk(self, chunk_id: str):

                corsur = self.collection.find_one({"_id": ObjectId(chunk_id)})   
                if corsur is None:
                        return None
                else:
                        corsur['_id'] = str(corsur['_id'])
                        return DataChunk(**corsur)        

        async def create_chunks_batch(self, chunks: list[DataChunk] , batch_size: int = 100) -> int:
                
                for i in range(0, len(chunks), batch_size):
                        batch = chunks[i:i + batch_size]
                        operations = [InsertOne(chunk.model_dump(exclude_unset=True , by_alias=True)) for chunk in batch]
                        await self.collection.bulk_write(operations)

                return len(chunks)   
        
        
        async def delete_chunks_by_project_id(self, project_id: str) -> int:

                try:
                        result = await self.collection.delete_many({"chunk_project_id": project_id})
                        return result.deleted_count
                
                except Exception as e:
                        print(f"Error deleting chunks: {e}")
                        return 0

        async def upsert_project_chunks_to_chroma(
                self,
                vector_store: Chroma,
                project_id: str,
                role: Optional[str] = None,
                batch_size: int = 200 ) -> int:

                query = {"chunk_project_id": project_id}
                if role:
                       query["metadata.allowed_roles"] = role  

                total = 0
                cursor = self.collection.find(query)

                batch = []
                async for doc in cursor:
                        batch.append(doc)
                        if len(batch) >= batch_size:
                                total += self._upsert_batch(vector_store, batch)
                                batch = []

                if batch:
                        total += self._upsert_batch(vector_store, batch)

                return total

        def _upsert_batch(self, vector_store: Chroma, docs: list[dict]) -> int:
                texts = []
                metadatas = []
                ids = []

                for d in docs:
                        ids.append(str(d["_id"]))
                        texts.append(d.get("chunk_text", ""))

                        md = d.get("metadata", {}) or {}
                        
                        metadatas.append({
                                "chunk_project_id": str(d.get("chunk_project_id", "")),
                                "allowed_roles": str(md.get("allowed_roles", "")),
                                "source": str(md.get("source", "")),
                                "section": str(md.get("section", "")),
                                "file_name": str(d.get("file_name", "")),
                                "chunk_order": int(d.get("chunk_order", 0)),
                        })

                vector_store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
                return len(docs)