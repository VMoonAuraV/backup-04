#!/usr/bin/env python3
"""Sync a Context Lab browser export to GitHub and prepare a review pack.
Uses only Python's standard library and the local Git CLI. Never stores tokens in the app.
"""
import argparse, json, subprocess, sys
from datetime import datetime, timezone, date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'docs/packs/starter.json'; LATEST=ROOT/'progress/latest.json'; REVIEW=ROOT/'docs/mobile/review-pack.json'
def read(path):
    with path.open(encoding='utf-8') as f: return json.load(f)
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*args):
    p=subprocess.run(['git',*args],cwd=ROOT,text=True,encoding='utf-8',errors='replace',capture_output=True)
    if p.returncode: raise RuntimeError((p.stderr or p.stdout or f'git {args} failed').strip())
    return p.stdout.strip()
def unpack(data):
    if data.get('type') not in ('context-lab-progress','context-lab-backup'): raise ValueError('请导入 Context Lab 导出的同步记录或完整备份 JSON。')
    state=data.get('state')
    if not isinstance(state,dict) or not isinstance(state.get('words',{}),dict) or not isinstance(state.get('log'),list): raise ValueError('学习记录结构不完整。')
    state.setdefault('quiz',{}); state.setdefault('words',{}); state.setdefault('created',int(datetime.now(timezone.utc).timestamp()*1000))
    state.setdefault('updatedAt',data.get('exportedAt') or datetime.now(timezone.utc).isoformat())
    cp=data.get('contentPack') or {'id':(data.get('pack') or {}).get('id','gre-core-context-01'),'version':(data.get('pack') or {}).get('version','unknown')}
    return state,cp
def make_review_pack(content,state):
    today=date.today().isoformat(); perf=state.get('words',{}); logs=state.get('log',[]); wrong={}
    for row in logs[-1500:]:
        if row.get('correct') is False and row.get('wordId'): wrong[row['wordId']]=wrong.get(row['wordId'],0)+1
    scores={}; reasons={}
    for w in content['words']:
        p=perf.get(w['id'],{}); seen=int(p.get('seen',0) or 0); err=int(p.get('wrong',0) or 0); cor=int(p.get('correct',0) or 0); due=str(p.get('due',''))
        score=(1 if not seen else 0)+(5 if seen and due and due<=today else 0)+2*min(err,5)+2*min(wrong.get(w['id'],0),4)+(2 if seen and err>cor else 0)
        scores[w['id']]=score; reasons[w['id']]=(['尚未学习'] if not seen else [])+(['已到复习时间'] if seen and due and due<=today else [])+(['曾出现错误'] if err or wrong.get(w['id'],0) else [])
    chosen=sorted(content['words'],key=lambda w:(scores[w['id']],w['id']),reverse=True)[:18]; ids={w['id'] for w in chosen}
    def related(items,limit): return sorted([q for q in items if ids.intersection(q.get('words',[]))],key=lambda q:(sum(scores.get(i,0) for i in q.get('words',[])),q['id']),reverse=True)[:limit]
    return {'type':'context-lab-review-pack','schemaVersion':1,'generatedAt':datetime.now(timezone.utc).isoformat(),'sourceProgressUpdatedAt':state.get('updatedAt',''),'contentPack':{'id':content.get('id'),'version':content.get('version')},'selectionPolicy':'Due words and repeated errors first; unseen words remain for coverage.','words':[{**w,'reviewReason':reasons[w['id']] or ['常规巩固']} for w in chosen],'comparisons':related(content.get('comparisons',[]),10),'se':related(content.get('se',[]),8)}
def build(_):
    content=read(CONTENT); state,cp=unpack(read(LATEST)) if LATEST.exists() else ({'words':{},'log':[],'quiz':{},'updatedAt':''},{})
    write(REVIEW,make_review_pack(content,state)); print('Review pack generated:',REVIEW.relative_to(ROOT))
def push(args):
    source=Path(args.file).expanduser().resolve()
    if not source.is_file(): raise FileNotFoundError(f'找不到导出文件：{source}')
    if not (ROOT/'.git').exists(): raise RuntimeError('请先将 backup-04 克隆到本地，再运行此脚本。')
    git('pull','--rebase'); data=read(source); state,cp=unpack(data); incoming=str(state.get('updatedAt',''))
    if LATEST.exists():
        old,_=unpack(read(LATEST)); oldtime=str(old.get('updatedAt',''))
        if old==state: print('学习记录没有变化；无需提交。'); return
        if oldtime and incoming and incoming<=oldtime and not args.force: raise RuntimeError('远程记录时间戳不早于本地记录，已拒绝覆盖。先导入 progress/latest.json；确认覆盖时可添加 --force。')
    now=datetime.now(timezone.utc); canonical={'type':'context-lab-progress','version':1,'exportedAt':data.get('exportedAt') or now.isoformat(),'contentPack':cp,'state':state}
    write(LATEST,canonical); history=ROOT/'progress/history'/(now.strftime('%Y-%m-%dT%H%M%SZ')+'.json'); write(history,canonical)
    write(REVIEW,make_review_pack(read(CONTENT),state)); git('add','progress/latest.json',str(history.relative_to(ROOT)),'docs/mobile/review-pack.json')
    diff=subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT).returncode
    if diff==0: print('没有可提交的变化。'); return
    git('commit','-m',f'Sync GRE learning progress {now:%Y-%m-%d}'); git('push')
    print('同步完成：最新记录、历史快照与复习包已推送到 GitHub。')
def main():
    p=argparse.ArgumentParser(description='GRE Context Lab desktop progress sync'); sub=p.add_subparsers(dest='cmd',required=True)
    b=sub.add_parser('build-review-pack'); b.set_defaults(func=build)
    s=sub.add_parser('push'); s.add_argument('file'); s.add_argument('--force',action='store_true'); s.set_defaults(func=push)
    args=p.parse_args()
    try: args.func(args)
    except Exception as e: print('ERROR:',e,file=sys.stderr); return 1
    return 0
if __name__=='__main__': raise SystemExit(main())
