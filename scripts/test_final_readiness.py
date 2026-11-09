"""Readiness must not turn missing evidence or placeholder approvals green."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from final_readiness import advanced_fresh, owner_results, OWNER_GATES


class ReadinessTests(unittest.TestCase):
    def test_no_owner_approval_is_implied(self):
        self.assertFalse(any(row['complete'] for row in owner_results({}).values()))
        self.assertFalse(any(row['complete'] for row in owner_results({key:'true' for key in OWNER_GATES}).values()))

    def test_stale_source_cannot_pass_freshness(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); source=root/'backend/app/understanding/runtime.py'
            source.parent.mkdir(parents=True);source.write_bytes(b'original\n')
            report={'service_sha256':{'runtime.py':hashlib.sha256(b'original\n').hexdigest()}}
            self.assertTrue(advanced_fresh(report,root))
            source.write_bytes(b'changed\n')
            self.assertFalse(advanced_fresh(report,root))
            self.assertFalse(advanced_fresh({'service_sha256':{}},root))


if __name__=='__main__':unittest.main()
