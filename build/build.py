import json
B='build'; D='dl'
t=open(f'{B}/template.html',encoding='utf-8').read()
data=open(f'{B}/modules.json',encoding='utf-8').read()
presets={
 'Starship default': '',
 'Pastel Powerline': open(f'{D}/pastel.toml',encoding='utf-8').read(),
 'Tokyo Night': open(f'{D}/tokyo.toml',encoding='utf-8').read(),
 'Gruvbox Rainbow': open(f'{D}/gruvbox.toml',encoding='utf-8').read(),
 'Nerd Font Symbols': open(f'{D}/nf.toml',encoding='utf-8').read(),
 'Minimal': open(f'{B}/minimal.toml',encoding='utf-8').read(),
}
def js(o): return json.dumps(o,ensure_ascii=False).replace('</','<\\/')
import collections
gn=json.load(open(f'{D}/glyphnames.json',encoding='utf-8')); gn.pop('METADATA',None)
groups=collections.OrderedDict()
for k,v in gn.items():
    pre,_,nm=k.partition('-'); groups.setdefault(pre,[]).append(f"{nm}:{v['code']}")
nfdata={k:','.join(v) for k,v in groups.items()}
t=t.replace('/*@NFDATA@*/null',js(nfdata))
import unicodedata
BLOCKS=[('Arrows',0x2190,0x21FF),('Supplemental arrows',0x27F0,0x27FF),('More arrows',0x2900,0x297F),('Misc arrows and shapes',0x2B00,0x2BFF),
 ('Box drawing',0x2500,0x257F),('Block elements',0x2580,0x259F),('Geometric shapes',0x25A0,0x25FF),('Misc technical',0x2300,0x23FF),
 ('Misc symbols',0x2600,0x26FF),('Dingbats',0x2700,0x27BF),('Math operators',0x2200,0x22FF),('Punctuation',0x2010,0x205E),
 ('Letterlike',0x2100,0x214F),('Greek',0x0391,0x03C9),('Latin-1 symbols',0x00A1,0x00BF),('Braille',0x2800,0x28FF)]
uni={}
for name,a,z in BLOCKS:
    ents=[]
    for cp in range(a,z+1):
        ch=chr(cp); nm=unicodedata.name(ch,'')
        if not nm or unicodedata.category(ch) in ('Zs','Cc','Cf','Mn'): continue
        if 0x23FB<=cp<=0x23FE or cp==0x2B58: continue  # these come from the Nerd Font
        ents.append('%04x:%s'%(cp,nm.lower()))
    uni[name]=','.join(ents)
t=t.replace('/*@UNIDATA@*/null',js(uni))
import glob,re as _re
def load_base(sysname, n):
    out=[]
    for f in sorted(glob.glob(f'{D}/schemes/{sysname}/*.yaml')):
        y=open(f,encoding='utf-8').read()
        name=_re.search(r'^name:\s*"?(.*?)"?\s*$',y,_re.M).group(1)
        var=(_re.search(r'^variant:\s*"?(\w+)"?',y,_re.M) or [None,''])[1]
        cols=[]
        for i in range(n):
            k='base%02X'%i
            m=_re.search(r'^\s*'+k+r':\s*"?#?([0-9a-fA-F]{6})"?',y,_re.M)
            if not m: break
            cols.append(m.group(1).lower())
        if len(cols)==n: out.append(f"{name}|{var}|{''.join(cols)}")
    return out
t=t.replace('/*@BASE@*/null',js({'base16':load_base('base16',16),'base24':load_base('base24',24)}))
t=t.replace('/*@DATA@*/null',data.replace('</','<\\/')).replace('/*@PRESETS@*/null',js(presets)).replace('/*@GLYPHS@*/null',open(f'{B}/curated.json',encoding='utf-8').read()).replace('@FONT@',open(f'{B}/nffull.b64').read())
open('starship-prompt-builder.html','w',encoding='utf-8').write(t)
print(len(t))

# Standalone copy that opens directly from disk (the artifact host adds this skeleton itself)
open('starship-prompt-builder-standalone.html','w',encoding='utf-8').write(
  '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
  '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  '<style>[hidden]{display:none!important}body{margin:0}</style>\n</head>\n<body>\n' + t + '\n</body>\n</html>\n')
