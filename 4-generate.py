#!/usr/bin/env python3
"""
Name        4-generate.py
Description Generate Python module which translates unicode data
Author      Pander <pander@users.sourceforge.net>
License     TODO
URL         https://github.com/OpenTaal/python-unicodedata_l10n

0.1 2019-02-19 Pander <pander@users.sourceforge.net>
Initial release
"""

from datetime import datetime, timezone
from logging import getLogger, INFO, info, warning, error
from os.path import isdir, join
from os import makedirs
from glob import glob

def read_texts(path, dest):
    for file_path in glob(path):
        if isdir(file_path):
            continue
        for line in open(file_path):
            line = line.strip()
            if ': ' not in line:
                continue
            unicode = line.split(': ')[0]
            text = line[len(unicode) + 2:]
            unicode = unicode.strip()
            if text == '':
                continue
            if unicode in dest:
                error('Duplicate Unicode codepoint {} for file {}.'.format(unicode, path))
            else:
                dest[unicode] = text

getLogger().setLevel(INFO)
now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M%z')
top = join('unicode-table-data-master', 'loc')

# source texts
sources = {}
# read symbols
read_texts(join(top, 'en', 'symbols', '*'), sources)
read_texts(join(top, 'en', 'symbols', 'plane1', '*'), sources)
read_texts(join(top, 'en', 'symbols', 'plane2', '*'), sources)
read_texts(join(top, 'en', 'symbols', 'planeE', '*'), sources)
info('Read for language "en" {} source texts'.format(len(sources)))

base_path = 'locale'
for lang_path in sorted(glob(join('unicode-table-data-master', 'loc', '*'))):
    lang = lang_path.split('/')[-1]
    if lang == 'en' or not isdir(lang_path):
        continue
    leaf_path = join(base_path, lang, 'LC_MESSAGES')
    # destination texts
    dests = {}
    # read symbols
    read_texts(join(top, lang, 'symbols', '*'), dests)
    read_texts(join(top, lang, 'symbols', 'plane1', '*'), dests)
    read_texts(join(top, lang, 'symbols', 'plane2', '*'), dests)
    read_texts(join(top, lang, 'symbols', 'planeE', '*'), dests)
    warning('Read {} destination texts for langauge "{}"'.format(len(dests), lang))
    
    translations = {}
    deletes = set()
    identical = 0
    missing = 0
    for unicode, dest in dests.items():
        try:
            source = sources[unicode]
        except KeyError:
            missing += 1
            continue
        if source in translations:
            if translations[source] != dest:
                warning('Removing multiple different destination texts for at least Unicode {} for source "{}", see destinations "{}" and "{}"'.format(unicode, source, translations[source], dest))
                deletes.add(source)
                continue
        else:
            translations[source] = dest
        if source == dest:
            identical += 1
    if missing > 0:
        warning('Missing {} source texts for which translation in langauge "{}" is available'.format(missing, lang))
    # delete translations with multiple destinations
    for source in deletes:
        del translations[source]

    if len(sources) == 0 or len(translations) == 0 or len(sources) > 100 * len(translations) or len(translations) < 10 * identical:
        warning('Skipping PO file generation for language "{}" with {} identical texts and only {} translations'.format(lang, identical, len(translations)))
        continue
    info('Generating PO file for language "{}" with {} identical texts and {} translations'.format(lang, identical, len(translations)))
    makedirs(leaf_path, exist_ok=True)
    out = open(join(leaf_path, 'symbols.po'), 'w')
    out.write('''# Copyright (C) https://github.com/unicode-table/unicode-table-data/blob/master/LICENSE.md
msgid ""
msgstr ""
"Project-Id-Version: unicode_l10n 1.0\\n"
"Report-Msgid-Bugs-To: https://github.com/unicode-table/unicode-table-data/issues\\n"
"POT-Creation-Date: {}\\n"
"PO-Revision-Date: {}\\n"
"Language-Team: https://github.com/unicode-table/unicode-table-data\\n"
"Language: {}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
'''.format(now, now, lang))
    for source, dest in sorted(translations.items()):
        out.write('msgid "{}"\n'.format(source.replace('\\', '\\\\').replace('"', '\\"')))
        out.write('msgstr "{}"\n'.format(dest.replace('\\', '\\\\').replace('"', '\\"')))
    out.close()
