import json, re, sys, tomllib
D = sys.argv[1]
schema = json.load(open(f'{D}/schema.json'))
P = schema['properties']
readme = open(f'{D}/README.md').read()
nf = tomllib.load(open(f'{D}/nf.toml', 'rb'))

# Section parsing
sections = re.split(r'\n## ', readme)
docs = {}
for s in sections:
    m = re.search(r'(?:By default the|The) `([a-z_]+)` module (.+?)(?:\n\n|$)', s, re.S)
    if not m: continue
    name = m.group(1)
    if name in docs: continue
    desc = (m.group(2)).replace('\n', ' ')
    desc = re.sub(r'\s+', ' ', desc)
    # first sentence
    first = re.split(r'(?<=[.!])\s', desc)[0]
    first = re.sub(r'^The `[a-z_]+` module ', '', first)
    first = first[0].upper() + first[1:]
    first = first.replace('**','')
    first = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', first)
    opts = {}
    om = re.search(r'### Options\s*\n(.*?)(?:\n\n|\Z)', s, re.S)
    if om:
        for row in om.group(1).split('\n'):
            cells = [c.strip() for c in row.strip().strip('|').split('|')]
            if len(cells) >= 3 and cells[0].startswith('`'):
                k = cells[0].strip('`')
                d = cells[-1]
                d = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', d)
                opts[k] = d
    head = s.split('\n',1)[0].strip()
    hm = re.search(r'\{#([^}]+)\}', head)
    anchor = hm.group(1) if hm else re.sub(r'[^a-z0-9]+','-',head.lower()).strip('-')
    docs[name] = {'desc': first, 'opts': opts, 'h': anchor}

skip = {'claude_context', 'claude_cost', 'claude_model', 'custom', 'vcs'}
mods = {}
for k, v in P.items():
    df = v.get('default')
    if not isinstance(df, dict) or k in skip or k == 'palettes' or k == 'profiles': continue
    if 'format' not in df and k not in ('fill', 'line_break', 'env_var'): continue
    d = {}
    for ok, ov in df.items():
        if isinstance(ov,int) and not isinstance(ov,bool) and abs(ov) > 2**53-1: ov = 2**53-1
        if isinstance(ov, (str, bool)) or (isinstance(ov, int) and not isinstance(ov,bool)) or isinstance(ov, float):
            d[ok] = ov
        elif k == 'os' and ok == 'symbols':
            d[ok] = ov
        elif ok in ('substitutions',):
            pass
    if k == 'env_var':
        d = {'format': 'with [$env_value]($style) ', 'style': 'black bold dimmed', 'symbol': '', 'disabled': False}
    doc = docs.get(k, {'desc': '', 'opts': {}})
    o = {'d': d, 'desc': doc['desc'], 'h': doc.get('h',''), 'opts': {kk: vv for kk, vv in doc['opts'].items() if kk in d}}
    nfo = {}
    if k in nf:
        for ok, ov in nf[k].items():
            if isinstance(ov, str): nfo[ok] = ov
            elif ok == 'symbols': nfo['symbols'] = ov
    if nfo: o['nf'] = nfo
    mods[k] = o

# default order from README "equivalent to" block
L = readme.index('# Which is equivalent to')
blk = readme[L:readme.index('"""', readme.index('"""', L) + 3)]
order = re.findall(r'\$([a-z_]+)', blk)
out = {'modules': mods, 'order': order,
       'top': {k: P[k].get('default') for k in ('add_newline', 'continuation_prompt', 'scan_timeout', 'command_timeout', 'follow_symlinks')}}
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(mods), 'modules', len(json.dumps(out, ensure_ascii=False)), 'bytes')
missing = [m for m in mods if not mods[m]['desc']]
print('no desc:', missing)
print('order missing in mods:', [o for o in order if o not in mods])
print('mods not in order:', [m for m in mods if m not in order])
