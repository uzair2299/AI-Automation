"""Smiota Web Chat Gateway & Production Embeddable Iframe Widget."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/webchat", tags=["Channels - Smiota Web Chat"])


@router.get("/config", summary="Web Chat client bootstrap config")
async def webchat_config():
    """Client bootstrap metadata for webchat embeds."""
    return {
        "features": {
            "streaming": True,
            "websocket": True,
            "file_upload": True,
            "voice": False,
        },
        "default_agent": "customer",
        "theme": {
            "primary": "#4F46E5",
            "gradient": "linear-gradient(to right, #7C3AED, #4F46E5)",
        },
    }


@router.get("/embed", response_class=HTMLResponse, summary="Embeddable Iframe Chatbot Widget")
@router.get("/ui", response_class=HTMLResponse, summary="Embeddable Iframe Chatbot Widget (Alias)")
async def embed_widget():
    """Renders the production-ready chatbot widget optimized for iframe embedding."""
    html_content = """<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Smiota AI - Concierge Widget</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 4px; }
        .typing-dot { animation: typingAnimation 1.4s infinite ease-in-out; }
        .typing-dot:nth-child(1) { animation-delay: 0s; }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typingAnimation {
            0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
            40% { transform: scale(1); opacity: 1; }
        }
    </style>
