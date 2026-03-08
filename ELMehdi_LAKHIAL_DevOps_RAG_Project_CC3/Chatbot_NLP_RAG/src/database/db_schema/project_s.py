from models.enums.roles import roles
from pydantic import BaseModel, Field , ConfigDict , field_validator
from typing import Optional 
from bson.objectid import ObjectId
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import core_schema
from bson import ObjectId
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

class Project(BaseModel):
        
        id : Optional[PyObjectId] =  Field(default=None, alias="_id")
        project_id : roles = Field(alias="project_id")
        model_config = ConfigDict(populate_by_name= True , arbitrary_types_allowed=True , json_encoders={ObjectId: str})

        @field_validator('project_id')
        def validate_project_id(cls, value):
                if not isinstance(value, roles):
                        raise ValueError("project_id must be an instance of roles enum")
                return value


        @classmethod 
        def get_indexes(cls) -> list[tuple[str, int]]:
                return [{
                    "key": [
                        ("project_id", 1)
                    ],
                    "name" : "project_id_index",
                    "unique": True
                }]

