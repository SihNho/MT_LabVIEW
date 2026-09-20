"""GUI benchmark preparation and read-only result verification. No GUI input."""
import sys, gc, json, time, shutil
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import gscript as g
g._run=lambda vi,*a,**kw:g._invoke(vi,'Run',hard_timeout_s=20)
root=Path(__file__).resolve().parent
target=str(Path(g.CLAUDEDEV)/'ASTRA_GUIBENCH_20260913.vi')
statefile=root/'astra_gui_state.json'
cmd=sys.argv[1]
try:
    if cmd=='prepare':
        assert not Path(target).exists()
        shutil.copyfile(Path(g.CLAUDEDEV)/'GUIBENCH_v0.vi',target)
        g.report(target,'Node');g.open_panel(target)
        print('PREPARED',target)
    elif cmd=='before':
        op,trial=sys.argv[2:4]
        g.revert(target)
        state={'op':op,'trial':trial,'uids':sorted(g.uids(target,'IndexArray')),
               'invoke':[n for n in g.report(target,'Invoke') if n['uid']==538][0]['pos'],
               'exec':g.exec_state(target),'t0':time.time()}
        statefile.write_text(json.dumps(state))
        print('READY',op,trial)
    elif cmd=='after':
        s=json.loads(statefile.read_text()); op=s['op']; info={}
        if op=='U1':
            pos=[n for n in g.report(target,'Invoke') if n['uid']==538][0]['pos']
            delta=[pos[i]-s['invoke'][i] for i in range(2)]
            ok=((delta[0]-100)**2+(delta[1]-50)**2)**0.5<=6
            info={'delta':delta}
        elif op=='U2':
            new=[n for n in g.report(target,'IndexArray') if n['uid'] not in s['uids']]
            ok=len(new)==1 and ((new[0]['pos'][0]+8-1100)**2+(new[0]['pos'][1]+8-600)**2)**0.5<=12
            info={'new':new}
        elif op=='U4':
            es=g.exec_state(target);ok=s['exec']==1 and es==0;info={'exec':es}
        else: raise ValueError(op)
        rec={'op':op,'trial':s['trial'],'ok':ok,'seconds':time.time()-s['t0'],**info}
        with (root/'astra_gui_results.jsonl').open('a') as f:f.write(json.dumps(rec)+'\n')
        print(json.dumps(rec))
    elif cmd=='reset':
        g.revert(target);print('RESET')
finally:
    g._cache.clear();g._lv=None;gc.collect()
