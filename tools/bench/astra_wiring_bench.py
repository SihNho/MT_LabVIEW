"""Isolated 15-connection Index Array benchmark. No hardware dependencies.
Prediction: five IndexArray nodes, one array input, five index inputs, five
outputs. Only a verified pure diagram may execute. Stop on the first mismatch.
"""
import gc, hashlib, json, shutil, sys, time
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gscript as g

def run(vi, *args, **kwargs):
    return g._invoke(vi, 'Run', hard_timeout_s=20)
g._run = run  # No GUI watchdog actions; unexpected outcomes stop the batch.
ROOT = Path(__file__).resolve().parent
TARGET = str(Path(g.CLAUDEDEV) / 'ASTRA_WIRING_20260913_v1.vi')
SEED = Path(g.CLAUDEDEV) / 'FPTARGET_v0.vi'
result = {'target': TARGET, 'passed': False, 'steps': []}

def step(label, fn):
    t = time.perf_counter()
    value = fn()
    result['steps'].append({'step': label, 'seconds': time.perf_counter()-t})
    print(label, repr(value), flush=True)
    return value

def purge_invokes():
    for _ in range(g.count(TARGET, 'Invoke')):
        g.delete_object(TARGET, 'Invoke', 0)
    g.remove_bad_wires_scripted(TARGET)

try:
    assert not Path(TARGET).exists(), 'Never overwrite an existing VI'
    digest = hashlib.sha256(SEED.read_bytes()).hexdigest()
    shutil.copyfile(SEED, TARGET)
    g.report(TARGET, 'Node')
    g.open_panel(TARGET)
    for _ in range(g.count(TARGET, 'Node')):
        g.delete_object(TARGET, 'Node', 0)
    g.remove_bad_wires_scripted(TARGET)
    # Unused inherited controls remain; they carry no executable code.
    assert g.count(TARGET, 'Node') == 0
    start = time.perf_counter()
    for i in range(5):
        step('place '+str(i), lambda i=i: g.build_index_array(TARGET, (400, 100+i*100)))
    purge_invokes()
    nodes = g.report(TARGET, 'Node')
    assert len(nodes) == 5 and all(n['class'] == 'IndexArray' for n in nodes), nodes
    new, arr = step('array input', lambda: g.create_control(TARGET, 0, 0))
    assert len(new) == 1 and arr
    indices, outputs = [], []
    for i in range(5):
        if i:
            step('array branch '+str(i), lambda i=i: g.wire_control(TARGET, [arr], 'IndexArray', i, ['array'], branch=True))
        new, label = step('index input '+str(i), lambda i=i: g.create_control(TARGET, i, 2))
        assert len(new) == 1 and label
        indices.append(label)
        old_count = g.count(TARGET, 'ControlTerminal')
        new = step('output '+str(i), lambda i=i: g.create_indicator(TARGET, i, 1))
        assert len(new) == 1
        labels = g.fp_labels(TARGET, max_n=old_count+1)
        outputs.append(labels[-1][1])
    result['build_seconds'] = time.perf_counter()-start
    purge_invokes()
    nodes = g.report(TARGET, 'Node')
    assert len(nodes) == 5 and all(n['class'] == 'IndexArray' for n in nodes), nodes
    assert g.exec_state(TARGET) == 1
    result['labels'] = {'array': arr, 'indices': indices, 'outputs': outputs}
    result['cases'] = []
    vi = g.op(TARGET)
    for k in range(8):
        values = [float(100*k+j*7-13) for j in range(9)]
        ix = [(k+2*j)%9 for j in range(5)]
        vi.SetControlValue(arr, values)
        assert list(vi.GetControlValue(arr)) == values
        for label, value in zip(indices, ix):
            vi.SetControlValue(label, value)
            assert int(vi.GetControlValue(label)) == value
        run(vi)
        actual = [vi.GetControlValue(label) for label in outputs]
        expected = [values[j] for j in ix]
        result['cases'].append({'indices': ix, 'expected': expected, 'actual': actual})
        assert actual == expected, result['cases'][-1]
    step('save', lambda: g.save(TARGET))
    assert hashlib.sha256(SEED.read_bytes()).hexdigest() == digest
    result['passed'] = True
    print('PASS', json.dumps(result), flush=True)
except Exception as exc:
    result['error'] = repr(exc)
    print('FAIL', repr(exc), flush=True)
    raise
finally:
    (ROOT / 'astra_wiring_result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    if 'vi' in globals():
        vi = None
    g._cache.clear()
    g._lv = None
    gc.collect()
