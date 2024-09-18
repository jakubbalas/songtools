from pathlib import Path
from abc import ABC


class UnsupportedSongType(Exception):
    pass


class SongFile(ABC):
    def __init__(self, path: Path):
        self.path = path

    def get_path(self) -> Path:
        return self.path

    @classmethod
    def construct(cls, file: Path):
        if not file.exists():
            raise FileNotFoundError(f"Song File {file} does not exist.")
        if file.suffix == ".mp3":
            return MP3File(file)
        else:
            raise UnsupportedSongType(f"Song File {file} is not supported.")

    def get_artist(self) -> str:
        pass


class MP3File(SongFile):
    def __init__(self, file: Path):
        super().__init__(file)

    def get_artist(self) -> str:
        pass
