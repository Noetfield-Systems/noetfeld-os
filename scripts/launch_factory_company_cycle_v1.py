#!/usr/bin/env python3
"""Compile scoped Launch Factory plan candidates into existing NOOS role assignments.

Pure translation, not actual governor approval, dispatch, production deploy or token mint.
Independent ventures are rejected at this NOETFIELD COMPANY boundary. Their own
Company OS must consume portfolio candidates under their specific venture permit.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=json.loads((ROOT/'data/launch-factory-company-cycle-v1.json').read_text())
COMPANY_ID='noetfield-systems-inc'
def compile_intake(plan:dict)->dict:
    if not isinstance(plan,dict) or plan.get('schema')!='sina.launch-factory.plan.v1':
        raise ValueError('Only canonical launch-factory plan v1 accepted')
    project=plan.get('project') or {}
    if project.get('venture_boundary')!='company_project' or project.get('company_id')!=COMPANY_ID:
        raise ValueError('Independent venture must use its own Company OS; NOOS cannot inherit it')
    if plan.get('routing',{}).get('intent_owner')!='SINA_FOUNDER_OS':
        raise ValueError('Missing canonical Sina Founder OS intent provenance')
    if not isinstance(plan.get('workpackets'),list) or not plan['workpackets']:
        raise ValueError('No candidate WorkPackets')
    seen=set();out=[]
    for candidate in plan['workpackets']:
        if candidate.get('company_id')!=COMPANY_ID or candidate.get('project_id')!=project.get('project_id'):
            raise ValueError('Cross-project/tenant WorkPacket denied')
        cid=candidate.get('workpacket_candidate_id')
        if not isinstance(cid,str) or not cid or cid in seen:
            raise ValueError('Invalid/duplicate WorkPacket ID')
        seen.add(cid)
        role=candidate.get('role')
        worker=CONTRACT['roles'].get(role)
        if worker is None: raise ValueError('Unknown specialist role')
        if candidate.get('dispatch_state')!='NOT_DISPATCHED':
            raise ValueError('Only pre-dispatch candidates accepted')
        signer=candidate.get('external_effect')=='MAINNET_SIGNER_REQUIRED'
        out.append({'candidate_id':cid,'project_id':project['project_id'],'company_id':COMPANY_ID,
                    'noos_role_id':worker,'objective':candidate.get('action'),'acceptance':candidate.get('required_proof'),
                    'external_effect':'SIGNER_REQUIRED' if signer else 'NONE',
                    'next_existing_flow':'EXISTING_GOVERNOR_SIGNER_PATH' if signer else 'EXISTING_NOOS_MISSION_INTAKE',
                    'execution_status':'NOT_DISPATCHED','source_candidate_id':cid})
    source=hashlib.sha256(json.dumps(plan,sort_keys=True).encode()).hexdigest()
    return {'schema':'noos.launch-factory.company-intake.v1',
            'project_id':project['project_id'],'company_id':COMPANY_ID,'source_plan_sha256':source,
            'contract_version':CONTRACT['version'],'role_mapped_candidates':out,
            'dispatch_state':'NOT_DISPATCHED','money_transferred':False,'mainnet_token_issued':False,
            'existing_governor_authority_required':True}
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('plan',type=Path)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    payload=compile_intake(json.loads(args.plan.read_text()))
    body=json.dumps(payload,indent=2)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open('x') as f:f.write(body)
    else: print(body,end='')
if __name__=='__main__':main()
