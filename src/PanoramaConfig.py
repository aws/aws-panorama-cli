from enum import Enum
import os.path

boolean_true_values = "y"
boolean_false_values = "n"

class ConfigType(Enum):
    FILE = 0
    DIR = 1
    STRING = 2
    BOOLEAN = 3

def validate_file(path):
    return os.path.isfile(path)


def validate_dir(path):
    return os.path.isdir(path)


def validate_string(string):
    return True

def validate_boolean(boolean):
    return (boolean.lower() in boolean_true_values) or (boolean.lower() in boolean_false_values)

validate_dict = {ConfigType.FILE: validate_file,
                 ConfigType.DIR: validate_dir,
                 ConfigType.STRING: validate_string,
                 ConfigType.BOOLEAN: validate_boolean
                 }

class Config:
    def __init__(self, key, config_type):
        self.key = key
        self.config_type = config_type

    def validate(self, value):
        validate_method = validate_dict[self.config_type]
        return validate_method(value)
