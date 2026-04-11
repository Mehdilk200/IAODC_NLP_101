document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const voiceBtn = document.getElementById("voice-btn");
    const audioToggleBtn = document.getElementById("audio-toggle-btn");
    const typingIndicator = document.getElementById("typing-indicator");
    
    // Voice playback state
    let audioEnabled = true;

    // Chat Session Management
    let chatSessions = JSON.parse(localStorage.getItem("cmc_chat_sessions")) || [];
    let currentSessionId = localStorage.getItem("cmc_current_session_id") || null;
    let chatHistory = [];

    // Mobile sidebar toggle
    const mobileMenuBtn = document.getElementById("mobile-menu-btn");
    const appSidebar = document.querySelector(".app-sidebar");

    if (mobileMenuBtn && appSidebar) {
        mobileMenuBtn.addEventListener("click", () => {
            appSidebar.classList.toggle("open");
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener("click", (e) => {
            if (window.innerWidth <= 768 && appSidebar.classList.contains("open") && !mobileMenuBtn.contains(e.target) && !appSidebar.contains(e.target)) {
                appSidebar.classList.remove("open");
            }
        });
    }

    // Load Chat History on Start
    function loadChatHistory() {
        chatBox.innerHTML = ''; // Clear chatbox

        if (chatHistory.length > 0) {
            chatHistory.forEach(msg => {
                renderMessage(msg.sender, msg.text, msg.id, msg.feedback);
            });
        } else {
            // Initial msg
            chatBox.innerHTML = `
                <div class="message bot-message">
                    <div class="avatar"><i class="fas fa-robot"></i></div>
                    <div class="message-content">
                        <p>Bonjour! 👋 Je suis C-BOT, l'assistant intelligent de la CMC Casablanca-Settat. Comment puis-je vous aider aujourd'hui?</p>
                    </div>
                </div>`;
        }
    }

    function initSessions() {
        if (chatSessions.length === 0) {
            createNewSession();
        } else {
            if (!currentSessionId || !chatSessions.find(s => s.id === currentSessionId)) {
                currentSessionId = chatSessions[0].id; // Load most recent
            }
            const session = chatSessions.find(s => s.id === currentSessionId);
            chatHistory = session.messages || [];
            localStorage.setItem("cmc_current_session_id", currentSessionId);
            loadChatHistory();
            renderHistorySidebar();
        }
    }

    function createNewSession() {
        currentSessionId = 'session_' + Date.now();
        chatHistory = [];
        const newSession = {
            id: currentSessionId,
            title: "Nouvelle discussion",
            date: new Date().toISOString(),
            messages: []
        };
        chatSessions.unshift(newSession); // Add to beginning
        localStorage.setItem("cmc_current_session_id", currentSessionId);
        saveSessions();
        loadChatHistory();
        renderHistorySidebar();
    }

    function saveSessions() {
        const sessionIndex = chatSessions.findIndex(s => s.id === currentSessionId);
        if (sessionIndex !== -1) {
            chatSessions[sessionIndex].messages = chatHistory;
            
            // Auto-generate title from first user message
            if (chatHistory.length > 0 && chatSessions[sessionIndex].title === "Nouvelle discussion") {
                const firstUserMsg = chatHistory.find(m => m.sender === 'user');
                if (firstUserMsg) {
                    let title = firstUserMsg.text.substring(0, 25);
                    if (firstUserMsg.text.length > 25) title += "...";
                    chatSessions[sessionIndex].title = title;
                }
            }
        }
        localStorage.setItem("cmc_chat_sessions", JSON.stringify(chatSessions));
        renderHistorySidebar();
    }

    function renderHistorySidebar() {
        const historyList = document.getElementById("chat-history-list");
        if (!historyList) return;
        
        historyList.innerHTML = '';
        chatSessions.forEach(session => {
            const btnWrapper = document.createElement("div");
            btnWrapper.className = `qr-btn ${session.id === currentSessionId ? 'active' : ''}`;
            btnWrapper.style.display = 'flex';
            btnWrapper.style.alignItems = 'center';
            btnWrapper.style.width = '100%';
            btnWrapper.style.padding = '0.4rem 0.6rem';
            btnWrapper.style.borderRadius = '8px';
            btnWrapper.style.border = 'none';
            btnWrapper.style.background = session.id === currentSessionId ? 'rgba(0,123,255,0.1)' : 'transparent';
            btnWrapper.style.cursor = 'pointer';
            
            // Format Date (Day/Month H:M)
            const dateObj = new Date(session.date);
            const formattedDate = `${dateObj.getDate()}/${dateObj.getMonth()+1} ${dateObj.getHours()}:${dateObj.getMinutes().toString().padStart(2, '0')}`;

            // Left side (Text content) clickable to switch chat
            const contentDiv = document.createElement("div");
            contentDiv.style.flex = "1";
            contentDiv.style.overflow = "hidden";
            contentDiv.style.textAlign = "left";
            contentDiv.style.color = session.id === currentSessionId ? 'var(--primary)' : 'var(--text-mid)';
            contentDiv.innerHTML = `
                <div style="font-weight: 600; font-size: 0.85rem; width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${session.title}</div>
                <div style="font-size: 0.7rem; color: var(--text-light); margin-top: 0.2rem;">${formattedDate}</div>
            `;
            
            contentDiv.addEventListener('click', () => {
                currentSessionId = session.id;
                chatHistory = session.messages;
                localStorage.setItem("cmc_current_session_id", currentSessionId);
                loadChatHistory();
                renderHistorySidebar();
                
                // Close sidebar on mobile after selecting
                if (window.innerWidth <= 768 && appSidebar) {
                    appSidebar.classList.remove("open");
                }
            });
            
            // Right side (Delete button)
            const deleteBtn = document.createElement("button");
            deleteBtn.className = "icon-btn-sm";
            deleteBtn.style.color = "var(--text-light)";
            deleteBtn.style.background = "transparent";
            deleteBtn.style.border = "none";
            deleteBtn.style.cursor = "pointer";
            deleteBtn.style.padding = "0.4rem";
            deleteBtn.style.marginLeft = "auto";
            deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i>';
            deleteBtn.title = "Supprimer cette discussion";
            
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation(); // Stop click from propagating to the wrapper if needed
                deleteSession(session.id);
            });
            
            deleteBtn.addEventListener('mouseenter', () => deleteBtn.style.color = "var(--red)");
            deleteBtn.addEventListener('mouseleave', () => deleteBtn.style.color = "var(--text-light)");

            btnWrapper.appendChild(contentDiv);
            btnWrapper.appendChild(deleteBtn);
            historyList.appendChild(btnWrapper);
        });
    }

    function deleteSession(sessionId) {
        if(confirm("Êtes-vous sûr de vouloir supprimer cette discussion ?")) {
            chatSessions = chatSessions.filter(s => s.id !== sessionId);
            localStorage.setItem("cmc_chat_sessions", JSON.stringify(chatSessions));
            
            if (chatSessions.length === 0) {
                createNewSession();
            } else if (currentSessionId === sessionId) {
                // If we deleted the active session, switch to the first available one
                currentSessionId = chatSessions[0].id;
                chatHistory = chatSessions[0].messages;
                localStorage.setItem("cmc_current_session_id", currentSessionId);
                loadChatHistory();
                renderHistorySidebar();
            } else {
                // Just re-render sidebar
                renderHistorySidebar();
            }
        }
    }

    // New Chat Button logic
    const newChatBtn = document.getElementById("new-chat-btn");
    if (newChatBtn) {
        newChatBtn.addEventListener("click", () => {
            createNewSession();
            if (window.innerWidth <= 768 && appSidebar) {
                appSidebar.classList.remove("open"); // Close sidebar on mobile
            }
        });
    }

    // Call it immediately
    initSessions();

    // Speed Dial has been removed in the new design, removed toggle logic

    // Generate a unique ID for messages to track feedback
    function generateId() {
        return '_' + Math.random().toString(36).substr(2, 9);
    }

    function renderMessage(sender, text, msgId, existingFeedback = null) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message");
        msgDiv.classList.add(sender === "user" ? "user-message" : "bot-message");

        const avatarIcon = sender === "user" ? "fa-user" : "fa-robot";
        
        // Add feedback buttons for bot messages
        let feedbackHtml = '';
        if (sender === "bot") {
            const upClass = existingFeedback === 'upvote' ? 'active text-success' : '';
            const downClass = existingFeedback === 'downvote' ? 'active text-danger' : '';
            feedbackHtml = `
                <div class="feedback-btns" data-id="${msgId}">
                    <button class="icon-btn-sm feedback-btn upvote ${upClass}" title="Réponse utile" data-type="upvote"><i class="fas fa-thumbs-up"></i></button>
                    <button class="icon-btn-sm feedback-btn downvote ${downClass}" title="Réponse non pertinente" data-type="downvote"><i class="fas fa-thumbs-down"></i></button>
                </div>
            `;
        }

        // Build message DOM safely: do not interpret text as HTML
        const avatarDiv = document.createElement("div");
        avatarDiv.classList.add("avatar");
        // avatarIcon is controlled by code, not by user input
        avatarDiv.innerHTML = `<i class="fas ${avatarIcon}"></i>`;

        const contentDiv = document.createElement("div");
        contentDiv.classList.add("message-content");

        const textParagraph = document.createElement("p");
        // Use textContent so user/DOM input is not treated as HTML
        textParagraph.textContent = text;
        contentDiv.appendChild(textParagraph);

        if (feedbackHtml) {
            // feedbackHtml is constructed by this script for bot messages only
            contentDiv.insertAdjacentHTML("beforeend", feedbackHtml);
        }

        msgDiv.appendChild(avatarDiv);
        msgDiv.appendChild(contentDiv);

        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        
        // Add event listeners to new feedback buttons
        if (sender === "bot") {
            const upvoteBtn = msgDiv.querySelector('.upvote');
            const downvoteBtn = msgDiv.querySelector('.downvote');
            
            upvoteBtn.addEventListener('click', () => handleFeedback(msgId, 'upvote', upvoteBtn, downvoteBtn, text));
            downvoteBtn.addEventListener('click', () => handleFeedback(msgId, 'downvote', downvoteBtn, upvoteBtn, text));
        }
    }

    function appendMessage(sender, text) {
        const msgId = generateId();
        
        // Add to history and DOM
        chatHistory.push({ id: msgId, sender, text, feedback: null });
        saveSessions();
        
        renderMessage(sender, text, msgId);
        return msgId;
    }

    async function handleFeedback(msgId, type, clickedBtn, otherBtn, botText) {
        // Toggle UI
        clickedBtn.classList.add('active');
        if (type === 'upvote') clickedBtn.classList.add('text-success');
        if (type === 'downvote') clickedBtn.classList.add('text-danger');
        
        otherBtn.classList.remove('active', 'text-success', 'text-danger');
        
        // Update history
        const msgIndex = chatHistory.findIndex(m => m.id === msgId);
        if (msgIndex !== -1) {
            chatHistory[msgIndex].feedback = type;
            saveSessions();
        }
        
        // Send to server
        try {
            await fetch("/api/feedback", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    message_id: msgId, 
                    bot_message: botText, 
                    feedback: type 
                })
            });
        } catch (error) {
            console.error("Feedback error:", error);
        }
    }

    async function sendMessage(text) {
        if (!text.trim()) return;

        appendMessage("user", text);
        userInput.value = "";

        typingIndicator.style.display = "flex";
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();

            typingIndicator.style.display = "none";
            appendMessage("bot", data.response);

            // Text to speech
            speakText(data.response);
        } catch (error) {
            console.error("Error:", error);
            typingIndicator.style.display = "none";
            const currentLang = localStorage.getItem('cmc_lang') || 'fr';
            const errorMessages = {
                ar: "عذراً، حدث خطأ في الاتصال بالخادم. حاول مرة أخرى. 🔌",
                fr: "Désolé, une erreur s'est produite lors de la connexion au serveur.",
                en: "Sorry, a connection error occurred. Please try again."
            };
            appendMessage("bot", errorMessages[currentLang] || errorMessages['fr']);
        }
    }

    sendBtn?.addEventListener("click", () => {
        sendMessage(userInput.value);
    });

    userInput?.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendMessage(userInput.value);
        }
    });

    // Stop speaking if the user starts typing
    userInput?.addEventListener("input", () => {
        if ('speechSynthesis' in window && window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
        }
    });

    // Audio toggle button functionality
    if (audioToggleBtn) {
        audioToggleBtn.addEventListener("click", () => {
            audioEnabled = !audioEnabled;
            if (audioEnabled) {
                audioToggleBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
                audioToggleBtn.classList.remove("text-muted");
            } else {
                audioToggleBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
                audioToggleBtn.classList.add("text-muted");
                // Stop any current speech
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                }
            }
        });
    }

    // Quick Replies Functionality
    const qrBtns = document.querySelectorAll('.qr-btn');
    qrBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const textToSend = btn.textContent;
            // Optionally, you could hide the buttons after one is clicked
            // document.getElementById('quick-replies').style.display = 'none';
            sendMessage(textToSend);
        });
    });

    // Voice Input (Speech Recognition)
    if (voiceBtn) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onstart = function () {
                voiceBtn.classList.add("recording");
                voiceBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
            };

            recognition.onresult = function (event) {
                const speechResult = event.results[0][0].transcript;
                userInput.value = speechResult;
                sendMessage(speechResult);
            };

            recognition.onerror = function (event) {
                console.error("Speech recognition error", event.error);
                voiceBtn.classList.remove("recording");
                voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            };

            recognition.onend = function () {
                voiceBtn.classList.remove("recording");
                voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            };

            voiceBtn.addEventListener("click", () => {
                if (voiceBtn.classList.contains("recording")) {
                    recognition.stop();
                } else {
                    const currentLang = localStorage.getItem('cmc_lang') || 'fr';
                    if (currentLang === 'ar') {
                        recognition.lang = 'ar-MA';
                    } else if (currentLang === 'en') {
                        recognition.lang = 'en-US';
                    } else {
                        recognition.lang = 'fr-FR';
                    }
                    recognition.start();
                }
            });
        } else {
            console.log("Speech Recognition not supported in this browser.");
            voiceBtn.style.opacity = "0.5";
            voiceBtn.title = "Non supporté par votre navigateur";
        }
    }

    // Text to Speech Function
    function speakText(text) {
        if (!audioEnabled) return; // Don't speak if audio is disabled
        
        if ('speechSynthesis' in window) {
            // Cancel any ongoing speech before starting a new one
            window.speechSynthesis.cancel();
            
            // Remove html tags from text before speaking
            const tempDiv = document.createElement("div");
            tempDiv.innerHTML = text;
            const cleanText = tempDiv.textContent || tempDiv.innerText || "";

            const utterance = new SpeechSynthesisUtterance(cleanText);

            // Simple heuristic to detect Arabic letters
            const arabicPattern = /[\u0600-\u06FF]/;
            if (arabicPattern.test(cleanText)) {
                utterance.lang = 'ar-SA';
            } else {
                utterance.lang = 'fr-FR';
            }
            window.speechSynthesis.speak(utterance);
        }
    }
});
