import unittest
from unittest.mock import Mock, patch

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

    def test_chat_answers_supplied_hotel_faq(self):
        cases = (
            (
                "Are you fake or real?",
                "I'm Guled Hotel's virtual assistant, not a human.",
            ),
            (
                "Can I request extra pillows?",
                "Contact reception, and our team will assist you.",
            ),
            (
                "Can I book a room for two people?",
                "Absolutely! We have accommodation options suitable for two guests.",
            ),
        )

        for message, expected_answer in cases:
            with self.subTest(message=message):
                response = self.client.post("/chat", json={"message": message})

                self.assertEqual(response.status_code, 200)
                self.assertIn(expected_answer, response.get_json()["reply"])

    def test_chat_does_not_expose_unconfigured_faq_placeholders(self):
        response = self.client.post("/chat", json={"message": "What time is check-in?"})
        reply = response.get_json()["reply"]

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("[Check-in Time]", reply)
        self.assertIn("0792194284", reply)

    @patch("app.psycopg.connect")
    @patch("app.get_database_url", return_value="postgresql://neon/db")
    def test_order_is_saved_with_consent(self, get_database_url, connect):
        connection = connect.return_value.__enter__.return_value
        cursor = connection.cursor.return_value.__enter__.return_value
        payload = {
            "customer_name": "Amina Hassan",
            "phone": "0792194284",
            "email": "amina@example.com",
            "order_details": "One-bedroom stay",
            "consent": True,
        }

        response = self.client.post("/api/orders", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {"status": "saved"})
        connect.assert_called_once_with("postgresql://neon/db", connect_timeout=5)
        self.assertIn("INSERT INTO public.hotel_orders", cursor.execute.call_args.args[0])
        self.assertEqual(cursor.execute.call_args.args[1], (
            "Amina Hassan",
            "0792194284",
            "amina@example.com",
            "One-bedroom stay",
            True,
        ))

    @patch("app.get_database_url", return_value=None)
    def test_order_reports_missing_database_config(self, get_database_url):
        response = self.client.post("/api/orders", json={
            "customer_name": "Amina Hassan",
            "phone": "0792194284",
            "email": "amina@example.com",
            "order_details": "One-bedroom stay",
            "consent": True,
        })

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json(), {"error": "Order storage is not configured."})

    def test_order_requires_explicit_consent(self):
        response = self.client.post("/api/orders", json={
            "customer_name": "Amina Hassan",
            "phone": "0792194284",
            "email": "amina@example.com",
            "order_details": "One-bedroom stay",
            "consent": False,
        })

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()