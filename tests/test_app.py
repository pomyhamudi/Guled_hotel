import unittest

from app import app


class HotelAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_check(self):
        response = self.client.get("/healthz")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_home_and_static_assets(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"GULED", response.data)
        for path in ("/static/style.css", "/static/script.js"):
            with self.subTest(path=path), self.client.get(path) as asset_response:
                self.assertEqual(asset_response.status_code, 200)

    def test_chatroom_prices_match_site(self):
        cases = (
            ("one bedroom", "KSH 15,000"),
            ("two bedroom", "KSH 20,000"),
        )

        for message, expected_price in cases:
            with self.subTest(message=message):
                response = self.client.post("/chat", json={"message": message})
                self.assertEqual(response.status_code, 200)
                self.assertIn(expected_price, response.get_json()["reply"])

    def test_chat_menu_and_item_prices_match_site(self):
        for message in ("show me the menu", "how much is tea?"):
            with self.subTest(message=message):
                response = self.client.post("/chat", json={"message": message})
                reply = response.get_json()["reply"]

                self.assertEqual(response.status_code, 200)
                for expected_price in (
                    "KSH 500", "KSH 250", "KSH 350", "KSH 5,000-20,000"
                ):
                    self.assertIn(expected_price, reply)


if __name__ == "__main__":
    unittest.main()