#!/usr/bin/python3
"""
    WARNING : This file is for developement only !
    Watch for pug, es2015 js files changes, transcode them on the fly
    Depends on pypugjs, babel with env plugin, sass
    On archlinux, it results on installing packages :
        * babel-cli
        * python-inotify-simple
        * python-jinja
        * python-pypugjs
        * yarn
    Then, on src folder, do a
        * yarn install
"""
import os
import sys
import subprocess
from time import sleep
from inotify_simple import INotify, flags

BASE_FOLDER = 'octoprint_z_probe_offset'
# WATCH_FOLDER = os.path.join(BASE_FOLDER, 'src')
WATCH_FOLDER = 'src'
PUG_FOLDER = os.path.join(BASE_FOLDER, 'templates')
ES_FOLDER = os.path.join(BASE_FOLDER, 'static')
PUG_FILES = []
ES_FILES = []

def get_output(file, folder, extension):
    output = f'{os.path.splitext(os.path.split(file)[1])[0]}.{extension}'
    return os.path.join(folder, output)

inotify = INotify()
for watch_file in os.listdir(WATCH_FOLDER):
    if os.path.splitext(watch_file)[1] == '.pug':
        PUG_FILES.append(os.path.join(WATCH_FOLDER, watch_file))
    if os.path.splitext(watch_file)[1] == '.js':
        ES_FILES.append(os.path.join(WATCH_FOLDER, watch_file))

def pug_watch(files):
    for pug_file in files:
        print(f'Watch {pug_file}: {get_output(pug_file, PUG_FOLDER, "jinja2")}')
        inotify.add_watch(os.path.join(pug_file), flags.MODIFY)

def es_watch(files):
    for es_file in files:
        print(f'Watch {es_file}: {get_output(es_file, ES_FOLDER, "js")}')
        inotify.add_watch(os.path.join(es_file), flags.MODIFY)

pug_watch(PUG_FILES)
es_watch(ES_FILES)

def pug_convert(file):
    pug_output = get_output(file, PUG_FOLDER, 'jinja2')
    print(f'Converting {file} to {pug_output}')
    subprocess.Popen(f'pypugjs -c jinja {file} {pug_output}', shell=True)

def es_convert(file):
    es_output = '../' + get_output(file, ES_FOLDER, 'js')
    print(f'Converting {file} to {es_output}')
    file = os.path.basename(file)
    subprocess.Popen(f'cd {WATCH_FOLDER}; babel {file} -o {es_output}',
                     shell=True)

try:
    if PUG_FILES or ES_FILES:
        while True:
            for event in inotify.read():
                print('File change detected')
                # pylint: disable=W0106
                [pug_convert(pug_file) for pug_file in PUG_FILES]
                [es_convert(es_file) for es_file in ES_FILES]
                sleep(5)
                pug_watch(PUG_FILES)
                es_watch(ES_FILES)

except KeyboardInterrupt:
    sys.exit(0)
