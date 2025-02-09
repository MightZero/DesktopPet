

import json
import os

class Config:
    _instance = None
    _settings = None

    def __new__(cls, file_path='config.json'):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._settings = cls._load_settings(file_path)
        return cls._instance
    @classmethod
    def _load_settings(cls,file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} does not exist.")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    @classmethod
    def get_setting(cls, key, default=None):
        return cls._settings.get(key, default)