moodle19-forum-extractor
========================

## Description
Extract forum content from a moodle 1.9.x backup file and present it in HTML format

## Usage

From a command line, pass a moodle 1.9 backup file with user data as a parameter. For example:

    $ python3 extract.py moodle-backup.zip

The output will print to the console. If you want to output to a file, pipe the output to an output file. For example:

    $ python3 extract.py moodle-backup.zip > out.html