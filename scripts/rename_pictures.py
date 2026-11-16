"""Renames the picture files in the form_assets repo so every name is lowercase.

It sits in form_assets/scripts and works on the events, experts, heroes and items folders next to it (files directly
in form_assets are left alone). Run it from anywhere:
    python scripts/rename_pictures.py

Then commit and push. It uses "git mv" so git records the renames, and it moves each file through a
temporary name first, because Windows and macOS treat "Lloyd.png" and "lloyd.png" as the same file.
Running it again changes nothing.
"""
import os
import subprocess
import sys

# The repo folder: the one above the scripts folder this file is in.
REPO_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PICTURE_FOLDERS = ['events', 'experts', 'heroes', 'items']

# Names that change more than their case: the old name, then the new one (in its folder).
SPECIAL_NAMES = {
    'heroes/ahmos-shard.png': 'heroes/ahmose-shard.png',
    'events/crazyJoe.png': 'events/crazy-joe.png',
    'events/fortressBattle.png': 'events/fortress-battle.png',
    'events/visionOfDawn.png': 'events/vision-of-dawn.png',
}


def is_git_repo():
    try:
        result = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], capture_output=True, text=True)
    except FileNotFoundError:  # git is not installed
        return False
    return result.returncode == 0 and result.stdout.strip() == 'true'


def move_file(old_path, new_path, use_git):
    # Two steps (old -> temporary -> new), so a case-only change also works on Windows and macOS.
    temporary_path = new_path + '.renaming'
    for source, target in [(old_path, temporary_path), (temporary_path, new_path)]:
        if use_git:
            subprocess.run(['git', 'mv', source, target], check=True)
        else:
            os.rename(source, target)


def main():
    # Paths below are relative to the repo folder, wherever the script is run from.
    os.chdir(REPO_FOLDER)
    missing_folders = [folder for folder in PICTURE_FOLDERS if not os.path.isdir(folder)]
    if len(missing_folders) == len(PICTURE_FOLDERS):
        sys.exit('No events, experts, heroes or items folder in ' + REPO_FOLDER + '. Keep this script in form_assets/scripts.')
    use_git = is_git_repo()
    renamed_count = 0
    for folder in PICTURE_FOLDERS:
        if not os.path.isdir(folder):
            continue
        for file_name in sorted(os.listdir(folder)):
            old_path = folder + '/' + file_name
            new_path = SPECIAL_NAMES.get(old_path, folder + '/' + file_name.lower())
            if new_path == old_path:
                continue
            # Another file already has exactly the new name: leave both for a person to check.
            # (The folder listing gives the real names, so "Lloyd.png" alone does not count as "lloyd.png".)
            if os.path.basename(new_path) in os.listdir(folder):
                print('Skipped ' + old_path + ': ' + new_path + ' already exists.')
                continue
            move_file(old_path, new_path, use_git)
            print(old_path + ' -> ' + new_path)
            renamed_count += 1
    print(str(renamed_count) + ' files renamed.' + (' Commit and push to finish.' if use_git and renamed_count else ''))


if __name__ == '__main__':
    main()