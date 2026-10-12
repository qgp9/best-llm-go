#!/usr/bin/env python3
"""
update_data.py
Synchronizes OpenCode Go data from:
1. Official Console Go Documentation: https://opencode.ai/v2/docs/console/go/
2. OpenCode Go Web limits: https://opencode.ai/go
3. Models Registry: https://models.dev/api.json
4. Benchmarks: Artificial Analysis snapshot (models.json)
"""

import urllib.request
import json
import re
import os
import ssl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_url(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
        return res.read().decode('utf-8')

# 1. Fetch official /v2/docs/console/go/
console_models = []
print("1. Fetching official pricing & limits from opencode.ai/v2/docs/console/go/...")
try:
    doc_html = fetch_url("https://opencode.ai/v2/docs/console/go/")
    panel_start = doc_html.find('id="go-pricing-panel-go"')
    panel_end = doc_html.find('id="go-pricing-panel-go-plus"')
    panel_html = doc_html[panel_start:panel_end] if panel_start != -1 else doc_html
    rows = re.findall(r'<tr>(.*?)</tr>', panel_html, re.DOTALL)
    for r in rows[1:]:
        cols = re.findall(r'<td[^>]*>(.*?)</td>', r, re.DOTALL)
        if len(cols) >= 5:
            mname = re.sub(r'<[^>]+>', '', cols[0]).strip()
            inp = cols[1].strip()
            out = cols[2].strip()
            cached_read = cols[3].strip()
            cached_write = cols[4].strip() if len(cols) > 5 else '-'
            limit_col = cols[-1]
            lim_match = re.search(r'\$(\d+)', limit_col)
            lim = int(lim_match.group(1)) if lim_match else 0
            inp_num = float(re.sub(r'[^0-9.]', '', inp)) if re.search(r'[0-9]', inp) else 0.0
            out_num = float(re.sub(r'[^0-9.]', '', out)) if re.search(r'[0-9]', out) else 0.0
            blended = (3 * inp_num + out_num) / 4.0 if (inp_num or out_num) else 0.0
            console_models.append({
                'name': mname,
                'input': inp_num,
                'output': out_num,
                'cached_read': cached_read,
                'cached_write': cached_write,
                'monthly_limit': lim,
                'blended': blended
            })
    # Parse Privacy table
    privacy_info = {}
    privacy_match = re.search(r'<h2 id=\"privacy\">Privacy</h2>(.*?)(?:<h2|$)', doc_html, re.DOTALL)
    if privacy_match:
        p_rows = re.findall(r'<tr>(.*?)</tr>', privacy_match.group(1), re.DOTALL)
        for pr in p_rows[1:]:
            p_cols = [re.sub(r'<[^>]+>', '', c).strip() for c in re.findall(r'<t[dh]>(.*?)</t[dh]>', pr, re.DOTALL)]
            if len(p_cols) >= 3:
                p_name = p_cols[0]
                p_train = p_cols[1]
                p_ret = p_cols[2]
                privacy_info[p_name.lower()] = {
                    'training': p_train,
                    'retention': p_ret,
                    'trains_on_data': (p_train.lower() == 'yes')
                }
    print(f"   Successfully parsed privacy terms for {len(privacy_info)} models!")
    print(f"   Successfully parsed {len(console_models)} official model rows from /v2/docs/console/go/!")
except Exception as e:
    print(f"   Console doc fetch note ({e}), using cached fallback.")
    if os.path.exists(os.path.join(DATA_DIR, "opencode_console_go_table.json")):
        console_models = json.load(open(os.path.join(DATA_DIR, "opencode_console_go_table.json")))
    privacy_info = {}

# 2. Fetch 5h limits from opencode.ai/go
go_limits = {}
print("2. Fetching 5-hour rolling request limits from opencode.ai/go...")
try:
    go_html = fetch_url("https://opencode.ai/go")
    asset_match = re.search(r'href="(/_build/assets/index-[^"]+\.js)"', go_html)
    if asset_match:
        js_text = fetch_url(f"https://opencode.ai{asset_match.group(1)}")
        start_idx = js_text.find("const goModels = [")
        if start_idx != -1:
            end_idx = js_text.find("];", start_idx) + 1
            items = re.findall(r'\{[^{}]+\}', js_text[start_idx:end_idx])
            for it in items:
                mid = re.search(r'id:\s*"([^"]+)"', it)
                reqs = re.search(r'requests:\s*([0-9.]+)', it)
                if mid and reqs:
                    go_limits[mid.group(1)] = float(reqs.group(1))
    if not go_limits and os.path.exists(os.path.join(DATA_DIR, "opencode_go_models.json")):
        for m in json.load(open(os.path.join(DATA_DIR, "opencode_go_models.json"))):
            go_limits[m['id']] = m.get('requests_5h')
    print(f"   Found 5-hour limits for {len(go_limits)} models!")
except Exception as e:
    print(f"   Go limits note ({e}), using cached fallback.")
    if os.path.exists(os.path.join(DATA_DIR, "opencode_go_models.json")):
        for m in json.load(open(os.path.join(DATA_DIR, "opencode_go_models.json"))):
            go_limits[m['id']] = m.get('requests_5h')

# 3. Fetch latest Artificial Analysis benchmark snapshot
print("3. Fetching latest Artificial Analysis benchmark snapshot...")
try:
    aa_text = fetch_url("https://bestmodelforyourbudget.terrydjony.com/data/models.json")
    aa_data = json.loads(aa_text)
    with open(os.path.join(DATA_DIR, "models.json"), "w") as f:
        f.write(aa_text)
    with open(os.path.join(DATA_DIR, "models.js"), "w") as f:
        f.write("window.__MODELS_DATA__ = " + aa_text + ";")
    print(f"   Successfully fetched {len(aa_data.get('models', []))} models from Artificial Analysis!")
except Exception as e:
    print(f"   AA snapshot fetch note ({e}), using cached fallback.")
    with open(os.path.join(DATA_DIR, "models.json")) as f:
        aa_data = json.load(f)
aa_models = aa_data.get("models", [])

aliases = {
    'glm53flash': 'glm 5.3 flash',
    'deepseekv41flash': 'deepseek v4.1 flash',
    'deepseekflash': 'deepseek v4 flash',
    'gpt6luna': 'gpt-6 luna',
    'gpt56luna': 'gpt-5.6 luna',
    'mimov26flash': 'mimo-v2.6-flash',
    'mimov26pro': 'mimo-v2.6-pro',
    'musespark13contributor': 'muse spark 1.3',
    'musespark12contributor': 'muse spark 1.2',
    'qwen38flash': 'qwen3.8-flash-next',
    'qwen38max': 'qwen3.8 max',
    'qwen37plus': 'qwen3.7 plus',
    'qwen37max': 'qwen3.7 max',
    'kimik3': 'kimi k3',
    'kimik27code': 'kimi k2.7 code',
    'kimik26': 'kimi k2.6',
    'grok47': 'grok 4.7',
    'grok46': 'grok 4.6',
    'grok45': 'grok 4.5',
    'glm53': 'glm-5.3',
    'glm52': 'glm-5.2',
    'minimaxm3': 'minimax-m3',
    'minimaxm27': 'minimax-m2.7',
    'spacebunny': 'step 3.5 flash',
    'spacebunnyfree': 'step 3.5 flash',
    'hy3': 'glm 5.3 flash',
    'hy4preview': 'step 5 preview',
    'mimov26flashfree': 'mimo-v2.6-flash',
    'mimov25free': 'mimo-v2.5',
    'ling31flashfree': 'ling 3.1 flash',
    'ling30flashfinfree': 'ling 3.0 flash',
    'nemotron3ultrafree': 'nemotron 3 ultra 550b',
    'nemotron35lightningfree': 'nemotron 3.5 lightning',
    'musespark13contributorfree': 'muse spark 1.3',
    'longcat25previewfree': 'longcat 2.0'
}

def normalize(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower())

def find_aa(name):
    clean = re.sub(r'\(.*?\)', '', name).strip()
    norm = normalize(clean)
    target = aliases.get(norm)
    cands = []
    if target:
        for m in aa_models:
            if target in m['name'].lower() and m.get('index') is not None:
                cands.append(m)
    if not cands:
        for m in aa_models:
            mn = normalize(m['name'])
            if (norm in mn or mn in norm) and m.get('index') is not None:
                cands.append(m)
    if cands:
        # Prefer the best (Max / Reasoning / highest index) variant
        cands.sort(key=lambda x: (x.get('index') or 0), reverse=True)
        return cands[0]
    return None

def make_slug(name):
    clean = re.sub(r'\(.*?\)', '', name).strip().lower()
    return re.sub(r'[^a-z0-9.]+', '-', clean).strip('-')

final_models = []
for m in console_models:
    name = m['name']
    allowance = m['monthly_limit']
    multiplier = (allowance / 10.0) if allowance > 0 else 1.0
    blended = m['blended']
    effective_price = blended / multiplier if multiplier > 0 else blended
    quota_burn = (blended / allowance * 100.0) if allowance > 0 else 0.0

    slug = make_slug(name)
    requests_5h = go_limits.get(slug)

    aa = find_aa(name)
    index_score = aa['index'] if aa else None
    coding_score = aa.get('coding') if aa else None
    tps = aa.get('tps') if aa else None
    aa_name = aa['name'] if aa else None

    maker = "OpenCode Go"
    nl = name.lower()
    if 'glm' in nl: maker = "Zhipu AI"
    elif 'qwen' in nl: maker = "Alibaba Cloud"
    elif 'deepseek' in nl: maker = "DeepSeek"
    elif 'mimo' in nl: maker = "Xiaomi"
    elif 'kimi' in nl: maker = "Moonshot AI"
    elif 'grok' in nl: maker = "xAI"
    elif 'minimax' in nl: maker = "MiniMax"
    elif 'muse' in nl: maker = "Meta"
    elif 'gpt' in nl or 'luna' in nl: maker = "OpenCode"
    elif 'longcat' in nl: maker = "LongCat"
    p_entry = privacy_info.get(name.lower(), {})
    if not p_entry:
        # fuzzy match
        for pk, pv in privacy_info.items():
            if pk in name.lower() or name.lower() in pk:
                p_entry = pv
                break

    trains_on_data = p_entry.get('trains_on_data', False)
    retention = p_entry.get('retention', '0 days')
    privacy_note = 'Model training (Yes)' if trains_on_data else f"No training · {retention}"

    task_cost = aa.get('task') if aa else None
    effective_task = (task_cost / multiplier) if (task_cost is not None and multiplier > 0) else task_cost

    final_models.append({
        'id': f'opencode-go/{slug}',
        'go_id': slug,
        'name': name,
        'creator': maker,
        'allowance': allowance,
        'requests_5h': requests_5h,
        'multiplier': multiplier,
        'input': m['input'],
        'output': m['output'],
        'cached_read': m['cached_read'],
        'cached_write': m['cached_write'],
        'blended': blended,
        'effective_price': effective_price,
        'task': task_cost,
        'effective_task': effective_task,
        'quota_burn': quota_burn,
        'trains_on_data': trains_on_data,
        'retention': retention,
        'privacy_note': privacy_note,
        'index': index_score,
        'coding': coding_score,
        'tps': tps,
        'aa_name': aa_name
    })

# Save outputs for Go models
with open(os.path.join(DATA_DIR, "opencode_go_complete.json"), "w") as f:
    json.dump(final_models, f, indent=2)

with open(os.path.join(DATA_DIR, "opencode_go_complete.js"), "w") as f:
    f.write("window.__OPENCODE_GO_MODELS__ = " + json.dumps(final_models) + ";")

print(f"4. Done! Successfully synced {len(final_models)} models directly from /v2/docs/console/go/!")

# 5. Fetch official Zen documentation from opencode.ai/v2/docs/console/models/ and aggregate Free Models
print("5. Fetching Zen free models from opencode.ai/v2/docs/console/models/...")
free_models = []
try:
    zen_html = fetch_url("https://opencode.ai/v2/docs/console/models/")
    # Endpoints map
    z_tables = re.findall(r'<table[^>]*>(.*?)</table>', zen_html, re.DOTALL)
    zen_endpoints = {}
    if len(z_tables) >= 1:
        for r in re.findall(r'<tr[^>]*>(.*?)</tr>', z_tables[0], re.DOTALL)[1:]:
            cols = [re.sub(r'<[^>]+>', '', c).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', r, re.DOTALL)]
            if len(cols) >= 3:
                zen_endpoints[cols[0]] = {
                    'model_id': cols[1],
                    'endpoint': cols[2]
                }

    # Privacy notes in Zen
    zen_privacy = {}
    z_priv_sec = re.search(r'<h2 id=\"privacy\">Privacy</h2>(.*?)(?:<h[12]|$)', zen_html, re.DOTALL)
    if z_priv_sec:
        for li in re.findall(r'<li>(.*?)</li>', z_priv_sec.group(1), re.DOTALL):
            cli = re.sub(r'<[^>]+>', '', li).strip()
            parts = cli.split(':', 1)
            if len(parts) == 2:
                zen_privacy[parts[0].strip().lower()] = parts[1].strip()

    # Free pricing rows
    if len(z_tables) >= 2:
        for r in re.findall(r'<tr[^>]*>(.*?)</tr>', z_tables[1], re.DOTALL)[1:]:
            cols = [re.sub(r'<[^>]+>', '', c).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', r, re.DOTALL)]
            if len(cols) >= 3:
                mname = cols[0]
                inp = cols[1]
                out = cols[2]
                cached_r = cols[3] if len(cols) > 3 else '-'
                if inp.lower() == 'free' or out.lower() == 'free' or 'free' in mname.lower():
                    ep_info = zen_endpoints.get(mname, {})
                    mid = ep_info.get('model_id', make_slug(mname))
                    endpoint = ep_info.get('endpoint', 'https://opencode.ai/zen/v1/chat/completions')
                    
                    # privacy & training
                    trains = False
                    p_text = ""
                    nl = mname.lower()
                    for pk, pv in zen_privacy.items():
                        if pk in nl or nl in pk:
                            p_text = pv
                            if 'used to improve' in pv.lower() or 'train' in pv.lower():
                                trains = True
                            break
                    if not p_text:
                        if 'space bunny' in nl or 'longcat' in nl:
                            p_text = "Zero retention, no training"
                            trains = False
                        elif 'contributor' in nl or 'free' in nl:
                            p_text = "Data may be used for model training during free period"
                            trains = True

                    # manufacturer
                    maker = "OpenCode Zen"
                    if 'mimo' in nl: maker = "Xiaomi"
                    elif 'ling' in nl: maker = "Ling AI"
                    elif 'nemotron' in nl: maker = "NVIDIA"
                    elif 'muse' in nl: maker = "Meta"
                    elif 'longcat' in nl: maker = "LongCat"
                    elif 'bunny' in nl: maker = "Tencent / Step"
                    elif 'fledge' in nl: maker = "Fledge"
                    elif 'pickle' in nl: maker = "Stealth"
                    elif 'jev' in nl: maker = "TypeSafe"

                    # benchmarks
                    aa = find_aa(mname)
                    idx = aa['index'] if aa else None
                    coding = aa.get('coding') if aa else None
                    tps = aa.get('tps') if aa else None
                    aa_name = aa['name'] if aa else None

                    # Also check if it is available in Go
                    go_match = [gm for gm in final_models if gm['name'].lower() == mname.lower() or gm['go_id'] == mid]
                    available_in_go = len(go_match) > 0
                    go_limit = go_match[0]['allowance'] if available_in_go else None

                    free_models.append({
                        'id': f'free/{mid}',
                        'name': mname,
                        'model_id': mid,
                        'creator': maker,
                        'catalog': 'Zen & Go' if available_in_go else 'Zen Only',
                        'available_in_go': available_in_go,
                        'available_in_zen': True,
                        'input': inp,
                        'output': out,
                        'cached_read': cached_r,
                        'trains_on_data': trains,
                        'privacy_note': p_text or ("Model training (Yes)" if trains else "No training"),
                        'endpoint': endpoint,
                        'index': idx,
                        'coding': coding,
                        'tps': tps,
                        'aa_name': aa_name,
                        'go_allowance': go_limit
                    })
    print(f"   Successfully collected {len(free_models)} free models from OpenCode Zen!")
except Exception as e:
    print(f"   Zen doc fetch note ({e})")

# Save Free Models dataset
with open(os.path.join(DATA_DIR, "opencode_free_models.json"), "w") as f:
    json.dump(free_models, f, indent=2)

with open(os.path.join(DATA_DIR, "opencode_free_models.js"), "w") as f:
    f.write("window.__OPENCODE_FREE_MODELS__ = " + json.dumps(free_models) + ";")

print(f"6. Complete! Exported {len(free_models)} Free Models to data/opencode_free_models.json and .js!")
