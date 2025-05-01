
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']]  // Allows inline LaTeX using $...$
  },
  svg: {
    fontCache: 'global'
  },
  startup: {
    ready: () => {
      console.log('MathJax is loaded, but not yet initialized');
      MathJax.startup.defaultReady();
      console.log('MathJax is initialized, and the initial typeset is queued');
    }
  }
};

let focusField = null;

function setFocus() {
    if (focusField !== null)
	focusField.focus();
}

function toggleResponseModal() {
    showHide('model-modal');
    showHide('modal-popup');
    setFocus();
}

function focusFirstQuestion() {
    el = document.getElementsByClassName("accordion-item-body");
    if (el.length === 0) {
        modalButton = document.getElementById("modalButton");
	modalButton.onclick = function(){window.location.href = '/index.php';};
	el = document.getElementById('tutorResponse');
	el.innerHTML = '<img src="/images/aitutor.webp" />' +
	    '<em>Congratulations!</em><p>You have passed this test and mastered this topic.</p><p>Click OK to return to your progress dashboard.</p>';
	toggleResponseModal();
	return
    }
    el[0].classList.add("active");
    elId = 'a' + el[0].id.slice(1);
    inputField = document.getElementById(elId);
    inputField.focus();
}

function sendAnswer(qid, chatEl, message, endpoint) {
    let uidInput = document.getElementById("uid");
    let uid = uidInput.value.trim();
    let inputSpan = document.getElementById('i' + qid);
    let inputField = document.getElementById('a' + qid);
    let loadingDiv = document.getElementById('l' + qid);
    let loadingIndicator = createLoadingIndicator();
    let xhr = new XMLHttpRequest();

    loadingIndicator.classList.add("loading");
    inputSpan.style.display = "none";
    loadingDiv.style.display = "block";
    loadingDiv.appendChild(loadingIndicator);
    xhr.open("POST", endpoint, true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            loadingDiv.style.display = "none";
            removeLoadingIndicator(loadingIndicator);

            if (xhr.status === 200) {
		if (xhr.responseText.trimEnd() === "correct") {
		    el = document.getElementById("correctAudio");
		    el.play();
		    el = document.getElementById('b' + qid);
		    parentDiv = el.parentElement;
		    el.remove();
		    document.getElementById('q' + qid).remove();
		    tickSpan = document.createElement("span");
		    tickSpan.classList.add("correct");
		    parentDiv.appendChild(tickSpan);
		    parentDiv.classList.add("tick");
		    focusFirstQuestion();
		} else {
		    el = document.getElementById("incorrectAudio");
		    el.play();
		    el = document.getElementById('b' + qid).firstChild;
		    if (el.nodeType === 1) {
			el.src = "/images/incorrect.webp";
		    }
            	    inputSpan.style.display = "block";
		    focusField = inputField;
		    el = document.getElementById('tutorResponse');
		    el.innerHTML = '<img src="/images/aitutor.webp" />' + xhr.responseText;
		    toggleResponseModal();
		}
            } else {
            	inputSpan.style.display = "block";
                alert("Error " + xhr.status + ": Failed to get response.");
            }
        }
    };

    xhr.send("uid=" + uid + "&message=" + encodeURIComponent(message));
}

