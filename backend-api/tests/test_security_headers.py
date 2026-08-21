import unittest

from fastapi.testclient import TestClient

from app.main import app


EXPECTED_HEADERS = {
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "content-security-policy": "frame-ancestors 'none'",
    "referrer-policy": "no-referrer",
    "permissions-policy": "camera=(), microphone=(), geolocation=()",
}


class TestSecurityHeaders(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    def check_security_headers(self, response):
        for header_name, expected_value in EXPECTED_HEADERS.items():
            self.assertEqual(
                response.headers.get(header_name),
                expected_value,
                f"Missing or incorrect header: {header_name}",
            )

    def test_security_headers_on_success_response(self):
        response = self.client.get("/liveness")

        self.assertEqual(response.status_code, 200)
        self.check_security_headers(response)

    def test_security_headers_on_not_found_response(self):
        response = self.client.get("/does-not-exist")

        self.assertEqual(response.status_code, 404)
        self.check_security_headers(response)


if __name__ == "__main__":
    unittest.main()
