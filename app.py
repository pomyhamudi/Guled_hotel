
import os

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

FRONT_DESK_PHONE = "0792194284"
FRONT_DESK_EMAIL = "guledmohamud099@gmail.com"


def contact_front_desk():
    return (
        f"Please call our front desk at {FRONT_DESK_PHONE} or email "
        f"{FRONT_DESK_EMAIL} for assistance."
    )


def hotel_chatbot(message):
    """Generate a helpful response to a hotel question."""

    text = message.lower().strip()

    if not text:
        return "What would you like to know?"

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

    if any(word in text for word in ["menu", "restaurant", "food", "dining"]):
        return (
            "Certainly! Here's our food and drinks menu:\n"
            "Food:\n"
            "- Chapati: KSH 50\n"
            "- Other food items: KSH 450-1,500\n"
            "Drinks:\n"
            "- Tea: KSH 100\n"
            "- Coffee varieties: KSH 150-400\n"
            f"For ordering, please contact us at {FRONT_DESK_PHONE} or "
            f"{FRONT_DESK_EMAIL}."
        )

    if any(word in text for word in ["one bedroom", "one bed room", "1 bedroom", "single bedroom"]):
        return "Certainly! A one-bedroom room is KSH 10,000 per night."

    if any(word in text for word in ["two bedrooms", "two bed rooms", "two bed room", "2 bedrooms", "two bedroom"]):
        return "Certainly! A two-bedroom room is KSH 15,000 per night."

    if any(word in text for word in ["price", "cost", "how much"]):
        return (
            "Certainly! A one-bedroom room is KSH 10,000 per night, and a "
            "two-bedroom room is KSH 15,000 per night. Which would you prefer?"
        )

    if any(word in text for word in ["availability", "available", "vacancy", "vacancies"]):
        return (
            "I'm unable to confirm room availability in this chat. "
            + contact_front_desk()
        )

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
            "Our listed options are a one-bedroom room at KSH 10,000 per night "
            "and a two-bedroom room at KSH 15,000 per night. "
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
