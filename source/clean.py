"""Clean Arabic text extracted from chat-exported PDFs."""
import re, sys, pathlib

BIDI = re.compile('[‪-‮‎‏⁦-⁩﻿]')
HARAKAT = 'ً-ْٰ'

def fix_line(s: str) -> str:
    s = BIDI.sub('', s).strip()
    s = s.replace('اهلل', 'الله').replace('هلل', 'لله')  # Allah ligature
    # lam-alef ligature extracted in reverse order (e.g. األولى -> الأولى, اآلن -> الآن)
    s = re.sub(r'([اأإآ])ل', lambda m: m.group(0), s)
    s = re.sub(r'ا([أإآ])ل', r'ال\1', s)          # article + hamza-alef: األ -> الأ
    s = re.sub(r'(?<=[ء-ي])([أإآ])ل(?=[ء-ي])', r'ل\1', s)  # mid-word: ِإل -> لإ
    s = re.sub(r'(?<![ء-ي])([وفبك]?)ل?([أإآ])ل(?=[ء-ي])', lambda m: m.group(0), s)
    # a space wrongly inserted after a haraka inside a word: "َق بول" -> "َقبول"
    s = re.sub(rf'(?<=[ء-ي][{HARAKAT}]) (?=[ء-ي])', '', s)
    s = re.sub(rf' (?=[{HARAKAT}])', '', s)
    s = re.sub(r'\s+', ' ', s)
    # visual-order artefacts: leading punctuation belongs at the end; trailing "N." belongs at the start
    m = re.match(r'^([:.!؟?،]+)\s*(.*)$', s)
    if m and m.group(2):
        s = m.group(2) + m.group(1)
    m = re.match(r'^(.*?)\s*(\d+)\.$', s)
    if m and m.group(1):
        s = f'{m.group(2)}. {m.group(1)}'
    return s

for f in sys.argv[1:]:
    p = pathlib.Path(f)
    out = [fix_line(l) for l in p.read_text(encoding='utf-8').splitlines()]
    out = [l for l in out if l]
    p.with_suffix('.clean.txt').write_text('\n'.join(out), encoding='utf-8')
