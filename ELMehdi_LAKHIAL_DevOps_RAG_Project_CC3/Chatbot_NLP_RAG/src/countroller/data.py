from countroller.base import BaseController
from fastapi import UploadFile
from models.enums import Const
from .project import ProjectController
import random 
import re
class DataController(BaseController):

        def __init__(self):

                super().__init__()
                self.size_scale = 1024 * 1024  # Scale for converting bytes to megabytes

        def validate_file(self,file: UploadFile):
                # Check file size
                contents = file.file.read()
                if len(contents) > self.config.MAX_FILE_SIZE * self.size_scale:
                        return False , Const.file_size_error.value
                
                # Check file type
                if file.content_type not in self.config.FILE_ALLOWED_EXTNSIONS:

                        return False , Const.file_type_error.value
                
                # Process the file (for demonstration, we just return its name and size)
                return True , f"filename : {file.filename}, size: {len(contents)/10000} MB , status : True , message : {Const.file_validation.value} "
        
        

        def file_name_generator(self, file_origin: str, project_id: str):
                file_extension = re.search(r'\.(\w+)$', file_origin)
                name_without_ext = re.sub(r"\.[^.]+$", "", file_origin)
                
                extension = file_extension.group(1) if file_extension else "txt"
                clean_name = re.sub(r'[^a-zA-Z0-9]', '_', name_without_ext)

                return f"{clean_name}_{project_id}_{random.randint(1000, 9999)}.{extension}"

                
