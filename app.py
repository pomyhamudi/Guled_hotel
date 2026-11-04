
import os
import re
from difflib import SequenceMatcher
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

load_dotenv()

app = Flask(__name__)

FRONT_DESK_PHONE = "0792194284"
FRONT_DESK_EMAIL = "guledmohamud099@gmail.com"
FAQ_PATH = Path(__file__).with_name("hotel_faq.md")
FAQ_QUESTION_PATTERN = re.compile(
    r"^\*\*Q\d+:\s*(.*?)\*\*\s*\r?\nA:\s*(.*?)(?=^\*\*Q\d+:|^---$|^# END|\Z)",
    re.MULTILINE | re.DOTALL,
)
FAQ_STOP_WORDS = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "is",
    "it", "me", "my", "of", "our", "the", "to", "we", "what", "when",
    "where", "which", "who", "you", "your",
}


def load_hotel_faq():
    content = FAQ_PATH.read_text(encoding="utf-8")
    entries = [
        (question.strip(), answer.strip())
        for question, answer in FAQ_QUESTION_PATTERN.findall(content)
    ]
    if not entries:
        raise ValueError(f"No questions were found in the hotel FAQ: {FAQ_PATH}")
    return entries


HOTEL_FAQ = load_hotel_faq()


def answer_from_faq(message, exact_only=False):
    def keywords(value):
        words = re.findall(r"[a-z0-9]+", value.lower())
        return " ".join(word for word in words if word not in FAQ_STOP_WORDS)

    message_keywords = keywords(message)
    if not message_keywords:
        return None

    best_match = None
    best_score = 0.0
    message_words = set(message_keywords.split())
    for question, answer in HOTEL_FAQ:
        question_keywords = keywords(question)
        if not question_keywords:
            continue

        question_words = set(question_keywords.split())
        overlap = len(message_words & question_words)
        token_score = (
            2 * overlap / (len(message_words) + len(question_words))
            if overlap
            else 0.0
        )
        sequence_score = SequenceMatcher(
            None, message_keywords, question_keywords
        ).ratio()
        score = max(token_score, sequence_score)
        if score > best_score:
            best_match = answer
            best_score = score

    if best_score < 0.6 or best_match is None:
        return None

    if exact_only and best_score < 1:
        return None

    answer = best_match.replace("[Hotel Name]", "Guled Hotel")
    if re.search(r"\[[^]]+\]", answer):
        if exact_only:
            return None
        return "I don't have confirmed details for that yet. " + contact_front_desk()
    return answer


def contact_front_desk():
    return (
        f"Please call our front desk at {FRONT_DESK_PHONE} or email "
        f"{FRONT_DESK_EMAIL} for assistance."
    )


def get_database_url():
    return os.getenv("DATABASE_URL")


