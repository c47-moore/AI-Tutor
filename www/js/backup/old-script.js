
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']]  // Allows inline LaTeX using $...$
  },
  svg: {
    fontCache: 'global'
  }
};


function sendMessage() {
    let messageInput = document.getElementById("message");
    let message = messageInput.value.trim();
    if (message === "") return;

    // Display sent message
    displayMessage(message, "sent");

    // Show loading indicator
    let loadingIndicator = displayLoadingIndicator();

    // AJAX request to send message
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/cgi-bin/process.py", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            // Remove loading indicator
            removeLoadingIndicator(loadingIndicator);

            if (xhr.status === 200) {
                displayMessage(xhr.responseText, "received");
            } else {
                displayMessage("Error: Failed to get response.", "received");
            }
        }
    };

    xhr.send("message=" + encodeURIComponent(message));

    // Clear input
    messageInput.value = "";
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
