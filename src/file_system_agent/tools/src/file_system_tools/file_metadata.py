from typing import TypedDict, Literal


class FileMetadata(TypedDict):
    file_name: str
    full_name: str
    file_type: Literal["file", "directory", "link"]
    size: int
    target: str | None
    
