import click
import mutagen
import math

from abc import ABC, abstractmethod
from pathlib import Path
from songtools import config as config


SUPPORTED_MUSIC_TYPES = [".mp3", ".flac", ".wav", ".m4a"]


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
    def artists(self) -> str: ...

    @property
    @abstractmethod
    def title(self) -> str: ...

    @property
    @abstractmethod
    def bpm(self) -> float: ...

    @property
    @abstractmethod
    def year(self) -> int: ...

    @property
    @abstractmethod
    def key(self) -> str: ...

    @property
    @abstractmethod
    def energy(self) -> int: ...

    @property
    @abstractmethod
    def genre(self) -> str: ...

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
        if self.path.stem.count("-") != 1 and (
            not self.metadata or not (self.metadata.artists or self.metadata.title)
        ):
            raise UnableToExtractData(
                f"Unable to extract data from metadata or filename: {self.path}."
            )

    def _load_metadata(self) -> MetaRetriever:
        sfx = self.path.suffix.lower()
        if sfx == ".mp3" or sfx == ".wav":
            return ID3File(self.path)
        elif sfx == ".flac":
            return FlacFile(self.path)
        elif sfx == ".m4a":
            return M4AFile(self.path)
        else:
            raise UnsupportedSongType(f"Song File {self.path} is not supported.")

    @property
    def artists(self) -> list[str]:
        """Retrieve artists from metadata, or filename if metadata is not present.

        :return: List of all artists collaborating on a song.
        """
        if self.metadata and self.metadata.artists:
            artists = self.metadata.artists
        else:
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
    def file_size_kb(self) -> int:
        return math.ceil(self.path.stat().st_size / 1024)

    @property
    def bpm(self) -> float:
        if not self.metadata:
            return 0.0
        return self.metadata.bpm

    @property
    def genre(self) -> str:
        if not self.metadata:
            return (
                str(self.path.relative_to(config.backlog_path))
                .split("/")[0]
                .split("-")[0]
            )
        return self.metadata.genre

    @property
    def year(self) -> int:
        if not self.metadata:
            return 0
        return self.metadata.year

    @property
    def key(self) -> str:
        if not self.metadata:
            return ""
        return self.metadata.key

    @property
    def energy(self) -> int:
        if not self.metadata:
            return 0
        return self.metadata.energy

    def _get_artists_from_filename(self) -> str:
        """Fallback method to extract artists from filename."""
        return self.path.stem.split("-")[0] if self.path.stem.count("-") == 1 else ""

    def _get_title_from_filename(self) -> str:
        """Fallback method to extract title from filename."""
        return self.path.stem.split("-")[1] if self.path.stem.count("-") == 1 else ""


class ID3File(MetaRetriever):
    @property
    def artists(self) -> str:
        return self._get_tag("TPE1")

    @property
    def title(self) -> str:
        return self._get_tag("TIT2")

    @property
    def bpm(self) -> float:
        bpm = self._get_tag("TBPM")
        return float(bpm) if bpm else 0.0

    @property
    def year(self) -> int:
        release_date = self.metadata.get("TDRC")
        return release_date.text[0].year if release_date else 0

    @property
    def key(self) -> str:
        key = self._get_tag("TKEY")
        if not key:
            key_part = self._get_tag("COMM::eng")
            if key_part and "ENERGY" in key_part:
                key = key_part.split("-")[0].strip()
        return key if key else ""

    @property
    def energy(self) -> int:
        energy = self._get_tag("TXXX:EnergyLevel")
        if not energy:
            energy_part = self._get_tag("COMM::eng")
            if energy_part and "Energy" in energy_part:
                energy = energy_part.split(" ")[-1].strip()
        return int(energy) if energy else 0

    @property
    def genre(self) -> str:
        genre = self._get_tag("TCON")
        return genre if genre else ""

    def _get_tag(self, tag: str) -> str | None:
        tag = self.metadata.get(tag)
        return tag.text[0] if tag else None


class FlacFile(MetaRetriever):
    @property
    def artists(self) -> str:
        return ", ".join(self.metadata.get("artist", [""]))

    @property
    def title(self) -> str:
        return ", ".join(self.metadata.get("title", [""]))

    @property
    def bpm(self) -> float:
        return float(self._get_tag("bpm", "0"))

    @property
    def year(self) -> int:
        date = int(self._get_tag("date").split("-")[0])
        if not date:
            date = int(self._get_tag("release date").split("-")[0])
        return date

    @property
    def key(self) -> str:
        key = self._get_tag("initialkey")
        if not key:
            key_part = self._get_tag("comment")
            if key_part and "ENERGY" in key_part:
                key = key_part.split("-")[0].strip()
        return key

    @property
    def energy(self) -> int:
        energy = self._get_tag("energylevel")
        if not energy:
            energy_part = self._get_tag("comment")
            if energy_part and "Energy" in energy_part:
                energy = energy_part.split(" ")[-1].strip()
        return int(energy) if energy else 0

    @property
    def genre(self) -> str:
        return self._get_tag("genre")

    def _get_tag(self, tag: str, default="") -> str:
        return self.metadata.get(tag, [default])[0]


class M4AFile(MetaRetriever):
    @property
    def artists(self) -> str:
        return self._get_tag("©ART")

    @property
    def title(self) -> str:
        return self._get_tag("©nam")

    @property
    def bpm(self) -> float:
        return float(self._get_tag("tmpo", "0"))

    @property
    def year(self) -> int:
        try:
            return int(self._get_tag("©day", "0").split("-")[0])
        except ValueError:
            return 0

    @property
    def key(self) -> str:
        key = ""
        comment = self._get_tag("©cmt")
        if comment and "ENERGY" in comment:
            key = comment.split("-")[0].strip()
        return key

    @property
    def energy(self) -> int:
        energy = 0
        comment = self._get_tag("©cmt")
        if comment and "Energy" in comment:
            energy = int(comment.split(" ")[-1].strip())
        return energy

    @property
    def genre(self) -> str:
        return self._get_tag("©gen")

    def _get_tag(self, tag: str, default="") -> str:
        return self.metadata.get(tag, [default])[0]