</head>
<body class="h-full bg-slate-100 flex flex-col overflow-hidden font-sans antialiased m-0 p-0">

    <!-- Chat Container (Responsive & Iframe Optimized) -->
    <div id="chat-widget" class="flex flex-col h-full w-full bg-white shadow-xl relative select-none">
        
        <!-- Header: Violet-to-Indigo Gradient -->
        <div class="bg-gradient-to-r from-violet-600 to-indigo-600 px-5 py-3.5 text-white flex items-center justify-between shrink-0 shadow-sm">
            <div class="flex items-center space-x-3">
                <div class="relative">
                    <div class="w-10 h-10 rounded-full bg-white/20 p-1 border border-white/30 flex items-center justify-center font-bold text-base shadow-sm">
                        AI
                    </div>
                    <span class="absolute bottom-0 right-0 w-3 h-3 bg-emerald-400 border-2 border-indigo-600 rounded-full"></span>
                </div>
                <div>
                    <h1 class="font-semibold text-base tracking-tight leading-tight">Smiota AI Concierge</h1>
                    <p class="text-xs text-indigo-100 opacity-90">Customer, AIOps & Security AI</p>
                </div>
            </div>
            <div class="flex items-center space-x-1.5">
                <button id="minimize-btn" class="w-8 h-8 rounded-full hover:bg-white/10 flex items-center justify-center transition text-white/80 hover:text-white" title="Minimize">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path></svg>
                </button>
                <button id="close-btn" class="w-8 h-8 rounded-full hover:bg-white/10 flex items-center justify-center transition text-white/80 hover:text-white" title="Close">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>
        </div>

        <!-- Chat History Canvas -->
        <div id="chat-messages" class="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50">
            <!-- Timestamp Divider -->
            <div class="flex justify-center my-1">
                <span id="timestamp-tag" class="text-[11px] text-slate-400 font-medium px-3 py-1 bg-slate-200/60 rounded-full">Today</span>
            </div>

            <!-- Bot Welcome Message -->
            <div class="flex items-end space-x-2">
                <div class="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-[10px] font-bold shrink-0 shadow-xs">AI</div>
                <div class="bg-slate-100 text-slate-800 px-4 py-2.5 rounded-2xl rounded-bl-sm max-w-[85%] text-sm shadow-xs leading-relaxed">
                    <div class="flex items-center justify-between space-x-3 mb-1">
                        <span class="text-[10px] font-bold uppercase tracking-wider text-indigo-600">Smiota Concierge</span>
                        <span id="initial-bot-time" class="text-[10px] text-slate-400 font-medium"></span>
                    </div>
                    <div>
                        Hi there! 👋<br>
                        Welcome to Smiota. How can I assist you with your smart locker, parcel tracking, or support inquiry today?
                    </div>
                </div>
            </div>

            <!-- Interactive Quick Reply Pill Buttons -->
            <div id="quick-replies-container" class="grid grid-cols-2 gap-2 pt-1 px-8">
                <button onclick="sendQuickReply('Check parcel status')" class="text-xs text-indigo-600 border border-indigo-200 hover:bg-indigo-50 font-medium py-2 px-3 rounded-full transition text-center shadow-xs truncate">📦 Check parcel status</button>
                <button onclick="sendQuickReply('Door sensor troubleshooting')" class="text-xs text-indigo-600 border border-indigo-200 hover:bg-indigo-50 font-medium py-2 px-3 rounded-full transition text-center shadow-xs truncate">🔧 Door troubleshooting</button>
                <button onclick="sendQuickReply('Investigate GKE high CPU')" class="text-xs text-indigo-600 border border-indigo-200 hover:bg-indigo-50 font-medium py-2 px-3 rounded-full transition text-center shadow-xs truncate">⚡ SRE / AIOps Telemetry</button>
                <button onclick="sendQuickReply('Wazuh SIEM intrusion alert')" class="text-xs text-indigo-600 border border-indigo-200 hover:bg-indigo-50 font-medium py-2 px-3 rounded-full transition text-center shadow-xs truncate">🛡️ Security Triage</button>
            </div>
        </div>

        <!-- Input Bar Toolbar -->
        <div class="p-3 bg-white border-t border-slate-100 shrink-0">
            <form id="chat-form" class="flex items-center space-x-2 bg-slate-100/80 rounded-full px-3.5 py-1.5 border border-slate-200 focus-within:border-indigo-500 focus-within:bg-white transition shadow-xs">
                <input type="text" id="chat-input" placeholder="Type and press [enter]..." class="flex-1 bg-transparent text-sm text-slate-700 placeholder-slate-400 focus:outline-none py-1">
                
                <button type="button" class="text-slate-400 hover:text-slate-600 transition p-1" title="Add Emoji" onclick="insertEmoji('😊')">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                </button>
                <button type="button" class="text-slate-400 hover:text-slate-600 transition p-1" title="Upload Attachment" onclick="alert('File upload supported in cloud storage mode')">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                </button>
                
                <button type="submit" id="send-btn" class="w-8 h-8 bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-full flex items-center justify-center hover:opacity-90 transition shadow-sm shrink-0" title="Send">
                    <svg class="w-4 h-4 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
                </button>
            </form>
        </div>
    </div>

    <script>
        // Formatted timestamp helper
        function getFormattedTime() {
            return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }

        const now = new Date();
        const initialTime = getFormattedTime();
        document.getElementById('timestamp-tag').innerText = 'Today, ' + initialTime;
        const initBotTime = document.getElementById('initial-bot-time');
        if (initBotTime) initBotTime.innerText = initialTime;

        // SVG Ticks (WhatsApp / Modern Chat style)
        const singleTickSvg = `
            <svg class="w-3.5 h-3.5 inline-block text-indigo-200/80" viewBox="0 0 18 18" fill="none" stroke="currentColor" title="Sent">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M3 9l4 4L16 4" />
            </svg>
        `;

        const doubleTickSvg = `
            <svg class="w-3.5 h-3.5 inline-block text-sky-200" viewBox="0 0 18 18" fill="none" stroke="currentColor" title="Delivered & Read">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M1 9l4 4L14 4" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M5 9l4 4L18 4" />
            </svg>
        `;

        // Session ID management
        const sessionId = "webchat-" + Math.random().toString(36).substring(2, 9);
        const messagesContainer = document.getElementById('chat-messages');
        const form = document.getElementById('chat-form');
        const input = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');
        const quickRepliesContainer = document.getElementById('quick-replies-container');

        // PostMessage Cross-Origin Iframe Bridge
        function notifyParentHeight() {
            const height = document.body.scrollHeight;
            window.parent.postMessage({ type: 'resize-chatbot', height: height }, '*');
        }

        function formatMarkdown(str) {
            if (!str) return '';
            return str
                .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                .replace(/`(.*?)`/g, '<code class="bg-indigo-50 text-indigo-700 px-1 py-0.5 rounded font-mono text-xs">$1</code>')
                .replace(/\\n/g, '<br>');
        }

        function appendMessage(sender, text, agentName = 'AI', requiresApproval = false, suggestedActions = []) {
            const isUser = sender === 'user';
            const timeStr = getFormattedTime();
            const div = document.createElement('div');
            div.className = `flex items-end space-x-2 ${isUser ? 'justify-end' : 'justify-start'}`;
            
            if (!isUser) {
                let approvalBadge = '';
                if (requiresApproval) {
                    approvalBadge = `
                        <div class="mt-2.5 p-2.5 bg-rose-50 border border-rose-200 rounded-lg text-rose-700 text-xs flex items-center space-x-1.5">
                            <span class="font-bold">🔒 HITL Gate:</span>
                            <span>Action mutates infrastructure and requires admin approval.</span>
                        </div>
                    `;
                }

                div.innerHTML = `
                    <div class="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-[10px] font-bold shrink-0 shadow-xs">${agentName.slice(0, 2).toUpperCase()}</div>
                    <div class="bg-slate-100 text-slate-800 px-4 py-2.5 rounded-2xl rounded-bl-sm max-w-[85%] text-sm shadow-xs leading-relaxed">
                        <div class="flex items-center justify-between space-x-3 mb-1">
                            <span class="text-[10px] font-bold uppercase tracking-wider text-indigo-600">${agentName} Agent</span>
                            <span class="text-[10px] text-slate-400 font-medium">${timeStr}</span>
                        </div>
                        <div>${formatMarkdown(text)}</div>
                        ${approvalBadge}
                    </div>
                `;
            } else {
                div.innerHTML = `
                    <div class="bg-gradient-to-r from-violet-600 to-indigo-600 text-white px-4 py-2.5 rounded-2xl rounded-br-sm max-w-[85%] text-sm shadow-xs leading-relaxed">
                        <div>${text}</div>
                        <div class="flex items-center justify-end space-x-1 mt-1 text-[10px] text-indigo-200/90 font-medium select-none">
                            <span>${timeStr}</span>
                            <span class="user-tick-status inline-flex items-center">${singleTickSvg}</span>
                        </div>
                    </div>
                `;
            }

            messagesContainer.appendChild(div);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            notifyParentHeight();

            // Render dynamic suggested actions if returned
            if (suggestedActions && suggestedActions.length > 0) {
                renderQuickReplies(suggestedActions);
            }
        }

        function markLastUserMessageDelivered() {
            const ticks = document.querySelectorAll('.user-tick-status');
            if (ticks.length > 0) {
                const lastTick = ticks[ticks.length - 1];
                lastTick.innerHTML = doubleTickSvg;
            }
        }

        function renderQuickReplies(actions) {
            quickRepliesContainer.innerHTML = '';
            if (!actions || actions.length === 0) {
                quickRepliesContainer.style.display = 'none';
                return;
            }
            quickRepliesContainer.style.display = 'grid';
            actions.slice(0, 4).forEach(act => {
                const btn = document.createElement('button');
                btn.className = "text-xs text-indigo-600 border border-indigo-200 hover:bg-indigo-50 font-medium py-2 px-3 rounded-full transition text-center shadow-xs truncate";
                btn.innerText = act;
                btn.onclick = () => sendQuickReply(act);
                quickRepliesContainer.appendChild(btn);
            });
            // Crucial: Move quickRepliesContainer to the very bottom of messagesContainer
            messagesContainer.appendChild(quickRepliesContainer);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            notifyParentHeight();
        }

        function showTypingIndicator() {
            const typingDiv = document.createElement('div');
            typingDiv.id = 'typing-indicator';
            typingDiv.className = 'flex items-center space-x-2 text-slate-400 text-xs py-1 px-8';
            typingDiv.innerHTML = `
                <div class="flex space-x-1">
                    <span class="w-2 h-2 bg-indigo-500 rounded-full typing-dot"></span>
                    <span class="w-2 h-2 bg-indigo-500 rounded-full typing-dot"></span>
                    <span class="w-2 h-2 bg-indigo-500 rounded-full typing-dot"></span>
                </div>
                <span class="text-[11px] font-medium text-slate-400">Agent is reasoning...</span>
            `;
            messagesContainer.appendChild(typingDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function removeTypingIndicator() {
            const el = document.getElementById('typing-indicator');
            if (el) el.remove();
        }

        async function executeQuery(messageText) {
            // Hide old quick replies while query is being processed
            if (quickRepliesContainer) {
                quickRepliesContainer.innerHTML = '';
                quickRepliesContainer.style.display = 'none';
            }
            appendMessage('user', messageText);
            showTypingIndicator();

            try {
                const response = await fetch('/api/v1/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: messageText,
                        channel: 'webchat',
                        session_id: sessionId
                    })
                });

                const data = await response.json();
                removeTypingIndicator();
                markLastUserMessageDelivered();
                appendMessage('bot', data.response, data.agent_used, data.requires_approval, data.suggested_actions);
            } catch (err) {
                removeTypingIndicator();
                appendMessage('bot', 'Network error communicating with Smiota AI Core.', 'Error');
            }
        }

        function sendQuickReply(text) {
            executeQuery(text);
        }

        function insertEmoji(emoji) {
            input.value += emoji;
            input.focus();
        }

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            executeQuery(text);
        });

        // Parent communication buttons
        document.getElementById('close-btn').addEventListener('click', () => {
            window.parent.postMessage({ type: 'close-chatbot' }, '*');
        });

        document.getElementById('minimize-btn').addEventListener('click', () => {
            window.parent.postMessage({ type: 'minimize-chatbot' }, '*');
        });

        // Initial height notification
        window.addEventListener('load', notifyParentHeight);
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)


