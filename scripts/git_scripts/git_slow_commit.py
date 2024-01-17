"""
This script is used to commit and force push files to a remote Git branch in chunks.
This helps with githubs tendency to choke on large commits.
In the future I want to do size buckets instead of file number buckets but this worked so i stopped haha.
"""

from pathlib import Path

import git

from lazy_log import logger

NUM_FILES = 50  # files per commit
PROJECT_GIT_ROOT = Path('C:\\GitHub\\')


def get_files_from_folder(folder: Path) -> list[Path]:
    """Get all files in a folder and return them as a list of Path objects.
    """
    files: list[Path] = []
    for file in folder.glob('**/*'):
        if file.is_file():
            files.append(file)

    return files


def get_untracked_files(folder: Path) -> list[Path]:
    """Get all untracked files in a folder and return them as a list of Path objects.
    """
    repo = git.Repo(folder)
    untracked_files = [Path(file) for file in repo.untracked_files]
    return untracked_files


def get_uncommited_files(folder: Path) -> list[Path]:
    """Get all uncommitted files in a folder and return them as a list of Path objects.
    """
    repo = git.Repo(folder)
    uncommited_files = [Path(file.a_path) for file in repo.index.diff(None)]
    return uncommited_files


def split_list_into_chunks(the_list: list, chunk_size: int = None) -> list[list]:
    """Split a list into chunks and return the chunks as a list of lists.
    """
    if chunk_size is None:
        chunk_size = NUM_FILES

    return [the_list[i:i + chunk_size] for i in range(0, len(the_list), chunk_size)]


def git_commit_and_force_push_files_to_remote_branch(files: list[Path], branch_name: str, commit_message: str) -> None:
    """Commit and force push a list of files to a remote branch.
    """
    repo = git.Repo(PROJECT_GIT_ROOT)
    for file_path in files:
        try:
            repo.git.add(file_path.as_posix())
        except Exception as error:
            logger.error(f'error adding file: {file_path.as_posix()}')
            logger.exception(error)

    repo.index.commit(commit_message)
    repo.git.push('origin', branch_name, force=True)


if __name__ == '__main__':
    import pprint

    root_folders = [
        PROJECT_GIT_ROOT
    ]
    the_branch_name = 'add_engine'
    the_untracked_files = get_untracked_files(PROJECT_GIT_ROOT)
    the_uncommitted_files = get_uncommited_files(PROJECT_GIT_ROOT)
    all_the_files = the_untracked_files + the_uncommitted_files
    all_the_files.sort(key=lambda x: x.as_posix())
    untracked_chunks = split_list_into_chunks(all_the_files)
    # pprint.pprint(untracked_chunks, indent=4)
    iter = 0
    for chunk in untracked_chunks:
        iter += 1
        logger.info(f'\n\nchunk size: {len(chunk)}')
        pprint.pprint(chunk, indent=4)
        git_commit_and_force_push_files_to_remote_branch(chunk, the_branch_name, f'uncommited files: {iter}')

    logger.info('Finished!')