// disp - true or false, whether message should be displayed in chat
// chatEl - identity of chat element (e.g. div)
// message - message to send
// endpoint - server-side script to send to
async function sendMessageText(disp, chatEl, message, endpoint) {
    let uidInput = document.getElementById("uid");
    let uid = uidInput.value.trim();

    // Display sent message
    if (disp)
        displayMessage(message, "sent");

    // Show loading indicator
    let loadingIndicator = displayLoadingIndicator();

    // Create a placeholder for the streamed response
    let chatBox = document.getElementById(chatEl);
    let messageDiv = document.createElement("div");
    messageDiv.style.display = "none";
    messageDiv.classList.add("message", "received");
    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        let response = await fetch(endpoint, {
            method: "POST",
            body: new URLSearchParams({ message, uid }),
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
}

async function sendMessage() {
    let messageInput = document.getElementById("message");
    let message = messageInput.value.trim();
    if (message === "") return;

    // Clear input
    messageInput.value = "";
    messageInput.focus();

    sendMessageText(true, 'chatBox', message, "/cgi-bin/aitutor.py");
}

function testAnswer(qnum, qid) {
    let userResponse = document.getElementById('a'+qnum);
    // maintain focus on the text field
    userResponse.focus();
    let message = userResponse.value.trim();
    if (message === "") return;

    message = "q" + qid + ":" + message;

    sendAnswer(qnum, 'testResponse', message, '/cgi-bin/check-answer.py');
}

function displayMessage(text, type) {
    let chatBox = document.getElementById("chatBox");
    let messageDiv = document.createElement("div");
    messageDiv.classList.add("message", type);

    // Insert raw text first
    messageDiv.innerHTML = text;
    chatBox.appendChild(messageDiv);

    // Handle any markdown formatting in the input
    messageDiv.innerHTML = marked.parse(text);
}

function createLoadingIndicator() {
    let loadingDiv = document.createElement("div");

    let dot1 = document.createElement("span");
    let dot2 = document.createElement("span");
    let dot3 = document.createElement("span");
    dot1.classList.add("dots");
    dot2.classList.add("dots");
    dot3.classList.add("dots");

    loadingDiv.appendChild(dot1);
    loadingDiv.appendChild(dot2);
    loadingDiv.appendChild(dot3);

    return loadingDiv;
}

function displayLoadingIndicator() {
    let chatBox = document.getElementById("chatBox");
    let loadingDiv = createLoadingIndicator();
    loadingDiv.classList.add("message", "loading");
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
    if (event.key === "Enter" && !event.shiftKey) {
        sendMessage();
        event.preventDefault();
    }

    return false;
}

function answerKeyPress(event, qnum, qid) {
    if (event.key === "Enter" && !event.shiftKey) {
        testAnswer(qnum, qid);
    }
    
    return false;
}

function hideModal(elId) {
    const el = document.getElementById(elId);
    el.style.display = 'none';
}

function showModal(elId) {
    const el = document.getElementById(elId);
    el.style.display = 'block';
}

function swapLogRegDisplay() {
    regDiv = document.getElementById('reg');
    logDiv = document.getElementById('log');
    if (regDiv.style.display != 'block') {
        regDiv.style.display = 'block';
        logDiv.style.display = 'none';
    } else {
        regDiv.style.display = 'none';
        logDiv.style.display = 'block';
    }

    return false;
}

function showHide(elId) {
   var el = document.getElementById(elId);
   if (el.style.display === "none")
       el.style.display = "block";
   else
       el.style.display = "none";
}

function expandContract(b_el, elId) {
    const el = document.getElementById(elId);
    el.classList.toggle('expanded')
    el.classList.toggle('collapsed')
    if (b_el.innerHTML == "-")
        b_el.innerHTML = "+";
    else
        b_el.innerHTML = "-";
}

function launchTopic(tid) {
    document.cookie = "aitid=" + tid;
    window.location.href = "/tutor.php";
}

function takeTest(tid) {
    document.cookie = "aitid=" + tid;
    window.location.assign("/topic-test.php");
}

function tutorBegin(command) {
    let endpoint = "/cgi-bin/aitutor.py";
    command = "cmd:" + command;
    displayMessage('Please start teaching me this topic!', 'sent');
    sendMessageText(false, 'chatBox', command, endpoint);
}

function tutorContinue(command) {
    let endpoint = "/cgi-bin/aitutor.py";
    command = "cmd:" + command;
    displayMessage('Please continue teaching me this topic!', 'sent');
    sendMessageText(false, 'chatBox', command, endpoint);
}
