"""Active Supabase paired-key routing tests; never use real credentials."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from noos_supabase_active_pair_v1 import canonical_env

ACTIVE="https://ldfruywifqnfpwsfgmdl.supabase.co"
OLD="https://tkgpapowwplupyekpivy.supabase.co"
ACTIVE_KEY="active_test_service_role_XXXXXXXXXXXXXXXXXXXXXXXX"
OLD_KEY="old_test_service_role_XXXXXXXXXXXXXXXXXXXXXXXX"


class SupabaseSinglePairTests(unittest.TestCase):
    def test_railway_active_pair_overrides_all_stale_legacy_aliases_together(self):
        effective=canonical_env({
            "NOETFIELD_SUPABASE_URL":OLD,
            "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY":OLD_KEY,
            "SUPABASE_URL":OLD,
            "SUPABASE_SERVICE_ROLE_KEY":OLD_KEY,
            "NOETFIELD_ACTIVE_SUPABASE_URL":ACTIVE,
            "NOETFIELD_ACTIVE_SUPABASE_SERVICE_ROLE_KEY":ACTIVE_KEY,
            "NOOS_RUNTIME_DATABASE_URL":"postgresql://existing-railway",
        })
        self.assertEqual(effective["NOETFIELD_SUPABASE_URL"],ACTIVE)
        self.assertEqual(effective["SUPABASE_URL"],ACTIVE)
        self.assertEqual(effective["NOETFIELD_SUPABASE_SERVICE_ROLE_KEY"],ACTIVE_KEY)
        self.assertEqual(effective["SUPABASE_SERVICE_ROLE_KEY"],ACTIVE_KEY)
        self.assertEqual(effective["NOOS_SUPABASE_SOURCE"],"ACTIVE_PAIR")
        self.assertEqual(effective["NOOS_RUNTIME_DATABASE_URL"],"postgresql://existing-railway")

    def test_single_half_pair_does_not_mix_keys_or_fallback_to_paused_project(self):
        env={"NOETFIELD_SUPABASE_URL":OLD,
             "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY":OLD_KEY,
             "NOETFIELD_ACTIVE_SUPABASE_URL":ACTIVE}
        with self.assertRaisesRegex(RuntimeError,"NOOS_ACTIVE_SUPABASE_PAIR_INCOMPLETE"):
            canonical_env(env)
        self.assertEqual(env["NOETFIELD_SUPABASE_URL"],OLD)

    def test_host_injection_rejected(self):
        for candidate in ("http://ldfruywifqnfpwsfgmdl.supabase.co",
                          ACTIVE+"/rest/v1",
                          ACTIVE+"@example.org",
                          "https://ldfruywifqnfpwsfgmdl.supabase.co.evil.example",
                          ACTIVE+"?token=x"):
            with self.subTest(candidate=candidate):
                with self.assertRaisesRegex(RuntimeError,"NOOS_ACTIVE_SUPABASE_PAIR_INVALID"):
                    canonical_env({"NOETFIELD_ACTIVE_SUPABASE_URL":candidate,
                                   "NOETFIELD_ACTIVE_SUPABASE_SERVICE_ROLE_KEY":ACTIVE_KEY})

    def test_legacy_only_env_is_unchanged_for_other_standalone_jobs(self):
        env={"NOETFIELD_SUPABASE_URL":OLD,"NOETFIELD_SUPABASE_SERVICE_ROLE_KEY":OLD_KEY}
        result=canonical_env(env)
        self.assertEqual(result["NOETFIELD_SUPABASE_URL"],OLD)
        self.assertEqual(result["NOOS_SUPABASE_SOURCE"],"LEGACY_UNCHANGED")
        self.assertNotIn("SUPABASE_SERVICE_ROLE_KEY",result)


if __name__=="__main__":
    unittest.main()
