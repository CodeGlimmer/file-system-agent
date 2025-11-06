from enum import Enum


class FileType(Enum):
    FILE = "file"
    DIRECTORY = "directory"
    LINK = "link"
