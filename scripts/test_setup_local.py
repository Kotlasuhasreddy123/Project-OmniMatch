"""Setup checks use an isolated directory and mocked Docker; never change real settings."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import setup_local


class SetupTests(unittest.TestCase):
    def test_creates_distinct_secrets_and_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "backend").mkdir()
            (root / "backend/.env.example").write_text("APP_SECRET_KEY=change-me-to-a-random-256-bit-secret\nJWT_SECRET_KEY=change-me-to-another-random-256-bit-secret\n")
            with patch.object(setup_local, "ROOT", root), patch.object(sys, "argv", ["setup_local.py"]), patch.object(setup_local.shutil, "which", return_value="docker"), patch.object(setup_local.subprocess, "run", return_value=Mock(returncode=0)), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(setup_local.main(), 0)
                saved = (root / "backend/.env").read_text()
                values = [line.split("=", 1)[1] for line in saved.splitlines()]
                self.assertEqual(len(set(values)), 2)
                self.assertTrue(all(len(value) == 64 for value in values))
                self.assertEqual(setup_local.main(), 0)
                self.assertEqual((root / "backend/.env").read_text(), saved)

    def test_stops_without_docker_and_does_not_create_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(setup_local, "ROOT", root), patch.object(sys, "argv", ["setup_local.py"]), patch.object(setup_local.shutil, "which", return_value=None), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(setup_local.main(), 1)
                self.assertFalse((root / "backend/.env").exists())


class StoragePreflightTests(unittest.TestCase):
    def test_low_space_stops_before_any_docker_command(self):
        for arguments in [['setup_local.py', '--start'], ['setup_local.py', '--start', '--advanced']]:
            with self.subTest(arguments=arguments), patch('sys.argv', arguments), \
                 patch.object(setup_local.shutil, 'disk_usage', return_value=Mock(free=1024**3)), \
                 patch.object(setup_local.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(setup_local.main(), 1)
                self.assertIn('Free at least', output.getvalue())
                run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
