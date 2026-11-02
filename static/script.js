
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const chatMessages = document.getElementById("chat-messages");
const sendButton = document.getElementById("send-button");
const chatPanel = document.getElementById("concierge-panel");
const chatFloatToggle = document.getElementById("chat-float-toggle");
const chatClose = document.getElementById("chat-close");

function setChatOpen(isOpen) {
    chatPanel.classList.toggle("is-open", isOpen);
    chatPanel.setAttribute("aria-hidden", String(!isOpen));
    chatFloatToggle.setAttribute("aria-expanded", String(isOpen));
    chatFloatToggle.classList.toggle("is-hidden", isOpen);

    if (isOpen) {
        messageInput.focus();
    } else {
        chatFloatToggle.focus();
    }
}

chatFloatToggle.addEventListener("click", () => setChatOpen(true));
chatClose.addEventListener("click", () => setChatOpen(false));

function createContactIcon(type) {
    const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    icon.setAttribute("viewBox", "0 0 20 20");
    icon.setAttribute("fill", "none");
    icon.setAttribute("aria-hidden", "true");

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("stroke", "currentColor");
    path.setAttribute("stroke-width", "1.5");
    path.setAttribute("stroke-linecap", "round");
    path.setAttribute("stroke-linejoin", "round");
    path.setAttribute(
        "d",
        type === "email"
            ? "M3 5.5h14v9H3z M3.5 6l6.5 5 6.5-5"
            : "M10 2.8a7.1 7.1 0 0 0-6.1 10.7L3 17l3.6-.9A7.1 7.1 0 1 0 10 2.8Zm0 1.4a5.7 5.7 0 1 1-2.9 10.6l-.3-.2-1.7.4.4-1.7-.2-.3A5.7 5.7 0 0 1 10 4.2Zm-2.1 2c-.2 0-.4.1-.6.3-.2.2-.7.7-.7 1.6s.7 1.9.8 2c.1.1 1.4 2.2 3.4 3 .4.2.8.3 1.1.3.5.1.9 0 1.2-.1.4-.2.7-.7.8-1 .1-.3.1-.6 0-.7-.1-.1-.2-.2-.4-.3l-1.2-.6c-.2-.1-.3-.1-.5.1l-.5.6c-.1.2-.3.2-.5.1-.2-.1-.9-.3-1.6-1-.6-.5-1-1.2-1.1-1.4-.1-.2 0-.3.1-.4l.3-.4c.1-.1.2-.2.2-.4.1-.1 0-.3 0-.4l-.5-1.2c-.1-.3-.3-.3-.5-.3Z"
    );
    icon.appendChild(path);
    return icon;
}

function addMessage(sender, message) {
    const bubble = document.createElement("div");
    bubble.className = `message ${sender}`;

    const label = document.createElement("strong");
    label.className = "message-time";
    label.textContent = sender === "user" ? "YOU · JUST NOW" : "CONCIERGE · JUST NOW";

    const paragraph = document.createElement("p");
    const contactPattern = /([\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?:\+?\d[\d ()-]{7,}\d))/g;
    let lastIndex = 0;
    for (const match of message.matchAll(contactPattern)) {
        paragraph.appendChild(
            document.createTextNode(message.slice(lastIndex, match.index))
        );

        const contact = match[0];
        const isEmail = contact.includes("@");
        const link = document.createElement("a");
        link.className = "contact-link";
        link.appendChild(createContactIcon(isEmail ? "email" : "whatsapp"));

        const contactText = document.createElement("span");
        contactText.textContent = contact;
        link.appendChild(contactText);

        if (isEmail) {
            link.href = `mailto:${contact}?subject=Message%20for%20Guled`;
            link.setAttribute("aria-label", `Email Guled at ${contact}`);
        } else {
            const internationalNumber = contact.replace(/\D/g, "").replace(/^0/, "254");
            link.href = `https://wa.me/${internationalNumber}`;
            link.target = "_blank";
            link.rel = "noopener noreferrer";
            link.setAttribute("aria-label", `Message Guled on WhatsApp at ${contact}`);
        }
        paragraph.appendChild(link);
        lastIndex = match.index + contact.length;
    }
    paragraph.appendChild(document.createTextNode(message.slice(lastIndex)));

    bubble.append(label, paragraph);
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage(message) {
    const question = message.trim();

    if (!question) return;

    addMessage("user", question);
    messageInput.value = "";
    sendButton.disabled = true;
    sendButton.querySelector("span").textContent = "Sending";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: question })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.reply || "The request failed.");
        }

        addMessage("bot", data.reply);
    } catch (error) {
        addMessage(
            "bot",
            "Sorry, I could not connect to the hotel server. " +
            "Please check that the Python application is running, " +
            "then try again."
        );
        console.error(error);
    } finally {
        sendButton.disabled = false;
        sendButton.querySelector("span").textContent = "Send";
        messageInput.focus();
    }
}

chatForm.addEventListener("submit", function (event) {
    event.preventDefault();
    sendMessage(messageInput.value);
});

document.querySelectorAll("[data-message]").forEach(button => {
    button.addEventListener("click", function () {
        sendMessage(button.dataset.message);
    });
});

const orderForm = document.getElementById("order-form");
const orderStatus = document.getElementById("order-status");
const orderWhatsappFallback = document.getElementById("order-whatsapp-fallback");
const orderItems = document.getElementById("order-items");
const orderEmpty = document.getElementById("order-empty");
const orderCount = document.getElementById("order-count");
const orderDetails = document.getElementById("order-details");
const selectedOrderItems = new Map();

