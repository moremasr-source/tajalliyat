import json,sys,re
Q=json.load(open('vendor/node_modules/quran-json/dist/quran.json'))
H=re.compile('[ً-ٰٟۖ-ۭـ]')
def norm(s): s=H.sub('',s); s=re.sub('[ٱأإآ]','ا',s); return re.sub('ى','ي',s)
cmd=sys.argv[1]
if cmd=='get':
  for ref in sys.argv[2:]:
    s,a=map(int,ref.split(':')); print(ref, Q[s-1]['name'], '|', Q[s-1]['verses'][a-1]['text'])
else:
  pat=norm(' '.join(sys.argv[2:]))
  for ch in Q:
    for v in ch['verses']:
      if pat in norm(v['text']): print(f"{ch['id']}:{v['id']}", ch['name'], '|', v['text'][:160])
