from pathlib import Path


IRRELEVANT_SUFFIXES = [".jpg", ".png", ".m3u", ".nfo", ".cue", ".txt"]


def clean_backlog_folder(backlog_folder: Path) -> None:
    """Take the backlog folder and clean it.
    It will:
     - Remove all empty folders recursively

    :param Path backlog_folder: Root path to the backlog folder
    """
    remove_irrelevant_files(backlog_folder)
    remove_empty_folders(backlog_folder)


def remove_empty_folders(root_path: Path) -> None:
    """Recursively remove all empty folders.
    It stops at 100 iterations of nesting to prevent any weird infinite loops.

    :param Path root_path: Root path to start the search
    """
    empties_exists = True
    nest = 0
    max_nested = 100
    while empties_exists and nest < max_nested:
        empties_exists = False
        for folder in sorted(
            root_path.rglob("*"), key=lambda p: len(p.parts), reverse=True
        ):
            if folder.is_dir() and not any(folder.iterdir()):
                folder.rmdir()
                empties_exists = True
        nest += 1


def remove_irrelevant_files(root_path: Path) -> None:
    """Remove all irrelevant files from the backlog folder.
    It removes all files that are not music files.
    This is a blacklist approach rather than a whitelist,
    so I won't delete more exotic music suffixes by accident.

    :param Path root_path: Root path to the backlog folder
    """
    for folder in root_path.rglob("*"):
        if folder.is_file() and folder.suffix in IRRELEVANT_SUFFIXES:
            folder.unlink()
