"""Testy reprodukovatelného výběru vzorku (scripts/select_sample.py).

Spuštění z kořene repozitáře:
    python3 -m unittest discover -s tests -v
"""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import select_sample  # noqa: E402

HEADER = "candidate_id,name,found_via,found_url,found_date,how,investor_id,note\n"


def write_candidates(rows: list[str]) -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
    handle.write(HEADER + "".join(row + "\n" for row in rows))
    handle.close()
    return Path(handle.name)


def row(cid, name, source, note=""):
    return f"{cid},{name},{source},https://zdroj.example/{cid},2026-10-16,list,,{note}"


class SelectSampleTest(unittest.TestCase):
    def test_one_per_source_skips_excluded_and_is_reproducible(self):
        path = write_candidates([
            row("CAN-0001", "Alfa", "ZDR-09"), row("CAN-0002", "Beta", "ZDR-09"),
            row("CAN-0003", "Gama", "ZDR-10", "mimo pilot: typ podle zdroje"),
            row("CAN-0004", "Delta", "ZDR-10"), row("CAN-0005", "Epsilon", "ZDR-12"),
        ])
        candidates = select_sample.load(path)
        first = select_sample.select(candidates, "seed", 3)
        self.assertEqual(first, select_sample.select(select_sample.load(path), "seed", 3))
        self.assertEqual([stratum for _, stratum in first], ["ZDR-09", "ZDR-10", "ZDR-12"])
        self.assertNotIn("CAN-0003", [c.candidate_id for c, _ in first])
        expected_09 = min(["Alfa", "Beta"], key=lambda name: select_sample.order_key("seed", name))
        self.assertEqual(first[0][0].name, expected_09)

    def test_candidate_from_two_sources_is_selected_once_and_rest_is_filled(self):
        path = write_candidates([
            row("CAN-0001", "Alfa", "ZDR-09"), row("CAN-0001", "Alfa Fund", "ZDR-10"),
            row("CAN-0002", "Beta", "ZDR-09"), row("CAN-0003", "Gama", "ZDR-09"),
        ])
        chosen = select_sample.select(select_sample.load(path), "seed", 3)
        ids = [c.candidate_id for c, _ in chosen]
        self.assertEqual(sorted(ids), ["CAN-0001", "CAN-0002", "CAN-0003"])
        self.assertEqual(len(set(ids)), 3)

    def test_exclusion_on_any_finding_excludes_candidate(self):
        path = write_candidates([
            row("CAN-0001", "Alfa", "ZDR-09"), row("CAN-0001", "Alfa", "ZDR-10", "mimo pilot: sídlo"),
            row("CAN-0002", "Beta", "ZDR-09"),
        ])
        candidates = {c.candidate_id: c for c in select_sample.load(path)}
        self.assertTrue(candidates["CAN-0001"].excluded)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(select_sample.main([str(path), "--seed", "s", "--count", "2"]), 1)
            self.assertEqual(select_sample.main([str(path), "--seed", "s", "--count", "1"]), 0)


if __name__ == "__main__":
    unittest.main()
