from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Commit:
    timestamp: datetime
    author_id: str


@dataclass
class Tag:
    name: str
    timestamp: datetime


@dataclass
class RepoSnapshot:
    commits: List[Commit]
    tags: List[Tag]
    file_paths: List[str]
