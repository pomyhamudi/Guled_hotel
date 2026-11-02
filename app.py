
import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

load_dotenv()

app = Flask(__name__)

FRONT_DESK_PHONE = "0792194284"
FRONT_DESK_EMAIL = "guledmohamud099@gmail.com"


def contact_front_desk():
    return (
        f"Please call our front desk at {FRONT_DESK_PHONE} or email "
        f"{FRONT_DESK_EMAIL} for assistance."
    )


def get_supabase_client():
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_role_key:
        return None

    from supabase import create_client

    return create_client(supabase_url, service_role_key)


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
        supabase = get_supabase_client()
        if supabase is None:
            return jsonify({"error": "Order storage is not configured."}), 503

        supabase.table("hotel_orders").insert({
            "customer_name": customer_name,
            "phone": phone,
            "email": email,
            "order_details": order_details,
            "consent_received": True,
        }).execute()
    except Exception as error:
        app.logger.warning("Supabase order save failed (%s)", type(error).__name__)
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
