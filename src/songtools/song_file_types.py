import click
import mutagen
import math

from abc import ABC, abstractmethod
from pathlib import Path
from songtools import config as config


class UnsupportedSongType(Exception):
    pass


class UnableToExtractData(Exception):
    pass


class MetaRetriever(ABC):
    def __init__(self, path: Path) -> None:
        self.metadata = mutagen.File(path)
        if self.metadata is None:
            raise UnableToExtractData()

    @property
    @abstractmethod
    def artists(self) -> str:
        ...

    @property
    @abstractmethod
    def title(self) -> str:
        ...

    @property
    @abstractmethod
    def bpm(self) -> int:
        ...

    @property
    def duration_seconds(self) -> int:
        return math.ceil(self.metadata.info.length)


class SongFile:
    def __init__(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"Song File {path} does not exist.")

        self.path: Path = path
        self.metadata: MetaRetriever | None = None
        try:
            self.metadata: MetaRetriever = self._load_metadata()
        except (mutagen.MutagenError, UnableToExtractData) as e:
            click.secho(f"Could not read metadata from file {path}.", fg="yellow")
            click.secho(e, fg="yellow", bg="white")
        self._check_naming()

    def _check_naming(self):
        if self.path.stem.count("-") != 1 and (not self.metadata or not (self.metadata.artists or self.metadata.title)):
            raise UnableToExtractData(
                f"Unable to extract data from metadata or filename: {self.path}."
            )

    def _load_metadata(self) -> MetaRetriever:
        if self.path.suffix == ".mp3":
            return MP3File(self.path)
        elif self.path.suffix == ".flac":
            return FlacFile(self.path)
        else:
            raise UnsupportedSongType(f"Song File {self.path} is not supported.")


    @property
    def artists(self) -> list[str]:
        """Retrieve artists from metadata, or filename if metadata is not present.

        :return: List of all artists collaborating on a song.
        """
        if self.metadata and self.metadata.artists:
            artists = self.metadata.artists
        else :
            click.secho(
                f"No artist metadata for song {self.path}, using file name.",
                fg="yellow",
            )
            artists = self._get_artists_from_filename()
        return [a.strip() for a in artists.split(", ")]

    @property
    def duration_seconds(self) -> int:
        """
        :return: Duration of the song in seconds
        """
        if self.metadata is None:
            click.secho(
                "Can't determine duration of song without metadata.",
                fg="yellow",
                bg="red",
            )
            return 0
        return self.metadata.duration_seconds

    @property
    def title(self) -> str:
        if self.metadata and self.metadata.title:
            title = self.metadata.title
        else:
            click.secho(
                f"No title metadata for song {self.path}, using file name.", fg="yellow"
            )
            title = self._get_title_from_filename()

        return title.strip()

    @property
    def bpm(self) -> int:
        if not self.metadata:
            return 0
        return self.metadata.bpm

    @property
    def genre(self) -> str:
        """super specific for my folder structure, will be removed"""
        return str(self.path.relative_to(config.backlog_path)).split("/")[0].split("-")[0]

    def _get_artists_from_filename(self) -> str:
        """Fallback method to extract artists from filename."""
        return self.path.stem.split("-")[0]

    def _get_title_from_filename(self) -> str:
        """Fallback method to extract title from filename."""
        return self.path.stem.split("-")[1]


class MP3File(MetaRetriever):
    @property
    def artists(self) -> str:
        return self._get_tag("TPE1")

    @property
    def title(self) -> str:
        return self._get_tag("TIT2")

    @property
    def bpm(self) -> int:
        bpm = self._get_tag("TBPM")
        return int(bpm) if bpm else 0

    def _get_tag(self, tag: str) -> str | None:
        tag = self.metadata.get(tag)
        return tag.text[0] if tag else None

class FlacFile(MetaRetriever):
    @property
    def artists(self) -> str:
        return ", ".join(self.metadata.get("artist", ""))

    @property
    def title(self) -> str:
        return ", ".join(self.metadata.get("title", ""))

    @property
    def bpm(self) -> int:
        return int(self.metadata.get("bpm", [0])[0])