@router.get("/demo", response_class=HTMLResponse, summary="Live Iframe Host Demonstration Page")
async def host_demo_page():
    """Renders a sample host webpage demonstrating seamless iframe embedding and postMessage integration."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smiota Host Website - Embed Demo</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>body { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen flex flex-col justify-between">

    <!-- Sample Host Navbar -->
    <header class="border-b border-slate-800 bg-slate-950/70 backdrop-blur-md px-8 py-4 flex items-center justify-between sticky top-0 z-10">
        <div class="flex items-center space-x-3">
            <div class="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center font-extrabold text-white">S</div>
            <span class="font-bold text-lg tracking-tight">Smiota Cloud Portal</span>
        </div>
        <div class="flex items-center space-x-6 text-sm text-slate-400">
            <a href="#" class="hover:text-white transition">Dashboard</a>
            <a href="#" class="hover:text-white transition">Smart Lockers</a>
            <a href="#" class="hover:text-white transition">Telemetry</a>
            <span class="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">Live System</span>
        </div>
    </header>

    <!-- Host Hero Section -->
    <main class="max-w-4xl mx-auto px-6 py-16 text-center flex-1 flex flex-col items-center justify-center">
        <div class="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold mb-6">
            <span>✨ Production-Ready Iframe Widget</span>
        </div>
        <h1 class="text-4xl sm:text-5xl font-extrabold tracking-tight leading-tight mb-4">
            Embeddable Multi-Agent AI <br><span class="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-indigo-400">In Any Website</span>
        </h1>
        <p class="text-slate-400 text-base max-w-xl mx-auto mb-8">
            This demonstration shows how third-party host sites embed the Smiota AI Chatbot inside an iframe using zero-dependency postMessage resizing and float controls.
        </p>

        <button onclick="toggleChatbot()" class="px-6 py-3 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold shadow-lg shadow-indigo-500/20 transition transform hover:-translate-y-0.5">
            Click to Toggle Floating Chatbot
        </button>
    </main>

    <!-- Floating Chatbot Launcher & Iframe Widget Wrapper -->
    <div id="chatbot-wrapper" class="fixed bottom-6 right-6 z-50 flex flex-col items-end">
        
        <!-- Embedded Iframe Window (Hidden initially or toggleable) -->
        <div id="iframe-card" class="w-[380px] h-[580px] mb-4 rounded-2xl overflow-hidden shadow-2xl border border-slate-700/60 transition-all duration-300 transform scale-100 origin-bottom-right">
            <iframe 
                id="smiota-iframe"
                src="/api/v1/channels/webchat/embed" 
                class="w-full h-full border-0"
                allow="clipboard-write">
            </iframe>
        </div>

        <!-- Floating Action Button (FAB) -->
        <button id="chatbot-fab" onclick="toggleChatbot()" class="w-14 h-14 rounded-full bg-gradient-to-r from-violet-600 to-indigo-600 text-white flex items-center justify-center shadow-xl hover:scale-105 active:scale-95 transition">
            <svg id="fab-open-icon" class="w-6 h-6 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
            <svg id="fab-close-icon" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
    </div>

    <script>
        const card = document.getElementById('iframe-card');
        const openIcon = document.getElementById('fab-open-icon');
        const closeIcon = document.getElementById('fab-close-icon');
        let isOpen = true;

        function toggleChatbot() {
            isOpen = !isOpen;
            if (isOpen) {
                card.classList.remove('hidden');
                openIcon.classList.add('hidden');
                closeIcon.classList.remove('hidden');
            } else {
                card.classList.add('hidden');
                openIcon.classList.remove('hidden');
                closeIcon.classList.add('hidden');
            }
        }

        // Listen for postMessage from the iframe
        window.addEventListener('message', (event) => {
            if (!event.data) return;
            if (event.data.type === 'close-chatbot' || event.data.type === 'minimize-chatbot') {
                toggleChatbot();
            }
        });
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)
