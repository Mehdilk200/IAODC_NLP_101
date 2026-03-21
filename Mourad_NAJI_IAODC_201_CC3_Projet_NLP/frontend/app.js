/**
 * StyleAI — SaaS Dynamic Frontend Logic
 * Implements conversational state management, confidence handling, and rich card rendering.
 */

const API_BASE = 'http://127.0.0.1:8000';

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('msgInput');
    const sendBtn = document.getElementById('sendBtn');
    const messagesList = document.getElementById('messagesList');
    const welcomeHero = document.querySelector('.welcome-hero');

    const scrollToBottom = () => {
        messagesList.scrollTop = messagesList.scrollHeight;
    };

    const addMessage = (text, type = 'user', data = null) => {
        if (welcomeHero) welcomeHero.style.display = 'none';

        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${type}`;

        const avatar = type === 'user' ? 'U' : '✦';

        let contentHtml = `<div class="msg-bubble">${type === 'ai' ? renderAIContent(text, data) : escapeHtml(text)}</div>`;

        msgDiv.innerHTML = `
            <div class="msg-avatar">${avatar}</div>
            ${contentHtml}
        `;

        messagesList.appendChild(msgDiv);
        scrollToBottom();
    };

    const renderAIContent = (text, data) => {
        if (!data) return escapeHtml(text);

        let html = '';

        // 1. Fallback / Confidence Warning
        if (data.fallback_message) {
            html += `<div class="fallback-alert">💡 ${data.fallback_message}</div>`;
        }

        // 2. Main Response Text
        html += `<div class="ai-text">${escapeHtml(text)}</div>`;

        // 3. Results Grid
        if (data.results && data.results.length > 0) {
            html += `<div class="outfits-grid">
                ${data.results.map(outfit => `
                    <div class="outfit-card">
                        <img src="${outfit.image_url}" alt="${outfit.title}" class="outfit-img" onerror="this.onerror=null; this.src='/static/images/placeholder.jpg';">
                        <div class="outfit-info">
                            <div class="outfit-brand">${outfit.tags[0] || 'Exclusive'}</div>
                            <h3 class="outfit-title">${escapeHtml(outfit.title)}</h3>
                            <div class="outfit-price">${outfit.price} dh</div>
                            <div class="outfit-expl">${formatMarkdown(outfit.explanation)}</div>
                        </div>
                    </div>
                `).join('')}
            </div>`;
        } else if (!data.fallback_message) {
            html += `<div class="no-results">I couldn't find a perfect match for that specific request. Try adjusting your description!</div>`;
        }

        return html;
    };

    const handleSend = async (queryOverride = null) => {
        const query = queryOverride || input.value.trim();
        if (!query) return;

        // User message
        addMessage(query, 'user');
        input.value = '';
        input.disabled = true;
        sendBtn.disabled = true;

        // Typing indicator
        const typingId = 'typing-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai typing';
        typingDiv.id = typingId;
        typingDiv.innerHTML = `
            <div class="msg-avatar">✦</div>
            <div class="loading-dots"><div class="dot-anim"></div><div class="dot-anim"></div><div class="dot-anim"></div></div>
        `;
        messagesList.appendChild(typingDiv);
        scrollToBottom();

        try {
            const response = await fetch(`${API_BASE}/recommend`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query, top_k: 4 })
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`API Error (${response.status}): ${errorText || response.statusText}`);
            }

            const data = await response.json();

            // Remove typing
            document.getElementById(typingId).remove();

            // AI message
            const mainText = `Based on your request, I've curated a few options that match your vibe (Confidence: ${Math.round(data.confidence * 100)}%).`;
            addMessage(mainText, 'ai', data);

        } catch (err) {
            document.getElementById(typingId).remove();
            addMessage(`I apologize, but I encountered a technical issue: ${err.message}`, 'ai');
        } finally {
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        }
    };

    // Event Listeners
    sendBtn.addEventListener('click', () => handleSend());
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });

    // Suggestion Chips
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            handleSend(chip.dataset.query);
        });
    });

    // Utils
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function formatMarkdown(text) {
        // Simple bold/italic formatter
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }
});
