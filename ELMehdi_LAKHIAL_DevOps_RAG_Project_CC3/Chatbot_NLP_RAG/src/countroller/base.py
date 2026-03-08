from helpers.config import get_settings ,settings
import os
class BaseController :
        def __init__(self):
                self.config = get_settings()
                self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                self.files_dir = os.path.join(self.base_dir, "assets/upload_file")
        def get_config(self):
                return self.config
