"""Installation checks cannot imply successful sign-in or clinical validation."""
import unittest
from unittest.mock import patch
from verify_release import verify


def healthy(url):
    if url.endswith('/health'):
        return 200, b'{"qdrant_connected":true,"whisper_loaded":true}', .1
    if url.endswith('/auth/config'):
        return 200, b'{"configured":true,"api_secret":"must-not-appear"}', .1
    if '/api/v1/' in url:
        return 401, b'', .1
    return 200, b'<html>ok</html>', .1


class VerificationTests(unittest.TestCase):
    def test_healthy_routes_do_not_attest_sign_in_or_accuracy(self):
        with patch('verify_release.request', side_effect=healthy):
            result=verify('http://localhost:3000','http://localhost:8000')
        self.assertTrue(result['passed'])
        self.assertFalse(result['live_sign_in_verified'])
        self.assertFalse(result['microphone_verified'])
        self.assertFalse(result['clinical_accuracy_validated'])
        self.assertNotIn('must-not-appear',str(result))

    def test_open_protected_endpoint_fails_verification(self):
        def vulnerable(url):
            if url.endswith('/api/v1/inbox'):
                return 200,b'{}',.1
            return healthy(url)
        with patch('verify_release.request',side_effect=vulnerable):
            self.assertFalse(verify('http://localhost:3000','http://localhost:8000')['passed'])

    def test_unloaded_model_fails_verification(self):
        def unavailable(url):
            if url.endswith('/health'):
                return 200,b'{"qdrant_connected":true,"whisper_loaded":false}',.1
            return healthy(url)
        with patch('verify_release.request',side_effect=unavailable):
            self.assertFalse(verify('http://localhost:3000','http://localhost:8000')['passed'])


if __name__=='__main__':unittest.main()
