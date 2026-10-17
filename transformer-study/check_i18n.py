"""Key-parity check for i18n/*.json (run by render.sh).
Fails on: a key that is not in en.json, a key used in the .puml but missing from en.json,
a key in en.json that no .puml uses, or a bare one-line JSON array value.
Reports (does not fail on) keys that are not translated yet (they fall back to English) and
translated notes whose line count differs from English (translations re-wrap lines on purpose).
"""
import json, re, sys, glob, os
here = os.path.dirname(os.path.abspath(__file__))
os.chdir(here)
en = json.load(open('i18n/en.json', encoding='utf-8'))
errors = []
warnings = []
used = set()
for f in glob.glob('plantuml_*.puml'):
    used |= set(re.findall(r'\$t\("([a-z_]+_\d+)"\)', open(f, encoding='utf-8').read()))
for k in sorted(used - set(en)): errors.append(f'key used in a .puml but missing from en.json: {k}')
for k in sorted(set(en) - used): errors.append(f'key in en.json but not used in any .puml: {k}')
for lang in ('zh-tw', 'ja', 'ko'):
    d = json.load(open(f'i18n/{lang}.json', encoding='utf-8'))
    for k in sorted(set(d) - set(en)): errors.append(f'{lang}: extra key not in en.json: {k}')
    for k, v in d.items():
        if k in en and v.count('\n') != en[k].count('\n'):
            warnings.append(f'{lang}: {k} has {v.count(chr(10))+1} lines, en has {en[k].count(chr(10))+1} (re-wrapped?)')
        if k in en and v.strip().startswith('[') and v.strip().endswith(']') and '\n' not in v:
            errors.append(f'{lang}: {k} looks like a bare JSON array; PlantUML would re-serialize it')
    missing = sorted(set(en) - set(d))
    print(f'{lang}: {len(d)}/{len(en)} keys translated, {len(missing)} fall back to English')
if warnings:
    print('warnings:\n  ' + '\n  '.join(warnings))
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('i18n parity OK')
