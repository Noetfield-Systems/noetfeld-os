"""Company OS team brain: actual scoped decisions, no company-wide task tracker."""
import os
import sqlite3
import sys
import unittest
from pathlib import Path
from datetime import datetime,timezone

sys.path.insert(0,str(Path(__file__).resolve().parent))
import brain_pulse

NOW=datetime(2026,11,11,14,0,tzinfo=timezone.utc)

def db():
    x=sqlite3.connect(":memory:");x.row_factory=sqlite3.Row
    x.executescript("""
        CREATE TABLE tasks(
          id TEXT PRIMARY KEY,company_id TEXT,project_id TEXT,
          status TEXT,role TEXT
        );
        INSERT INTO tasks VALUES('task_aaaaaaaaaaaaaaaa','noetfield-systems-inc',
          'earnloop','queued','product_strategy');
        INSERT INTO tasks VALUES('task_bbbbbbbbbbbbbbbb','noetfield-systems-inc',
          'signalforge','drafted','marketing_content');
        INSERT INTO tasks VALUES('task_cccccccccccccccc',NULL,NULL,'queued','unknown');
    """)
    return x

class CompanyBrainTests(unittest.TestCase):
    def test_actual_management_pulse_and_bounded_team_scope(self):
        with db() as d:
            pulse=brain_pulse.capture_cycle(d,
                portfolio={"state":"OBSERVED"},
                mandate={"state":"MANDATES_ONLY_AGENT_FABRIC_OWNS_WORKPACKETS",
                         "venture_mandates_adopted":2,
                         "agent_feedback_pending_retry":1},
                local={"state":"OBSERVED","events_created":1},
                market={"state":"NOT_DUE"},
                clock="2026-11-11T14:00:00Z")
            report=brain_pulse.read(d,clock=datetime(2026,11,11,14,1,tzinfo=timezone.utc))
        self.assertTrue(pulse["recorded"])
        self.assertEqual(pulse["reason_code"],"FOUNDER_FEEDBACK_PENDING_RETRY")
        self.assertEqual(report["summary"]["mandates_adopted_in_pulses"],2)
        self.assertEqual(report["pulses"][0]["active_local_tasks"],1)
        self.assertEqual(report["pulses"][0]["local_drafts"],1)
        self.assertEqual(report["summary"]["recorded_team_actions"],0)
    def test_real_role_action_and_provider_failure_are_explicit(self):
        with db() as d:
            x=brain_pulse.record_specialist(d,
                task={"id":"task_aaaaaaaaaaaaaaaa","company_id":"noetfield-systems-inc",
                      "project_id":"earnloop","role":"product_strategy",
                      "objective":"PRIVATE_INTERNAL_TEXT"},
                goalkeeper={"state":"DEGRADED_NO_TRUSTED_GOALKEEPER_RESPONSE"},
                provider="deterministic",input_tokens=0,output_tokens=0,
                clock="2026-11-11T14:00:00Z")
            data=brain_pulse.read(d,clock=datetime(2026,11,11,14,2,tzinfo=timezone.utc))
        self.assertTrue(x["recorded"])
        a=data["role_actions"][0]
        self.assertEqual(a["reason_code"],"GOALKEEPER_UNAVAILABLE")
        self.assertEqual(a["task_id"],"task_aaaaaaaaaaaaaaaa")
        self.assertEqual(a["role"],"product_strategy")
        self.assertEqual(a["model_tokens"],0)
        self.assertEqual(a["external_action_executed"],0)
        self.assertNotIn("PRIVATE_INTERNAL_TEXT",str(data))
    def test_model_draft_not_a_shipped_product(self):
        with db() as d:
            brain_pulse.record_specialist(d,
                task={"id":"task_aaaaaaaaaaaaaaaa","company_id":"noetfield-systems-inc",
                      "project_id":"earnloop","role":"product_strategy"},
                goalkeeper={"state":"SUCCEEDED","disposition":"PROCEED_IN_LOCAL_COMPANY_OS"},
                provider="sina-deepseek",input_tokens=200,output_tokens=100,
                clock="2026-11-11T14:00:00Z")
            report=brain_pulse.read(d,clock=datetime(2026,11,11,14,1,tzinfo=timezone.utc))
        self.assertEqual(report["summary"]["model_drafts"],1)
        self.assertEqual(report["role_actions"][0]["external_action_executed"],0)
        self.assertEqual(report["role_actions"][0]["next_step"],"FOLLOW_EXISTING_REVIEW_OR_HANDOFF")
    def test_dedup_unchanged_management_heartbeat(self):
        with db() as d:
            args={"portfolio":{"state":"NOT_DUE"},
                  "mandate":{"state":"NOT_DUE"},
                  "local":{"state":"NOT_DUE"},
                  "market":{"state":"NOT_DUE"}}
            a=brain_pulse.capture_cycle(d,**args,clock="2026-11-11T14:00:00Z")
            b=brain_pulse.capture_cycle(d,**args,clock="2026-11-11T14:00:10Z")
            c=brain_pulse.capture_cycle(d,**args,clock="2026-11-11T14:06:00Z")
            report=brain_pulse.read(d,clock=datetime(2026,11,11,14,8,tzinfo=timezone.utc))
        self.assertTrue(a["recorded"])
        self.assertFalse(b["recorded"])
        self.assertTrue(c["recorded"])
        self.assertEqual(report["summary"]["recorded_management_cycles"],2)
    def test_not_due_alternating_with_fabric_owner_is_one_idle_beat(self):
        with db() as d:
            arguments={"portfolio":{"state":"OBSERVED"},
                       "local":{"state":"NOT_DUE"},
                       "market":{"state":"NOT_DUE"}}
            a=brain_pulse.capture_cycle(d,**arguments,
                 mandate={"state":"MANDATES_ONLY_AGENT_FABRIC_OWNS_WORKPACKETS"},
                 clock="2026-11-11T14:00:00Z")
            b=brain_pulse.capture_cycle(d,**arguments,
                 mandate={"state":"NOT_DUE"},
                 clock="2026-11-11T14:00:05Z")
            c=brain_pulse.capture_cycle(d,**arguments,
                 mandate={"state":"MANDATES_ONLY_AGENT_FABRIC_OWNS_WORKPACKETS"},
                 clock="2026-11-11T14:00:10Z")
            result=brain_pulse.read(d,clock=datetime(2026,11,11,14,1,tzinfo=timezone.utc))
        self.assertTrue(a["recorded"])
        self.assertFalse(b["recorded"])
        self.assertFalse(c["recorded"])
        self.assertEqual(result["summary"]["recorded_management_cycles"],1)
    def test_no_fake_backfill(self):
        with db() as d:
            report=brain_pulse.read(d,clock=NOW)
            self.assertEqual(report["pulses"],[])
            self.assertEqual(report["role_actions"],[])
            for hours in (0,49,"48",True):
                with self.assertRaises(ValueError):
                    brain_pulse.read(d,hours=hours,clock=NOW)
if __name__=="__main__":unittest.main()