def hotel_chatbot(message):
    """Generate a helpful response to a hotel question."""

    text = message.lower().strip()

    if not text:
        return "What would you like to know?"

    if "fake" in text and "real" in text:
        return (
            "I'm Guled Hotel's virtual assistant, not a human. I can help with "
            "hotel information. For a person, " + contact_front_desk()
        )

    exact_faq_reply = answer_from_faq(text, exact_only=True)
    if exact_faq_reply is not None:
        return exact_faq_reply

    first_word = text.split(maxsplit=1)[0].strip(".,!?") if text else ""
    if first_word in {"hello", "hi", "hey"}:
        return "Hi! Welcome to Guled. How can I help?"

    if any(word in text for word in ["thanks", "thank you", "thx"]):
        return "You're welcome!"

    if any(word in text for word in ["hours", "opening", "open", "closing", "close"]) and any(
        word in text for word in ["restaurant", "dining", "food", "breakfast", "dinner"]
    ):
        return "I'm not sure about our restaurant hours. " + contact_front_desk()

    if any(word in text for word in ["book", "reservation", "reserve"]):
        return (
            "Certainly! I'd be happy to help you get in touch about a booking. "
            "I can't confirm availability or complete reservations in this chat. "
            f"Please contact us at {FRONT_DESK_PHONE} or {FRONT_DESK_EMAIL}."
        )

    if any(
        word in text
        for word in [
            "menu", "restaurant", "food", "dining", "tea", "coffee",
            "chapati", "signature meal",
        ]
    ):
        return (
            "Certainly! Here's our food and drinks menu:\n"
            "Food:\n"
            "- Chapati: KSH 500\n"
            "- Signature meals: KSH 5,000-20,000\n"
            "Drinks:\n"
            "- Tea: KSH 250\n"
            "- Coffee: KSH 350\n"
            f"For ordering, please contact us at {FRONT_DESK_PHONE} or "
            f"{FRONT_DESK_EMAIL}."
        )

    if any(word in text for word in ["one bedroom", "one bed room", "1 bedroom", "single bedroom"]):
        return "Certainly! A one-bedroom room is KSH 15,000 per night."

    if any(word in text for word in ["two bedrooms", "two bed rooms", "two bed room", "2 bedrooms", "two bedroom"]):
        return "Certainly! A two-bedroom room is KSH 20,000 per night."

    if any(word in text for word in ["price", "cost", "how much"]):
        return (
            "Certainly! A one-bedroom room is KSH 15,000 per night, and a "
            "two-bedroom room is KSH 20,000 per night. Which would you prefer?"
        )

    if any(word in text for word in ["availability", "available", "vacancy", "vacancies"]):
        return (
            "I'm unable to confirm room availability in this chat. "
            + contact_front_desk()
        )

    faq_reply = answer_from_faq(text)
    if faq_reply is not None:
        return faq_reply

    if any(
        word in text
        for word in [
            "amenity", "amenities", "facility", "facilities", "wi-fi", "wifi",
            "breakfast", "parking", "pool", "gym", "check-in", "check in",
            "checkout", "check-out", "cancellation", "pet policy", "restaurant hours",
            "opening hours",
        ]
    ):
        return "I'm not sure about that detail. " + contact_front_desk()

    if any(word in text for word in ["room", "bedroom", "suite"]):
        return (
            "Our listed options are a one-bedroom room at KSH 15,000 per night "
            "and a two-bedroom room at KSH 20,000 per night. "
            "Please contact us to ask about descriptions or amenities."
        )

    if any(word in text for word in ["help", "services", "what can you do"]):
        return (
            "I'd be happy to help with room prices and our food and drinks menu. "
            "For availability, bookings, amenities, or other details, "
            + contact_front_desk()
        )

    return (
        "I'm not sure about that. I can help with room prices and our menu. "
        + contact_front_desk()
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.get("/healthz")
def health_check():
    return jsonify({"status": "ok"})


@app.post("/api/orders")
def create_order():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Please submit order details as JSON."}), 400

    customer_name = data.get("customer_name")
    phone = data.get("phone")
    email = data.get("email")
    order_details = data.get("order_details")
    if not all(isinstance(value, str) for value in (customer_name, phone, email, order_details)):
        return jsonify({"error": "Please complete all order fields."}), 400

    customer_name = customer_name.strip()
    phone = phone.strip()
    email = email.strip()
    order_details = order_details.strip()
    if (
        not customer_name
        or len(customer_name) > 120
        or not phone
        or len(phone) > 40
        or "@" not in email
        or len(email) > 254
        or not order_details
        or len(order_details) > 5000
        or data.get("consent") is not True
    ):
        return jsonify({"error": "Please check your details and consent, then try again."}), 400

    try:
        database_url = get_database_url()
        if not database_url:
            return jsonify({"error": "Order storage is not configured."}), 503

        with psycopg.connect(database_url, connect_timeout=5) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO public.hotel_orders
                        (customer_name, phone, email, order_details, consent_received)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (customer_name, phone, email, order_details, True),
                )
    except Exception as error:
        app.logger.warning("Neon order save failed (%s)", type(error).__name__)
        return jsonify({"error": "We could not save your order. Please try again."}), 503

    return jsonify({"status": "saved"}), 201


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"reply": "Please send a JSON object containing a text question."}), 400

    message = data.get("message", "")

    if not isinstance(message, str):
        return jsonify({"reply": "Please send a text question."}), 400

    reply = hotel_chatbot(message)

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5003")), debug=False)
