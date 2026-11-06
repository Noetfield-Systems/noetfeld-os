import unittest
from core import route_for, score, AGENTS

class BusinessOSRoutingTests(unittest.TestCase):
    def test_brand_specific_routes(self):
        self.assertEqual(route_for("buildworkflow","operator","buildworkflow")[0],"trade_operations")
        self.assertEqual(route_for("trustfield","enterprise","trustfield")[0],"regulated_enterprise")
        self.assertEqual(route_for("buildrelay","investor","investment")[0],"capital_partner")
    def test_urgency_increases_fit_score(self):
        low=score("operator","automation","exploring",10000,"Improve operations and workflow")
        high=score("operator","automation","now",10000,"Improve operations and workflow")
        self.assertGreater(high,low)
    def test_agent_roles_are_unique(self):
        roles=[a[0] for a in AGENTS]
        self.assertEqual(len(roles),len(set(roles)))
        self.assertIn("roi_analyst",roles)
        self.assertIn("risk_governance",roles)

if __name__=="__main__": unittest.main()
