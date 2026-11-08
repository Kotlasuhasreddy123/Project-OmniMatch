"""Installer must stop before Docker when the project drive cannot fit a build."""
import contextlib
import io
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import setup_local


class StoragePreflightTests(unittest.TestCase):
    def test_low_space_stops_before_any_docker_command(self):
        for arguments in [['setup_local.py', '--start'], ['setup_local.py', '--start', '--advanced']]:
            with self.subTest(arguments=arguments), patch('sys.argv', arguments), \
                 patch.object(setup_local.shutil, 'disk_usage', return_value=SimpleNamespace(free=1024**3)), \
                 patch.object(setup_local.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(setup_local.main(), 1)
                self.assertIn('Free at least', output.getvalue())
                run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
