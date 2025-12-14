# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from __future__ import print_function
import argparse
import json
import os
import os.path

from cowlist import COWList
from ctypes_unicode_proclaunch import launch, wait
from directory_file_mapping import DirectoryFileMapping
from get_unicode_multiline_input_with_editor import get_unicode_multiline_input_with_editor
from get_unicode_shell import get_unicode_shell
from sorted_fractionally_indexed_cowlist_set import SortedFractionallyIndexedCOWListSet
from textcompat import filesystem_str_to_text

# Alphabet for base58 fractional indexing (short filenames, can insert in middle)
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def main():
    # -- CLI set-up --
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subcommand', help='Subcommand help')

    # sdial dial <number> [args...]
    parser_dial = subparsers.add_parser('dial', help='Dial a command')
    parser_dial.add_argument('number', type=int, help='Command number to dial')
    parser_dial.add_argument('args', nargs=argparse.REMAINDER, help='Arguments to pass to the command')

    # sdial add [command]
    parser_add = subparsers.add_parser('add', help='Add a command')
    parser_add.add_argument('command', nargs='?', default=None, help='Command to add')

    # sdial edit <number>
    parser_edit = subparsers.add_parser('edit', help='Edit a command')
    parser_edit.add_argument('number', type=int, help='Command number to edit')

    # sdial remove <number>
    parser_remove = subparsers.add_parser('remove', help='Remove a command')
    parser_remove.add_argument('number', type=int, help='Command number to remove')

    # sdial list
    parser_list = subparsers.add_parser('list', help='List all commands')

    # Parse arguments from the command-line
    args = parser.parse_args()

    # Detect the user's shell for script execution (e.g., /bin/bash, cmd.exe, etc.)
    unicode_shell = get_unicode_shell()

    # Ensure the ~/.sdial directory exists to store scripts
    sdial_directory_path = os.path.expanduser('~/.sdial')
    if not os.path.isdir(sdial_directory_path):
        os.mkdir(sdial_directory_path)

    # File mapping to the directory for storing commands as plain text files
    directory_file_mapping = DirectoryFileMapping(sdial_directory_path)

    # Fractionally-indexed list to allow insert/remove with minimal rename-churn
    sorted_fractionally_indexed_cowlist_set = SortedFractionallyIndexedCOWListSet(BASE58_ALPHABET)
    for file_name in directory_file_mapping:
        sorted_fractionally_indexed_cowlist_set.add(COWList(file_name))

    # -- Subcommand handlers --
    if args.subcommand == 'dial':
        number = args.number
        file_name = ''.join(sorted_fractionally_indexed_cowlist_set[number])
        file_path = os.path.join(sdial_directory_path, file_name)
        unicode_file_path = filesystem_str_to_text(file_path)
        unicode_args = list(map(filesystem_str_to_text, args.args))
        # Command: [shell, <snippet file>, arg1, arg2 ...]
        command_args = [unicode_shell, unicode_file_path]
        command_args.extend(unicode_args)
        # Fork and wait for completion
        wait(launch(command_args))
    elif args.subcommand == 'add':
        if not args.command:
            # Input interactively using preferred editor
            command = u''.join(
                get_unicode_multiline_input_with_editor(
                    unicode_initial_input_lines=[],
                    unicode_line_comments_start_with=None,  # specify `None` to not skip over any line
                    editor=None  # or specify e.g. 'vim'
                )
            ).strip()
        else:
            command = filesystem_str_to_text(args.command).strip()

        # Compute filename for the next inserted command (after last)
        number = len(sorted_fractionally_indexed_cowlist_set)
        file_name = ''.join(
            sorted_fractionally_indexed_cowlist_set.synthesize(index=number)
        )

        # Write the command (as UTF-8 bytes) to a new file in the dials directory
        directory_file_mapping[file_name] = command.encode('utf-8')

        print(number)
    elif args.subcommand == 'edit':
        number = args.number
        file_name = ''.join(sorted_fractionally_indexed_cowlist_set[number])
        command = directory_file_mapping[file_name].decode('utf-8')
        new_command = u''.join(
            get_unicode_multiline_input_with_editor(
                unicode_initial_input_lines=[command],
                unicode_line_comments_start_with=None,  # specify `None` to not skip over any line
                editor=None  # or specify e.g. 'vim'
            )
        ).strip()
        # Overwrite the file with updated content
        directory_file_mapping[file_name] = new_command.encode('utf-8')
    elif args.subcommand == 'remove':
        number = args.number
        file_name = ''.join(sorted_fractionally_indexed_cowlist_set[number])

        del directory_file_mapping[file_name]
    elif args.subcommand == 'list':
        print('number,command')
        for i, cowlist in enumerate(sorted_fractionally_indexed_cowlist_set):
            file_name = ''.join(cowlist)
            command = directory_file_mapping[file_name].decode('utf-8')
            # Print quoted command text for clarity/robustness in CSV
            print('%d,%s' % (i, json.dumps(command)))
    # No subcommand? Print parser error/help.
    else:
        parser.error('argument subcommand: not provided (choose from %s)' % (', '.join(subparsers.choices.keys()),))


if __name__ == '__main__':
    main()
