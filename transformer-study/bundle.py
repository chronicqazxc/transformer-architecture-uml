"""Build self-contained diagrams: bundle/<name>.puml
Each bundle has the translations (only the keys that diagram uses) inlined and the language
set by ONE editable line near the top, so it renders in ANY PlantUML editor, including ones
that cannot read i18n/*.json (a local editor started elsewhere, or online editors).
Run by render.sh. Never edit bundle/ by hand: change the source .puml / i18n/*.json instead.
"""
import glob, json, os, re, sys
here = os.path.dirname(os.path.abspath(__file__))
os.chdir(here)
LANGS = ('en', 'zh-tw', 'ja', 'ko')
data = {l: json.load(open(f'i18n/{l}.json', encoding='utf-8')) for l in LANGS}
os.makedirs('bundle', exist_ok=True)
for f in sorted(glob.glob('plantuml_*.puml')):
    s = open(f, encoding='utf-8').read()
    used = set(re.findall(r'\$t\("([a-z_]+_\d+)"\)', s))
    inline = {l: {k: v for k, v in data[l].items() if k in used} for l in LANGS}
    block = ("' --- bundled by bundle.py: DO NOT EDIT; edit " + f + " and i18n/*.json, then run ./render.sh ---\n"
             "' >>> CHANGE THE LANGUAGE HERE: en | zh-tw | ja | ko\n"
             '!$lang = "en"\n'
             "!$all = " + json.dumps(inline, ensure_ascii=False, separators=(',', ':')) + "\n"
             "!$en = $all.en\n"
             "!$loc = $all[$lang]\n")
    out, n = re.subn(r"' --- i18n:begin.*?' --- i18n:end ---\n", lambda m: block, s, flags=re.S)
    assert n == 1, f'{f}: i18n markers not found'
    path = os.path.join('bundle', f)
    open(path, 'w', encoding='utf-8').write(out)
    print(f'bundle/{f}: {len(out)//1024} KB, {len(used)} keys')
