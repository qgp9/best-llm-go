"""Shared helpers for the OpenCode console provider catalog.

build_console_catalog.py writes data/console_models.json from the console API;
these helpers read it and resolve model ids, limits and paid counterparts of
free models. The catalog is optional: every helper degrades to "no data" when
the file is missing, so the pipeline keeps working from the documentation
pages alone.
"""

import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONSOLE_PATH = os.path.join(BASE_DIR, "data", "console_models.json")

# provider order decides which price wins when a model is offered twice
PROVIDER_ORDER = ('opencode-go', 'opencode', 'console-openrouter', 'console-nvidia')


def key(text):
    return re.sub(r'[^a-z0-9]', '', (text or '').lower())


def load(path=CONSOLE_PATH):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding='utf-8') as f:
            return (json.load(f) or {}).get('providers') or {}
    except (OSError, ValueError):
        return {}


def build_index(providers):
    """Index every console model by normalized id and provider.

    Keys are the last path segment, so OpenRouter ids such as
    "minimax/minimax-m3.1-flash" match the plain "minimax-m3.1-flash" used by
    the OpenCode providers.
    """
    entries = []
    ordered = sorted((providers or {}).items(),
                     key=lambda kv: PROVIDER_ORDER.index(kv[0])
                     if kv[0] in PROVIDER_ORDER else len(PROVIDER_ORDER))
    for provider_key, provider in ordered:
        for model_id, model in (provider.get('models') or {}).items():
            entries.append({
                'id': model_id,
                'key': key((model_id or '').split('/')[-1]),
                'name_key': key(model.get('name')),
                'provider': provider_key,
                'model': model,
            })
    return entries


def lookup(entries, wanted, allow_prefix=True):
    """Exact match first, then a prefix match (nemotron-3-ultra -> ...-550b).

    The wanted id may carry a provider prefix ("nvidia/nemotron-3-ultra");
    entries are keyed by their last path segment, so both forms are tried.
    """
    candidates = []
    for text in (wanted, (wanted or '').split('/')[-1]):
        target = key(text)
        if target and target not in candidates:
            candidates.append(target)
    for target in candidates:
        for entry in entries:
            if entry['key'] == target or entry['name_key'] == target:
                return entry
    if not allow_prefix:
        return None
    for target in candidates:
        for entry in entries:
            if entry['key'].startswith(target) and len(entry['key']) - len(target) <= 24:
                return entry
    return None


def price_info(entry):
    model = entry['model']
    cost_in = model.get('cost_input')
    cost_out = model.get('cost_output')
    if not cost_in and not cost_out:
        return None
    return {
        'id': entry['id'],
        'provider': entry['provider'],
        'input': cost_in,
        'output': cost_out,
        'context_limit': model.get('context_limit'),
    }


def _common_prefix(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def base_model_for(free_id, entries, go_rows=None, family=None, provider=None):
    """Find the paid counterpart of a free model and its list price.

    The result carries a `relation` telling how sure the match is:
    `same` (identical model id), `sibling` (one id is a prefix of the other,
    e.g. nemotron-3-ultra -> nemotron-3-ultra-550b-a55b) or `family`
    (same model family, only when the names still share a long prefix).
    """
    stripped = free_id[:-5] if free_id.endswith('-free') else free_id
    if ':free' in free_id:
        stripped = free_id.replace(':free', '')
    target = key(stripped.split('/')[-1])
    best = None
    for entry in entries:
        price = price_info(entry)
        if not price:
            continue
        entry_key = entry['key']
        same_provider = 1 if (provider and entry['provider'] == provider) else 0
        if entry_key == target or entry['name_key'] == target:
            score, common = 3, len(target)
        elif target.startswith(entry_key) and len(target) - len(entry_key) <= 12:
            score, common = 2, len(entry_key)
        elif entry_key.startswith(target) and len(entry_key) - len(target) <= 24:
            score, common = 2, len(target)
        elif family and entry['model'].get('family') == family:
            common = _common_prefix(entry_key, target)
            if common < 8:
                continue
            score = 1
        else:
            continue
        rank = (score, same_provider, common, price['input'] or 0)
        if best is None or rank > best[0]:
            best = (rank, price, score)
    if best:
        price = dict(best[1])
        price['relation'] = {3: 'same', 2: 'sibling', 1: 'family'}[best[2]]
        return price
    for row in (go_rows or []):
        row_key = key(row.get('go_id'))
        if row.get('input') and row_key in (key(free_id), target):
            return {
                'id': row['go_id'],
                'provider': 'opencode-go',
                'input': row['input'],
                'output': row['output'],
                'context_limit': None,
                'relation': 'same',
            }
    return None
