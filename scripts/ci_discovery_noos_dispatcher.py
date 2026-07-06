#!/usr/bin/env python3
"""CI discovery check for NOOS Copilot dispatcher registration.

Checks:
- data/package_map.json contains key noos-copilot-dispatcher-mode
- resolves to a file that exists
- required fields in machine record exist

Writes result to receipts/ci-discovery-noos-dispatcher.json and prints JSON summary.
Exit code 0 always (non-enforcing); callers may inspect output.
"""
from __future__ import annotations
import json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
out_path = root / 'receipts' / 'ci-discovery-noos-dispatcher.json'
summary = {'ok': True, 'checks': []}
try:
    pm = json.loads((root / 'data' / 'package_map.json').read_text(encoding='utf-8'))
except Exception as e:
    summary['ok'] = False
    summary['checks'].append({'package_map_readable': False, 'error': str(e)})
    print(json.dumps(summary, indent=2))
    out_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    raise SystemExit(0)
key = 'noos-copilot-dispatcher-mode'
if key not in pm:
    summary['ok'] = False
    summary['checks'].append({'package_map_has_key': False})
else:
    summary['checks'].append({'package_map_has_key': True, 'key': key, 'value': pm[key]})
    target = root / pm[key]
    if not target.exists():
        summary['ok'] = False
        summary['checks'].append({'target_exists': False, 'target': str(target)})
    else:
        summary['checks'].append({'target_exists': True, 'target': str(target)})
        try:
            mr = json.loads(target.read_text(encoding='utf-8'))
            required = ['schema','version','default_allowed_modes','blocked_modes','cloud_write_scopes','enforcement']
            missing = [f for f in required if f not in mr]
            if missing:
                summary['ok'] = False
                summary['checks'].append({'machine_record_required_fields_present': False, 'missing': missing})
            else:
                summary['checks'].append({'machine_record_required_fields_present': True})
        except Exception as e:
            summary['ok'] = False
            summary['checks'].append({'machine_record_readable': False, 'error': str(e)})
# write receipt and print
out_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary, indent=2))
raise SystemExit(0)
