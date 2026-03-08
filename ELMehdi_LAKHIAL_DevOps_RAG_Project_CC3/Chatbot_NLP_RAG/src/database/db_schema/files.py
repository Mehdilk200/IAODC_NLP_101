
from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field , ConfigDict , field_validator
from bson.objectid import ObjectId
from pydantic import  GetJsonSchemaHandler
from pydantic_core import core_schema
from typing import Any , Annotated
from pydantic import BaseModel, Field, ConfigDict, GetJsonSchemaHandler
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue


class _ObjectIdPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(lambda x: ObjectId(x)),
                ]),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: str(x)),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: Any, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return handler(core_schema.str_schema())
    
PyObjectId = Annotated[ObjectId, _ObjectIdPydanticAnnotation]

class FileAsset(BaseModel):
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    project_id: str = Field(..., min_length=1)
    name_file: str = Field(..., min_length=1)
    path_file: str = Field(..., min_length=1) 
    type_file: str = Field(..., min_length=1)
    size_file: int = Field(..., gt=0)
    status_chunk: Optional[bool] = False
    date_pushed_at: datetime = Field(default_factory=datetime.now)
    
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )