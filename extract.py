#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import zipfile
import html.parser
import sys
import os
import xml.etree.ElementTree as et
from datetime import date
import sqlite3

class MoodleBackup:
    backup = ''
    moodle_backup = ''
    forums = []
    forum_discussions = []
    forum_posts = []
    users = []
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

        #find all the forums and add them to forum_discussions
        parsed = html.parser.HTMLParser()
        forum_discussions = []

        for forum in self.moodle_backup.findall('./COURSE/MODULES/MOD'):
            if forum.find('./MODTYPE').text == 'forum':
                self.forums.append({'name':forum.find('./NAME').text,
                    'description':parsed.unescape(forum.find('./INTRO').text)})

                for discussion in forum.findall('./DISCUSSIONS/DISCUSSION'):
                    for post in discussion.findall('./POSTS/POST'):
                        forum_discussions.append([
                            int(discussion.find('./ID').text),
                            post.find('./SUBJECT').text,
                            int(post.find('./PARENT').text),
                            int(post.find('./USERID').text),
                            post.find('./MODIFIED').text,
                            parsed.unescape(post.find('./MESSAGE').text)
                            ])

        self.forum_discussions = forum_discussions

        #find all the users and add them to users
        for user in self.moodle_backup.findall('./COURSE/USERS/USER'):
            self.users.append([int(user.find('./ID').text),user.find('./FIRSTNAME').text,user.find('./LASTNAME').text])

    def extract(self):
        c = sqlite3.connect(':memory:')
        c.execute('''CREATE TABLE if not exists users
            (id int, firstname text, lastname text)''')
        c.execute('''CREATE TABLE if not exists posts
            (id int, subject text, parent int, userid int, modified int, message text)''')
        c.executemany('INSERT INTO users VALUES(?,?,?)',self.users)
        c.executemany('INSERT INTO posts VALUES(?,?,?,?,?,?)', self.forum_discussions)
        c.commit()
        print("<!doctype html>\n<html>\n<head>\n<title>"+self.course_name+"</title>\n</head>\n<body>")
        print("<h1>Forum posts in: "+self.course_name+"</h1>")
        for row in c.execute('SELECT subject,modified,message,firstname,lastname FROM posts as P JOIN users as u on P.userid=U.id'):
            modified_date = date.fromtimestamp(row[1])
            print("<h2>"+row[0]+"</h2>")
            print("<h3>By: "+row[3]+" "+row[4]+"</h3>")
            print("<h4>Written on: "+modified_date.strftime("%B %d %Y")+"</h4>")
            print("<div>"+row[2]+"</div>")
            
        print("</body>\n</html>")

    def list(self):
        pass

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("backup_file",help="A backup zip file from moodle 1.9")
    args = parser.parse_args()

    mb = MoodleBackup(args.backup_file)
    mb.extract()