function syncOrderDetails() {
    if (!orderDetails || orderDetails.dataset.generated !== "true") return;

    orderDetails.value = Array.from(selectedOrderItems.values())
        .map(item => `${item.quantity} × ${item.name} (${item.price})`)
        .join("\n");
}

function renderOrder() {
    const items = Array.from(selectedOrderItems.values());
    const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);

    orderItems.replaceChildren();
    orderEmpty.hidden = items.length > 0;
    orderCount.textContent = `${itemCount} ${itemCount === 1 ? "item" : "items"}`;

    items.forEach(item => {
        const row = document.createElement("div");
        row.className = "order-line";

        const details = document.createElement("div");
        details.className = "order-line-details";
        const name = document.createElement("strong");
        name.textContent = item.name;
        const price = document.createElement("span");
        price.textContent = item.price;
        details.append(name, price);

        const controls = document.createElement("div");
        controls.className = "order-line-controls";
        controls.innerHTML = `
            <button type="button" aria-label="Decrease ${item.name} quantity"
                    data-order-action="decrease" data-order-key="${item.name}">−</button>
            <span>${item.quantity}</span>
            <button type="button" aria-label="Increase ${item.name} quantity"
                    data-order-action="increase" data-order-key="${item.name}">+</button>
            <button class="order-remove" type="button" aria-label="Remove ${item.name}"
                    data-order-action="remove" data-order-key="${item.name}">Remove</button>`;

        row.append(details, controls);
        orderItems.appendChild(row);
    });

    syncOrderDetails();
}

document.querySelectorAll(".drink-card").forEach(card => {
    const caption = card.querySelector("figcaption");
    if (!caption) return;

    const itemName = caption.textContent.trim();
    const priceByName = {
        "Tropical moments": "KSH 800",
        "An evening pour": "KSH 1,500",
        "Celebrate simply": "KSH 2,000",
        "Bright & refreshing": "KSH 600",
        "A colourful selection": "KSH 1,000",
        "Made for slow afternoons": "KSH 900",
        "Freshly poured tea": "KSH 250",
        "A familiar favourite": "KSH 250",
        "Made for slow mornings": "KSH 350"
    };
    const price = priceByName[itemName] || "KSH 500";

    const addButton = document.createElement("button");
    addButton.className = "gallery-add";
    addButton.type = "button";
    addButton.textContent = `Add · ${price}`;
    addButton.dataset.orderName = itemName;
    addButton.dataset.orderPrice = price;
    addButton.setAttribute("aria-label", `Add ${itemName}, ${price}, to my order`);
    card.appendChild(addButton);
});

document.querySelectorAll("[data-order-name]").forEach(button => {
    button.addEventListener("click", () => {
        const name = button.dataset.orderName;
        const current = selectedOrderItems.get(name);
        selectedOrderItems.set(name, {
            name,
            price: button.dataset.orderPrice,
            quantity: current ? current.quantity + 1 : 1
        });
        orderDetails.dataset.generated = "true";
        renderOrder();
        document.getElementById("order").scrollIntoView({ behavior: "smooth", block: "start" });
    });
});

orderItems.addEventListener("click", event => {
    const button = event.target.closest("[data-order-action]");
    if (!button) return;

    const key = button.dataset.orderKey;
    const item = selectedOrderItems.get(key);
    if (!item) return;

    if (button.dataset.orderAction === "increase") item.quantity += 1;
    if (button.dataset.orderAction === "decrease") item.quantity -= 1;
    if (button.dataset.orderAction === "remove" || item.quantity < 1) {
        selectedOrderItems.delete(key);
    }

    orderDetails.dataset.generated = "true";
    renderOrder();
});

orderDetails.addEventListener("input", () => {
    orderDetails.dataset.generated = "false";
});

orderForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    if (!orderForm.reportValidity()) return;

    const formData = new FormData(orderForm);
    const orderMessage = [
        "Hello Guled, I would like to place an order.",
        "",
        `Name: ${formData.get("name")}`,
        `Phone: ${formData.get("phone")}`,
        `Email: ${formData.get("email")}`,
        "",
        "Order details:",
        formData.get("order")
    ].join("\n");
    const whatsappUrl = new URL("https://wa.me/254792194284");
    whatsappUrl.searchParams.set("text", orderMessage);
    orderWhatsappFallback.href = whatsappUrl.toString();
    orderWhatsappFallback.hidden = true;
    orderStatus.textContent = "Saving your request securely...";
    const submitButton = orderForm.querySelector(".order-submit");
    submitButton.disabled = true;

    try {
        const response = await fetch("/api/orders", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                customer_name: formData.get("name"),
                phone: formData.get("phone"),
                email: formData.get("email"),
                order_details: formData.get("order"),
                consent: formData.get("consent") === "on"
            })
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || "Order save failed.");

        orderWhatsappFallback.hidden = false;
        orderStatus.textContent =
            "Your request is saved. Open the WhatsApp draft to review it and tap Send.";
        window.open(whatsappUrl.toString(), "_blank", "noopener,noreferrer");
    } catch (error) {
        orderWhatsappFallback.hidden = false;
        orderStatus.textContent =
            "We could not save your request. You can still contact us using the WhatsApp draft below.";
        console.error(error);
    } finally {
        submitButton.disabled = false;
    }
});
