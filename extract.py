#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import zipfile
import HTMLParser
import sys
import xml.etree.ElementTree as et

class MoodleBackup:
    backup = ''
    moodle_backup = ''
    forums = []
    forum_discussions = []
    forum_posts = []
    course_name = ''

    def __init__(self,backup_file):
        #try opening backup zip file
        try:
            self.backup = zipfile.ZipFile(backup_file)
        except (zipfile.BadZipfile, IOError):
            sys.exit("Please provide a proper zip file.")
        
        #parse the moodle.xml file
        self.moodle_backup = et.parse(self.backup.open('moodle.xml')).getroot()
        self.course_name = self.moodle_backup.find('./COURSE/HEADER/FULLNAME').text

        #find all the forums
        html = HTMLParser.HTMLParser()
        for forum in self.moodle_backup.findall('./COURSE/MODULES/MOD'):
            if forum.find('./MODTYPE').text == 'forum':
                self.forums.append({'name':forum.find('./NAME').text,
                    'description':html.unescape(forum.find('./INTRO').text)})
                #the logic in this section needs to be figured out a bit better
                for discussion in forum.findall('./DISCUSSIONS/DISCUSSION'):
                    self.forum_discussions.append({'discussion_id':discussion.find('./ID').text,
                        'name':discussion.find('./NAME')})
    def extract(self):
        pass
    def list(self):
        pass

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("backup_file",help="A backup zip file from moodle 1.9")
    args = parser.parse_args()

    mb = MoodleBackup(args.backup_file)
    mb.list()
    print(mb.course_name)
    print(mb.forums)