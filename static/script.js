
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const chatMessages = document.getElementById("chat-messages");
const sendButton = document.getElementById("send-button");

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

orderForm.addEventListener("submit", function (event) {
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
    orderWhatsappFallback.hidden = false;
    window.open(whatsappUrl.toString(), "_blank", "noopener,noreferrer");
    orderStatus.textContent =
        "WhatsApp opened with your draft. Review the details and tap Send to submit your request.";
});
