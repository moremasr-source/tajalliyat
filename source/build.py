"""Validate the name cards and resolve every ayah excerpt to the exact Mushaf text."""
import json, re, pathlib, sys

ROOT = pathlib.Path(__file__).parent
Q = json.load(open(ROOT / 'vendor/node_modules/quran-json/dist/quran.json', encoding='utf-8'))
MARKS = re.compile('[ً-ٰٟۖ-ۭـ]')
ORDER = ['rahman', 'latif', 'wadud', 'shakur', 'tawwab', 'halim', 'wali', 'wakil', 'hakim', 'wahid', 'azizrahim', 'samibasir', 'azizhakim', 'hayyqayyum', 'ghanihamid', 'ghafurrahim']
GROUPS = ['boy', 'girl', 'youngman', 'youngwoman', 'father', 'mother']
KOLB = ['tajriba', 'taammul', 'fahm', 'tatbiq']

def fold(ch):
    if MARKS.match(ch): return ''
    return {'ٱ': '', 'أ': '', 'إ': '', 'آ': '', 'ا': '', 'ى': 'ي', 'ئ': 'ي', 'ؤ': 'و', 'ة': 'ه', 'ء': ''}.get(ch, ch)

def normalize_with_map(s):
    out, idx = [], []
    for i, ch in enumerate(s):
        f = fold(ch)
        for c in f:
            out.append(c); idx.append(i)
    return ''.join(out), idx

def norm(s): return normalize_with_map(s)[0]

def resolve(ref, excerpt=None):
    s, a = map(int, ref.split(':'))
    ch = Q[s - 1]; text = ch['verses'][a - 1]['text']
    if excerpt:
        n, idx = normalize_with_map(text)
        target = norm(excerpt).replace(' ', '')
        nz = n.replace(' ', ''); # match ignoring spaces, map back through indices
        nz_idx = [idx[i] for i, c in enumerate(n) if c != ' ']
        pos = nz.find(target)
        if pos < 0:
            raise SystemExit(f'excerpt not found in {ref}: {excerpt}')
        start, end = nz_idx[pos], nz_idx[pos + len(target) - 1] + 1
        # grow to whole-word edges (alef/hamza/marks fold to nothing and get dropped otherwise)
        while start > 0 and text[start - 1] != ' ': start -= 1
        while end < len(text) and text[end] != ' ': end += 1
        text = text[start:end].strip().lstrip('۞')
    surah = {'ابراهيم': 'إبراهيم'}.get(ch['name'], ch['name'])
    # this dataset encodes the open (muttasil) tanween with look-alike marks; use the Unicode ones fonts support
    text = text.translate({0x065E: 0x08F1, 0x0656: 0x08F2, 0x0657: 0x08F0})
    return {'ref': ref, 'surah': surah, 'num': f'{a}', 'text': text.lstrip('۞'), 'partial': bool(excerpt)}

problems, names, pending = [], [], []
ALL = ORDER + sorted(p.stem for p in (ROOT/'data').glob('*.json') if p.stem not in ORDER + ['feelings'])
for nid in ALL:
    d = json.load(open(ROOT / f'data/{nid}.json', encoding='utf-8'))
    d['ayah'] = resolve(d['ayah']['ref'], d['ayah'].get('excerpt'))
    d['ayat'] = [resolve(x['ref'], x.get('excerpt')) for x in d['ayat']]
    for g in GROUPS:
        grp = d['groups'][g]
        nq, nt = len(grp['questions']), len(grp['tajalliyat'])
        nk = sum(len(grp['tasks'][k]) for k in KOLB)
        if (nq, nt, nk) != (10, 20, 20):
            problems.append(f'{nid}/{g}: questions={nq} tajalliyat={nt} tasks={nk}')
        for k in ['simple', 'deep', 'lesson']:
            if not grp.get(k): problems.append(f'{nid}/{g}: missing {k}')
    (pending if d.get('status') in ('draft', 'in_review') else names).append(d)

if problems:
    print('\n'.join(problems)); sys.exit(1)
feel = json.load(open(ROOT / 'data/feelings.json', encoding='utf-8'))
ids = {d['id'] for d in names}
for f in feel:
    f['ayah'] = resolve(f['ayah']['ref'], f['ayah'].get('excerpt'))
    if not set(f['names']) <= ids: problems.append(f'feeling {f["id"]}: unknown name')
if problems:
    print('\n'.join(problems)); sys.exit(1)
out = ROOT / 'dist'; out.mkdir(exist_ok=True)
(out / 'data.js').write_text('window.ASMA=' + json.dumps(names, ensure_ascii=False) + ';\nwindow.FEEL=' + json.dumps(feel, ensure_ascii=False) + ';', encoding='utf-8')
for f in feel: print('feel', f['label'], '|', f['ayah']['surah'], f['ayah']['num'], '|', f['ayah']['text'])
total = sum(len(g['questions']) + len(g['tajalliyat']) + sum(len(g['tasks'][k]) for k in KOLB) for d in names for g in d['groups'].values())
print(f'in review (validated, not published): {[d["plain"] for d in pending]}')
print(f'ok: {len(names)} names, {total} items, data.js {(out / "data.js").stat().st_size // 1024} KB')
for d in names:
    print(d['plain'], '|', d['ayah']['surah'], d['ayah']['num'], '|', d['ayah']['text'])
