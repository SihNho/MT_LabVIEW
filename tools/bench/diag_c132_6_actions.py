"""card 132-6 diag (offline, read-only): are the recovered provisional plan's actions (98992a59), rebased in the temp dir by
stage_prerun --rebase, identical to the actions of 31bea1c5 (= the old b25c1ecb rebased by card 132-5)?"""
import glob, json, os                                                              # noqa: E401
old = json.load(open('tools/bench/plan_ring_p3b2_rebased_c132_5.json', encoding='utf-8'))
tmp = sorted(glob.glob(os.path.join(os.environ.get('TEMP', ''), 'rebase_*', 'plan_ring_p3b2.json')), key=os.path.getmtime)
print('temp rebased plans', tmp[-3:])
new = json.load(open(tmp[-1], encoding='utf-8'))
a, b = old['actions'], new['actions']
print('n actions old/new', len(a), len(b))
diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
print('differing action indexes', diff[:20])
for i in diff[:3]:
    print(' old', json.dumps(a[i])[:300])
    print(' new', json.dumps(b[i])[:300])
print('open_rows equal', old.get('open_rows') == new.get('open_rows'), 'base old', old.get('base'), 'base new', new.get('base'))
