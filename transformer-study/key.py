"""Token-cheap access to the i18n keys, so nobody has to read a whole .puml or *.json.

  python3 key.py show note_012            value in all 4 languages + where the .puml uses it
  python3 key.py find "softmax"           keys whose English value contains the text (case-insensitive)
  python3 key.py find -a "old number"     same, but search all 4 languages
  python3 key.py set ja note_012 < new.txt   replace one value (stdin, real newlines); writes i18n/ja.json
  python3 key.py ctx note_012 [N]         the .puml lines around the key's use (default N=3)
  python3 key.py list [prefix]            key names (and the English first line) with an optional prefix

Writes keep the exact file format (indent 2, no ASCII escaping). Run ./site/sync.sh afterwards.
"""
import json, re, sys, glob, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
LANGS = ('en', 'zh-tw', 'ja', 'ko')


def load(l):
    return json.load(open(f'i18n/{l}.json', encoding='utf-8'))


def uses(key):
    out = []
    for f in sorted(glob.glob('plantuml_*.puml')):
        for n, line in enumerate(open(f, encoding='utf-8').read().split('\n'), 1):
            if f'$t("{key}")' in line:
                out.append((f, n))
    return out


def show(key):
    for l in LANGS:
        v = load(l).get(key)
        print(f'--- {l}' + ('' if v is not None else ' (missing, falls back to en)'))
        if v is not None:
            print(v)
    print('--- used at:', ', '.join(f'{f}:{n}' for f, n in uses(key)) or 'nowhere')


def ctx(key, n=3):
    for f, ln in uses(key):
        lines = open(f, encoding='utf-8').read().split('\n')
        print(f'=== {f}:{ln}')
        for i in range(max(0, ln - 1 - n), min(len(lines), ln + n)):
            print(f'{i + 1:4}{">" if i + 1 == ln else " "} {lines[i]}')


def find(text, all_langs):
    t = text.lower()
    for l in (LANGS if all_langs else ('en',)):
        for k, v in load(l).items():
            if t in v.lower():
                print(f'{l}\t{k}\t{v.splitlines()[0][:100] if v else ""}')


def set_(lang, key, value):
    d = load(lang)
    if lang != 'en' and key not in load('en'):
        sys.exit(f'{key} is not in en.json; add it there first')
    d[key] = value.rstrip('\n')
    open(f'i18n/{lang}.json', 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2))
    print(f'{lang}.json: {key} updated')


a = sys.argv[1:]
if len(a) >= 2 and a[0] == 'show': show(a[1])
elif len(a) >= 2 and a[0] == 'ctx': ctx(a[1], int(a[2]) if len(a) > 2 else 3)
elif len(a) >= 2 and a[0] == 'find': find(a[-1], a[1] == '-a')
elif len(a) == 3 and a[0] == 'set': set_(a[1], a[2], sys.stdin.read())
elif a and a[0] == 'list':
    for k, v in load('en').items():
        if k.startswith(a[1] if len(a) > 1 else ''):
            print(f'{k}\t{v.splitlines()[0][:80] if v else ""}')
else:
    print(__doc__)
