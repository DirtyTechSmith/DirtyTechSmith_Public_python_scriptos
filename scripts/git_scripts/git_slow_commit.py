import sys

import git
import logging
import pprint
from pathlib import Path

logger = logging.getLogger(__name__)
logger.level = logging.DEBUG
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

NUM_FILES = 100
CHUNK_SIZE = 100 * 1024 * 1024  # 100 MB
# Your project's git root folder
PROJECT_GIT_ROOT = Path('C:\\GitHub\\')
THIS_FILE_LOC = Path.cwd()


def get_files_from_folder(folder: Path) -> list[Path]:
    files: list[Path] = []
    for file in folder.glob('**/*'):
        if file.is_file():
            files.append(file)

    return files


def get_untracked_files(folder: Path) -> list[Path]:
    repo = git.Repo(folder)
    untracked_files = [Path(file) for file in repo.untracked_files]
    return untracked_files


def get_uncommited_files(folder: Path) -> list[Path]:
    repo = git.Repo(folder)
    uncommited_files = [Path(file.a_path) for file in repo.index.diff(None)]
    return uncommited_files


def split_list_into_chunks(the_list: list, chunk_size: int = None) -> list[list]:
    if chunk_size is None:
        chunk_size = NUM_FILES

    return [the_list[i:i + chunk_size] for i in range(0, len(the_list), chunk_size)]


def chunk_files_by_size(file_paths: list[Path], max_chunk_size: int = CHUNK_SIZE, raise_on_big_file: bool = True) -> \
list[list[Path]]:
    """
    Groups file paths into chunks, with each group's total size not exceeding max_chunk_size.

    Parameters:
    - file_paths: List of pathlib.Path objects.
    - max_chunk_size: Maximum size of each chunk in bytes. Defaults to 100 MB.

    Returns:
    - A list of lists, where each inner list is a group of files not exceeding the specified total size.
    """
    chunks = []
    current_chunk = []
    current_chunk_size = 0

    for file_path in file_paths:
        if isinstance(file_path, str):
            file_path = Path(file_path)
        # git also seems to have a problem with big chunks, so we'll split the chunks into smaller chunks
        if len(current_chunk) >= NUM_FILES:
            chunks.append(current_chunk)
            current_chunk = []
            current_chunk_size = 0

        # if not file_path.is_relative_to(PROJECT_GIT_ROOT):
        #     file_path = PROJECT_GIT_ROOT / file_path

        # if not file_path.exists():
        #     continue
        try:
            disk_path = file_path
            if not disk_path.is_relative_to(PROJECT_GIT_ROOT):
                disk_path = PROJECT_GIT_ROOT / file_path

            if not disk_path.exists():
                current_chunk.append(file_path)
                logger.debug(f'file does not exist, or maybe a delete: {file_path.as_posix()}')
                continue

            file_size = disk_path.stat().st_size
            if file_size > max_chunk_size:
                if raise_on_big_file:
                    raise RuntimeError(f'file size too big: {file_path.as_posix()}')

                logger.warning(f'file size too big: {file_path.as_posix()}')
                continue

            if file_size + current_chunk_size <= max_chunk_size:
                current_chunk.append(file_path)
                current_chunk_size += file_size
                continue

            if current_chunk:  # if the current_chunk is not empty, add it to chunks
                chunks.append(current_chunk)

            current_chunk = [file_path]
            current_chunk_size = file_size

        except Exception as error:
            logger.error(f'error getting file size: {file_path.as_posix()}')
            logger.exception(error)

    # Don't forget to add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def git_commit_and_force_push_files_to_remote_branch(files: list[Path], branch_name: str, commit_message: str) -> None:
    repo = git.Repo(PROJECT_GIT_ROOT)
    for file_path in files:
        if isinstance(file_path, str):
            file_path = Path(file_path)
        try:
            repo.git.add(file_path.as_posix())
        except Exception as error:
            logger.error(f'error adding file: {file_path.as_posix()}')
            logger.exception(error)

    repo.index.commit(commit_message)
    repo.git.push('origin', branch_name, force=True)


if __name__ == '__main__':
    root_folders = [
        PROJECT_GIT_ROOT
    ]
    the_branch_name = 'master'
    untracked_files = get_untracked_files(PROJECT_GIT_ROOT)
    the_uncommited_files = get_uncommited_files(PROJECT_GIT_ROOT)
    all_the_files = untracked_files + the_uncommited_files
    all_the_files.sort(key=lambda x: x.as_posix())
    untracked_chunks = chunk_files_by_size(all_the_files)
    # pprint.pprint(untracked_chunks, indent=4)
    logger.info(f'num untracked files: {len(untracked_files)}')
    logger.info(f'num uncommited files: {len(the_uncommited_files)}')
    logger.info(f'num chunks: {len(untracked_chunks)}')
    iter = 0
    commit_message = f'I Am a cool commit message'
    for chunk in untracked_chunks:
        iter += 1
        pprint.pprint(chunk, indent=4)
        git_commit_and_force_push_files_to_remote_branch(chunk, the_branch_name, f'{commit_message} : {iter}')

    logger.info('Finished!')
