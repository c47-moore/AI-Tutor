
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']]  // Allows inline LaTeX using $...$
  },
  svg: {
    fontCache: 'global'
  }
};


async function sendMessage() {
    let messageInput = document.getElementById("message");
    let message = messageInput.value.trim();
    if (message === "") return;

    // Display sent message
    displayMessage(message, "sent");

    // Show loading indicator
    let loadingIndicator = displayLoadingIndicator();

    // Create a placeholder for the streamed response
    let chatBox = document.getElementById("chatBox");
    let messageDiv = document.createElement("div");
    messageDiv.style.display = "none";
    messageDiv.classList.add("message", "received");
    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        let response = await fetch("/cgi-bin/process.py", {
            method: "POST",
            body: new URLSearchParams({ message }),
            headers: { "Content-Type": "application/x-www-form-urlencoded" }
        });

        if (!response.body) throw new Error("No response body received");

        // Remove loading indicator before displaying response
        removeLoadingIndicator(loadingIndicator);
        messageDiv.style.display = "block";

        // Process streaming response
        let reader = response.body.getReader();
        let decoder = new TextDecoder();
        let accumulatedText = "";

        while (true) {
            let { done, value } = await reader.read();
            if (done) break;

            // Decode and append the new chunk
            let chunk = decoder.decode(value, { stream: true });
            accumulatedText += chunk;
            messageDiv.innerHTML = accumulatedText;

            // Ensure MathJax processes LaTeX dynamically
            if (window.MathJax) {
                MathJax.typesetPromise([messageDiv]).then(() => {
                    // Step 2: Convert Markdown after LaTeX is processed
                    messageDiv.innerHTML = marked.parse(messageDiv.innerHTML);
                    chatBox.scrollTop = chatBox.scrollHeight;  // Auto-scroll
                }).catch(err => console.error('MathJax rendering error:', err));
            } else {
                // If MathJax is not available, fallback to Markdown only
                messageDiv.innerHTML = marked.parse(text);
            }

            chatBox.scrollTop = chatBox.scrollHeight;  // Auto-scroll
        }
    } catch (error) {
        messageDiv.innerHTML = "Error: " + error.message;
    }

    // Clear input
    messageInput.value = "";
    messageInput.focus();
}

function displayMessage(text, type) {
    let chatBox = document.getElementById("chatBox");
    let messageDiv = document.createElement("div");
    messageDiv.classList.add("message", type);

    // Insert raw text first
    messageDiv.innerHTML = text;
    chatBox.appendChild(messageDiv);

    // Step 1: Render LaTeX first
    if (window.MathJax) {
        MathJax.typesetPromise([messageDiv]).then(() => {
            // Step 2: Convert Markdown after LaTeX is processed
            messageDiv.innerHTML = marked.parse(messageDiv.innerHTML);
            chatBox.scrollTop = chatBox.scrollHeight;  // Auto-scroll
        }).catch(err => console.error('MathJax rendering error:', err));
    } else {
        // If MathJax is not available, fallback to Markdown only
        messageDiv.innerHTML = marked.parse(text);
    }
}


function displayLoadingIndicator() {
    let chatBox = document.getElementById("chatBox");
    let loadingDiv = document.createElement("div");
    loadingDiv.classList.add("message", "loading");

    let dot1 = document.createElement("span");
    let dot2 = document.createElement("span");
    let dot3 = document.createElement("span");
    dot1.classList.add("dots");
    dot2.classList.add("dots");
    dot3.classList.add("dots");

    loadingDiv.appendChild(dot1);
    loadingDiv.appendChild(dot2);
    loadingDiv.appendChild(dot3);
    chatBox.appendChild(loadingDiv);

    // Auto-scroll to latest message
    chatBox.scrollTop = chatBox.scrollHeight;

    return loadingDiv;
}

function removeLoadingIndicator(loadingDiv) {
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}
