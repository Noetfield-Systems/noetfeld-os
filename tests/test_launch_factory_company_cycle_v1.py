import importlib.util
import unittest
from pathlib import Path

FILE=Path(__file__).resolve().parents[1]/'scripts/launch_factory_company_cycle_v1.py'
spec=importlib.util.spec_from_file_location('lf_company',FILE)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def fixture(company='noetfield-systems-inc',boundary='company_project'):
    return {'schema':'sina.launch-factory.plan.v1','project':{'project_id':'test-noetfield-product','company_id':company,'venture_boundary':boundary},
       'routing':{'intent_owner':'SINA_FOUNDER_OS'},
       'workpackets':[{'workpacket_candidate_id':'candidate-123','company_id':company,'project_id':'test-noetfield-product',
           'role':'Engineering','dispatch_state':'NOT_DISPATCHED','external_effect':'NONE','action':'Publish site','required_proof':'Live SHA'}]}
class TestFactoryIntake(unittest.TestCase):
    def test_maps_to_existing_role_without_dispatch(self):
        r=mod.compile_intake(fixture())
        self.assertEqual(r['role_mapped_candidates'][0]['noos_role_id'],'N-03')
        self.assertEqual(r['dispatch_state'],'NOT_DISPATCHED')
        self.assertFalse(r['mainnet_token_issued'])
    def test_does_not_cross_venture(self):
        with self.assertRaisesRegex(ValueError,'Independent venture'):mod.compile_intake(fixture(None,'independent_venture'))
    def test_rejects_mismatch_and_duplicate(self):
        x=fixture();x['workpackets'][0]['project_id']='other'
        with self.assertRaisesRegex(ValueError,'Cross-project'):mod.compile_intake(x)
        x=fixture();x['workpackets'].append(dict(x['workpackets'][0]))
        with self.assertRaisesRegex(ValueError,'duplicate'):mod.compile_intake(x)
    def test_financial_tasks_remain_unsigned(self):
        x=fixture();x['workpackets'][0]['external_effect']='MAINNET_SIGNER_REQUIRED'
        r=mod.compile_intake(x)
        self.assertEqual(r['role_mapped_candidates'][0]['next_existing_flow'],'EXISTING_GOVERNOR_SIGNER_PATH')
        self.assertFalse(r['money_transferred'])
if __name__=='__main__':unittest.main()
