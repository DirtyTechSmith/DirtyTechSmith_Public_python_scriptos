# AINT nobody has time for GITLFS
from pathlib import Path

FILE_SIZE_TOO_BIG = 100000000

source_folder = Path('C:\\GitHub\\ProceduWorld_Unreal\\ProceduWorld')


def find_big_files_in_folder(folder: Path, big_size: int = None) -> list[Path]:
    """
    Find files over a certain size in a folder and return them as a list of Path objects.

    Args:
        folder : The folder to search for big files.
        big_size : The size threshold for big files. Defaults to FILE_SIZE_TOO_BIG.

    Returns:
        : A list of Path objects representing the big files found in the folder.
    """

    if big_size is None:
        big_size = FILE_SIZE_TOO_BIG

    big_files: list[Path] = []
    for file in folder.glob('**/*'):
        if file.is_file():
            if file.stat().st_size > big_size:
                big_files.append(file)

    return big_files


def delete_files(files: list[Path]):
    """
        Deletes the files provided in the list.

        Args:
            files: A list of files to be deleted.

        """
    for file in files:
        file.unlink()


if __name__ == '__main__':
    import pprint

    the_big_files = find_big_files_in_folder(source_folder)
    print(f'num big files: {len(the_big_files)}')
    pprint.pprint(the_big_files)
    # delete_files(the_big_files)
