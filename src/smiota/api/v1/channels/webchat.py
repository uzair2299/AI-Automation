"""Smiota Web Chat Gateway & Production Embeddable Iframe Widget."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

BOT_MASCOT_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="60 40 100 148" width="100%" height="100%" class="ai-bot-svg" role="img" aria-label="AI Assistant Bot">
  <defs>
    <!-- Robot Head 3D Spherical Lighting Gradient -->
    <linearGradient id="robot-head-grad" x1="20%" y1="10%" x2="85%" y2="95%">
      <stop offset="0%" stop-color="#dbe8fd"/>
      <stop offset="30%" stop-color="#b7d3fc"/>
      <stop offset="75%" stop-color="#81adfa"/>
      <stop offset="100%" stop-color="#5d94f2"/>
    </linearGradient>

    <!-- Visor Deep Navy Shield -->
    <linearGradient id="robot-visor-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#2e3d82"/>
      <stop offset="50%" stop-color="#1e2962"/>
      <stop offset="100%" stop-color="#131a42"/>
    </linearGradient>

    <!-- Visor Glass Glare / Sheen -->
    <linearGradient id="visor-glare-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.35"/>
      <stop offset="40%" stop-color="#ffffff" stop-opacity="0.1"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>

    <!-- Torso 3D Gradient -->
    <linearGradient id="robot-torso-grad" x1="20%" y1="0%" x2="80%" y2="100%">
      <stop offset="0%" stop-color="#cce0fc"/>
      <stop offset="50%" stop-color="#92bdfa"/>
      <stop offset="100%" stop-color="#6399f3"/>
    </linearGradient>

    <!-- Arms Capsule Gradient -->
    <linearGradient id="robot-arm-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#d0e3fc"/>
      <stop offset="100%" stop-color="#79a9f7"/>
    </linearGradient>

    <!-- Cyan Neon Glow Filter -->
    <filter id="cyan-neon-glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Ground Shadow Blur Filter -->
    <filter id="ground-shadow-blur" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2.5"/>
    </filter>
  </defs>

  <!-- 1. Ground Shadow (Breathing Scale & Opacity) -->
  <g class="mascot-svg-shadow">
    <ellipse cx="110" cy="180" rx="32" ry="6" fill="#222b5e" opacity="0.55" filter="url(#ground-shadow-blur)"/>
  </g>

  <!-- 2. Central Robot Mascot -->
  <g class="mascot-svg-robot">
    <!-- Thruster Tail Cone & Core Glow -->
    <path d="M 103 146 L 110 162 L 117 146 Z" fill="#6399f3"/>
    <ellipse cx="110" cy="162.5" rx="5.5" ry="2.8" fill="#00f5d4" filter="url(#cyan-neon-glow)"/>

    <!-- Torso -->
    <rect x="92" y="120" width="36" height="30" rx="15" fill="url(#robot-torso-grad)"/>
    <path d="M 94 130 C 94 123 99 122 106 121 C 98 123 94 128 94 135 Z" fill="#ffffff" opacity="0.4"/>

    <!-- Chest Glowing Reactor Button -->
    <circle cx="110" cy="131" r="3.5" fill="#00f5d4" filter="url(#cyan-neon-glow)"/>
    <circle cx="110" cy="131" r="1.5" fill="#ffffff"/>

    <!-- Floating Arms -->
    <g transform="rotate(-16 76 126)">
      <rect x="68" y="121" width="17" height="10.5" rx="5.25" fill="url(#robot-arm-grad)"/>
      <ellipse cx="72" cy="124" rx="4" ry="2" fill="#ffffff" opacity="0.45"/>
    </g>
    <g transform="rotate(16 144 126)">
      <rect x="135" y="121" width="17" height="10.5" rx="5.25" fill="url(#robot-arm-grad)"/>
      <ellipse cx="140" cy="124" rx="4" ry="2" fill="#ffffff" opacity="0.45"/>
    </g>

    <!-- Antenna Stem & Neon Bulb -->
    <line x1="124" y1="68" x2="134" y2="47" stroke="#00f5d4" stroke-width="3" stroke-linecap="round" filter="url(#cyan-neon-glow)"/>
    <circle cx="134" cy="47" r="4" fill="#00f5d4" filter="url(#cyan-neon-glow)"/>
    <circle cx="133" cy="46" r="1.8" fill="#ffffff"/>

    <!-- Head Dome Shell -->
    <rect x="72" y="60" width="76" height="58" rx="29" fill="url(#robot-head-grad)"/>
    <ellipse cx="92" cy="70" rx="16" ry="7" fill="#ffffff" opacity="0.45" transform="rotate(-15 92 70)"/>

    <!-- Headset Ear Cushions -->
    <rect x="70" y="86" width="5.5" height="13" rx="2.75" fill="#1a2356"/>
    <rect x="144.5" y="86" width="5.5" height="13" rx="2.75" fill="#1a2356"/>

    <!-- Face Visor Screen -->
    <rect x="81" y="70" width="58" height="38" rx="19" fill="url(#robot-visor-grad)"/>
    <path d="M 85 86 C 85 76 92 72 101 71 L 115 71 C 99 74 92 79 89 90 Z" fill="url(#visor-glare-grad)"/>

    <!-- Glowing Cyan Left Eye (Blinks when authenticated) -->
    <g class="mascot-left-eye" filter="url(#cyan-neon-glow)">
      <rect x="90.5" y="80.5" width="10.5" height="14.5" rx="5.25" fill="#00f5d4"/>
      <circle cx="94" cy="84" r="1.8" fill="#ffffff"/>
    </g>
    <!-- Glowing Cyan Right Eye (Winks in guest mode, blinks in sync when authenticated) -->
    <g class="mascot-right-eye mascot-eye-wink" filter="url(#cyan-neon-glow)">
      <rect x="119" y="80.5" width="10.5" height="14.5" rx="5.25" fill="#00f5d4"/>
      <circle cx="122.5" cy="84" r="1.8" fill="#ffffff"/>
    </g>

    <!-- Cheerful Smile -->
    <path d="M 104 97 Q 110 102.5 116 97 Z" fill="#ffffff"/>

    <!-- Headset Boom Microphone -->
    <path d="M 147 94 C 147 107 134 110.5 124 105.5" fill="none" stroke="#00f5d4" stroke-width="2.6" stroke-linecap="round" filter="url(#cyan-neon-glow)"/>
    <circle cx="123.5" cy="105.5" r="3.2" fill="#00f5d4" filter="url(#cyan-neon-glow)"/>
    <circle cx="122.5" cy="104.5" r="1.2" fill="#ffffff"/>
  </g>
</svg>"""

router = APIRouter(prefix="/webchat", tags=["Channels - Smiota Web Chat"])


@router.get("/config", summary="Web Chat client bootstrap config")
async def webchat_config():
    """Client bootstrap metadata for webchat embeds."""
    from smiota.core.config import get_settings
    settings = get_settings()
    return {
        "assistant_name": getattr(settings, "WEBCHAT_ASSISTANT_NAME", "Smiota Assistant"),
        "subtitle": getattr(settings, "WEBCHAT_SUBTITLE", "Smart Locker & Parcel Concierge"),
        "welcome_title": getattr(settings, "WEBCHAT_WELCOME_TITLE", "Welcome to Smiota!"),
        "welcome_message": getattr(
            settings,
            "WEBCHAT_WELCOME_MESSAGE",
            "Hi there! Welcome to Smiota. How can I help you today?",
        ),
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
async def embed_widget(
    welcome_title: str | None = None,
    welcome_msg: str | None = None,
    subtitle: str | None = None,
    assistant_name: str | None = None,
):
    """Renders the production-ready chatbot widget optimized for iframe embedding."""
    from smiota.core.config import get_settings
    settings = get_settings()
    active_title = welcome_title or getattr(settings, "WEBCHAT_WELCOME_TITLE", "Welcome to Smiota!")
    active_msg = welcome_msg or getattr(
        settings,
        "WEBCHAT_WELCOME_MESSAGE",
        "Hi there! Welcome to Smiota. How can I help you today?",
    )
    active_subtitle = subtitle or getattr(settings, "WEBCHAT_SUBTITLE", "Smart Locker & Parcel Concierge")
    active_name = assistant_name or getattr(settings, "WEBCHAT_ASSISTANT_NAME", "Smiota Assistant")
    html_content = r"""<!DOCTYPE html>
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
    
        /* Central Mascot Robot SVG & Micro-Animations */
        .ai-bot-svg { width: 100%; height: 100%; overflow: visible; }
        .bot-text-body, .streaming-content { white-space: normal; word-break: break-word; }
        .mascot-svg-shadow { animation: shadowPulse 4s ease-in-out infinite; transform-box: fill-box; transform-origin: 110px 180px; }
        .mascot-svg-robot { animation: botHover 4s ease-in-out infinite; transform-box: fill-box; transform-origin: 110px 105px; }
        .mascot-eye-wink { animation: eyeWink 3.8s ease-in-out infinite; transform-box: fill-box; transform-origin: 50% 50%; }

        @keyframes eyeWink {
            0%, 42%, 58%, 100% { transform: scaleY(1); }
            49%, 51% { transform: scaleY(0.08); }
        }

        @keyframes botHover {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-4px); }
        }
        @keyframes shadowPulse {
            0%, 100% { transform: scaleX(1); opacity: 0.55; }
            50% { transform: scaleX(0.85); opacity: 0.32; }
        }
        /* Authenticated Mascot State: Both Eyes Blinking in Sync */
        .is-authenticated .mascot-left-eye,
        .is-authenticated .mascot-right-eye {
            animation: bothEyesBlink 2.5s ease-in-out infinite !important;
            transform-box: fill-box;
            transform-origin: 50% 50%;
        }

        @keyframes bothEyesBlink {
            0%, 42%, 58%, 100% { transform: scaleY(1); }
            48%, 52% { transform: scaleY(0.08); }
        }
    </style>
</head>
<body class="h-full bg-slate-100 flex flex-col overflow-hidden font-sans antialiased m-0 p-0">

    <!-- Chat Container (Responsive & Iframe Optimized) -->
    <div id="chat-widget" class="flex flex-col h-full w-full bg-white shadow-xl relative select-none">
        
        <!-- Header: Violet-to-Indigo Gradient -->
        <div class="bg-gradient-to-r from-violet-600 to-indigo-600 px-5 py-3.5 text-white flex items-center justify-between shrink-0 shadow-sm">
            <div class="flex items-center space-x-3">
                <div id="mascot-header-avatar" class="relative shrink-0">
                    <div id="mascot-header-shell" class="w-11 h-11 rounded-full bg-white/20 backdrop-blur-md border border-white/40 shadow-sm flex items-center justify-center p-1 hover:scale-105 transition-transform">
                        __BOT_SVG__
                    </div>
                    <span id="mascot-status-dot" class="absolute bottom-0 right-0 w-3 h-3 bg-emerald-400 border-2 border-indigo-600 rounded-full shadow-xs"></span>
                </div>
                <div>
                    <h1 class="font-semibold text-base tracking-tight leading-tight">Smiota AI Assistant</h1>
                    <p class="text-xs text-indigo-100 opacity-90 transition-all" id="header-subtitle">__SUBTITLE__</p>
                </div>
            </div>

            <!-- Header Action Controls -->
            <div class="flex items-center space-x-1.5">
                <button type="button" onclick="startNewChat()" title="Start New Conversation" class="px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-indigo-100 hover:text-white transition flex items-center space-x-1 text-xs font-medium cursor-pointer">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                    <span>New Chat</span>
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
            <div id="initial-welcome-bubble" class="flex items-end space-x-2.5">
                <div class="w-8 h-8 rounded-full bg-white border border-indigo-100 shadow-xs flex items-center justify-center p-0.5 shrink-0 select-none relative">__BOT_SVG__</div>
                <div class="bg-white text-slate-800 px-4 py-3 rounded-[18px] rounded-bl-[4px] max-w-[82%] text-sm border border-slate-200/80 shadow-[0_2px_8px_rgba(0,0,0,0.03)] leading-relaxed">
                    <div class="flex items-center justify-between space-x-3 mb-1.5 pb-1 border-b border-slate-100/90">
                        <span class="text-[11px] font-bold uppercase tracking-wider text-indigo-600" id="bot-sender-name">__ASSISTANT_NAME__</span>
                        <span id="initial-bot-time" class="text-[11px] text-slate-400 font-medium"></span>
                    </div>
                    <div id="welcome-message-body" class="space-y-1">
                        <div class="font-semibold text-slate-900 text-sm" id="welcome-title-text">__WELCOME_TITLE__ 👋</div>
                        <div class="text-slate-700 text-sm leading-relaxed" id="welcome-msg-text">__WELCOME_MESSAGE__</div>
                    </div>
                </div>
            </div>

            <!-- Interactive Quick Reply Pill Buttons -->
            <div id="quick-replies-container" class="grid grid-cols-2 gap-2 pt-1 px-8">
                <button type="button" onclick="sendQuickReply('Where is my package?')" class="text-xs text-indigo-600 bg-white hover:bg-indigo-50/80 border border-indigo-200/80 hover:border-indigo-300 font-medium py-2 px-3 rounded-xl transition text-center shadow-xs truncate">📦 Track package</button>
                <button type="button" onclick="sendQuickReply('Resend pickup PIN')" class="text-xs text-indigo-600 bg-white hover:bg-indigo-50/80 border border-indigo-200/80 hover:border-indigo-300 font-medium py-2 px-3 rounded-xl transition text-center shadow-xs truncate">🔑 Get pickup PIN</button>
                <button type="button" onclick="sendQuickReply('What does Smiota offer?')" class="text-xs text-indigo-600 bg-white hover:bg-indigo-50/80 border border-indigo-200/80 hover:border-indigo-300 font-medium py-2 px-3 rounded-xl transition text-center shadow-xs truncate">🏢 Smiota smart lockers</button>
                <button type="button" onclick="sendQuickReply('Locker door did not open')" class="text-xs text-indigo-600 bg-white hover:bg-indigo-50/80 border border-indigo-200/80 hover:border-indigo-300 font-medium py-2 px-3 rounded-xl transition text-center shadow-xs truncate">🚪 Locker door help</button>
            </div>
        </div>

        <!-- Input Bar Toolbar -->
        <div class="p-3 bg-white border-t border-slate-100 shrink-0">
            <form id="chat-form" class="flex items-center space-x-2 bg-slate-100/80 rounded-full px-4 py-1.5 border border-slate-200 focus-within:border-indigo-500 focus-within:bg-white transition shadow-xs">
                <input type="text" id="chat-input" placeholder="Type and press [enter]..." class="flex-1 bg-transparent text-sm text-slate-700 placeholder-slate-400 focus:outline-none py-1.5">
                
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

        const botAvatarSvg = `__BOT_SVG__`;
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

        // Session & Resident ID management (from URL parameters or auto-generated)
        const urlParams = new URLSearchParams(window.location.search);
        // Client-side URL query parameter hydration for title and message
        if (urlParams.get('welcome_title')) {
            const el = document.getElementById('welcome-title-text');
            if (el) el.innerText = urlParams.get('welcome_title') + ' 👋';
        }
        if (urlParams.get('welcome_msg')) {
            const el = document.getElementById('welcome-msg-text');
            if (el) el.innerText = urlParams.get('welcome_msg');
        }
        if (urlParams.get('subtitle')) {
            const el = document.getElementById('header-subtitle');
            if (el) el.innerText = urlParams.get('subtitle');
        }
        const STORAGE_KEY = 'smiota_active_chat_session_id';
        const cachedSid = localStorage.getItem(STORAGE_KEY);
        let sessionId = urlParams.get('session_id') || cachedSid || ("webchat-" + Math.random().toString(36).substring(2, 9));
        const residentId = urlParams.get('resident_id') || urlParams.get('user_id') || null;

        // Chatbot Authentication State & One-Time Code Exchange
        let chatSessionToken = null;
        let authenticatedUser = null;
        let historyRestored = false;

        async function restoreChatHistory(activeSessionId, token) {
            if (!activeSessionId || !token || historyRestored) return;
            try {
                const res = await fetch('/api/v1/chat/history/' + encodeURIComponent(activeSessionId), {
                    headers: { 'Authorization': 'Bearer ' + token }
                });
                if (res.ok) {
                    const data = await res.json();
                    if (data.messages && data.messages.length > 0) {
                        historyRestored = true;
                        console.log(`Restoring ${data.messages.length} previous conversation messages...`);
                        
                        // Hide initial welcome message if user already has an active history
                        const initBubble = document.getElementById('initial-welcome-bubble');
                        if (initBubble) initBubble.style.display = 'none';

                        for (const msg of data.messages) {
                            const textContent = (typeof msg.content === 'object' && msg.content !== null) ? (msg.content.text || '') : (msg.content || '');
                            const senderRole = msg.sender?.role || msg.role || 'user';
                            const senderName = msg.sender?.name || msg.sender_name || msg.agent_name || 'AI';
                            const isApproval = msg.type === 'approval_gate' || msg.message_type === 'approval_gate';
                            const actions = (typeof msg.content === 'object' && msg.content !== null && msg.content.suggested_actions) ? msg.content.suggested_actions : (msg.suggested_actions || []);
                            appendMessage(
                                senderRole === 'user' ? 'user' : 'bot',
                                textContent,
                                senderName,
                                isApproval,
                                actions
                            );
                        }
                    }
                }
            } catch (err) {
                console.warn("Could not restore chat history:", err);
            }
        }

        async function exchangeBootstrapCode(bootstrapCode) {
            if (!bootstrapCode) return;
            try {
                console.log("Exchanging bootstrap code for chatbot session...");
                const exchangePayload = { code: bootstrapCode };
                const savedId = localStorage.getItem(STORAGE_KEY);
                if (savedId && savedId.startsWith('sess-')) {
                    exchangePayload.session_id = savedId;
                }

                const res = await fetch('/api/v1/auth/exchange', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(exchangePayload)
                });
                if (res.ok) {
                    const data = await res.json();
                    const prevSessionId = sessionId;
                    chatSessionToken = data.access_token;
                    authenticatedUser = data.user;
                    if (data.session_id) {
                        sessionId = data.session_id;
                        localStorage.setItem(STORAGE_KEY, data.session_id);
                    }
                    console.log("Chatbot session established for user:", data.user?.user_id, "session:", sessionId);
                    
                    // Activate both eyes blinking and protected shield forcefield
                    setAuthenticatedMascotState(true, data.user);
                    
                    window.parent.postMessage({ type: 'auth-success', user: data.user, session_id: data.session_id }, '*');

                    // If session changed or socket is not connected, reconnect with authenticated session
                    if (!wsConnected || (data.session_id && data.session_id !== prevSessionId)) {
                        console.log("Re-initializing WebSocket connection with authenticated session:", sessionId);
                        if (wsSocket) {
                            try { wsSocket.close(); } catch(e){}
                        }
                        initWebSocket();
                    }

                    // Automatically restore previous conversation history so closing/reopening drawer retains chat!
                    await restoreChatHistory(data.session_id, data.access_token);
                } else {
                    console.warn("Bootstrap code exchange rejected with status:", res.status);
                    setAuthenticatedMascotState(false);
                    window.parent.postMessage({ type: 'auth-failed', status: res.status }, '*');
                }
            } catch (err) {
                console.error("Error exchanging bootstrap code:", err);
            }
        }

        function setAuthenticatedMascotState(isAuthenticated, user = null) {
            const avatarContainer = document.getElementById('mascot-header-avatar');
            const subtitleEl = document.getElementById('header-subtitle');

            if (isAuthenticated) {
                document.body.classList.add('is-authenticated');
                if (avatarContainer) avatarContainer.classList.add('is-authenticated');
                const displayName = user?.name || (user?.first_name ? (user.first_name + " " + (user.last_name || "")) : "");
                if (subtitleEl && displayName.trim()) {
                    subtitleEl.innerHTML = `<span class="inline-flex items-center text-emerald-200 font-medium">Verified: <strong>${displayName.trim()}</strong></span>`;
                }
            } else {
                document.body.classList.remove('is-authenticated');
                if (avatarContainer) avatarContainer.classList.remove('is-authenticated');
            }
        }

        // Listen for postMessage from parent host application
        window.addEventListener('message', (event) => {
            if (!event.data) return;
            if (event.data.type === 'auth-code' && event.data.code) {
                exchangeBootstrapCode(event.data.code);
            }
        });

        // Auto-exchange if code query parameter is provided in iframe URL (?code=...)
        const initialCode = urlParams.get('code');
        if (initialCode) {
            exchangeBootstrapCode(initialCode);
        }

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
            
            // Normalize line breaks
            let text = str.replace(/\r\n/g, '\n');

            // 1. Normalize squashed separators & headings
            text = text.replace(/\s*(---|___|\*\*\*)\s*/g, '\n\n---\n\n');
            text = text.replace(/\s*(#{1,4}\s+)/g, '\n\n$1');
            text = text.replace(/(#{1,4}\s+[^?\n:]+[?:])\s+([A-Z])/g, '$1\n\n$2');

            // 2. Normalize inline bullet and numbered lists that lack newlines
            // e.g. "deliveries: * Small: ... * Medium: ..." or "works: 1. Delivery ... 2. Instant ..."
            text = text.replace(/([.:!?])\s*([*•\-])\s+/g, '$1\n* ');
            text = text.replace(/([.:!?])\s*(\d+\.)\s+/g, '$1\n$2 ');

            // 3. Bold: **text**
            text = text.replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold text-slate-900">$1</strong>');

            // 4. Inline code: `code`
            text = text.replace(/`([^`\n]+)`/g, '<code class="bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded font-mono text-xs border border-indigo-100 font-medium">$1</code>');

            // 5. Italic: *(text)* or *text* (excluding space directly after opening *)
            text = text.replace(/\*(?!\s)([^*\n]+?)(?<!\s)\*/g, '<em class="text-slate-600 not-italic font-medium">$1</em>');

            // Process lines for headings, dividers, lists, and paragraphs
            const rawLines = text.split('\n');
            const processed = [];
            let inList = false;
            let listType = null; // 'ul' or 'ol'

            for (let i = 0; i < rawLines.length; i++) {
                const line = rawLines[i].trim();
                if (!line) {
                    if (inList) {
                        processed.push(listType === 'ul' ? '</ul>' : '</ol>');
                        inList = false;
                        listType = null;
                    }
                    continue;
                }

                // Horizontal divider: --- or ***
                if (/^[-*_]{3,}$/.test(line)) {
                    if (inList) {
                        processed.push(listType === 'ul' ? '</ul>' : '</ol>');
                        inList = false;
                        listType = null;
                    }
                    processed.push('<hr class="my-3 border-slate-200/80">');
                    continue;
                }

                // Markdown headings: #, ##, ###
                const headingMatch = line.match(/^(#{1,4})\s+(.+)$/);
                if (headingMatch) {
                    if (inList) {
                        processed.push(listType === 'ul' ? '</ul>' : '</ol>');
                        inList = false;
                        listType = null;
                    }
                    processed.push(`<div class="font-semibold text-slate-900 text-sm mt-3 mb-1.5 flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-indigo-500 inline-block"></span>${headingMatch[2]}</div>`);
                    continue;
                }

                // Unordered list items: *, -, •
                const ulMatch = line.match(/^([*•\-])\s+(.+)$/);
                if (ulMatch) {
                    if (!inList || listType !== 'ul') {
                        if (inList) processed.push(listType === 'ul' ? '</ul>' : '</ol>');
                        processed.push('<ul class="list-disc pl-5 space-y-1.5 my-2 text-slate-700">');
                        inList = true;
                        listType = 'ul';
                    }
                    processed.push(`<li>${ulMatch[2]}</li>`);
                    continue;
                }

                // Ordered list items: 1., 2.
                const olMatch = line.match(/^(\d+)\.\s+(.+)$/);
                if (olMatch) {
                    if (!inList || listType !== 'ol') {
                        if (inList) processed.push(listType === 'ul' ? '</ul>' : '</ol>');
                        processed.push('<ol class="list-decimal pl-5 space-y-1.5 my-2 text-slate-700">');
                        inList = true;
                        listType = 'ol';
                    }
                    processed.push(`<li>${olMatch[2]}</li>`);
                    continue;
                }

                // Standard paragraph text
                if (inList) {
                    processed.push(listType === 'ul' ? '</ul>' : '</ol>');
                    inList = false;
                    listType = null;
                }
                processed.push(`<p class="leading-relaxed mb-2 last:mb-0">${line}</p>`);
            }

            if (inList) {
                processed.push(listType === 'ul' ? '</ul>' : '</ol>');
            }

            return processed.join('');
        }

        function getUserAvatarHtml() {
            const displayName = authenticatedUser?.name || (authenticatedUser?.first_name ? (authenticatedUser.first_name + " " + (authenticatedUser.last_name || "")) : "");
            if (displayName && displayName.trim()) {
                const parts = displayName.trim().split(/\s+/);
                let initials = "";
                if (parts.length >= 2) {
                    initials = (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
                } else {
                    initials = parts[0].substring(0, 2).toUpperCase();
                }
                return `
                    <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-violet-600 to-indigo-600 text-white flex items-center justify-center text-[11px] font-bold tracking-tight shadow-sm shrink-0 border border-white/80 select-none" title="${displayName.trim()}">
                        ${initials}
                    </div>
                `;
            }
            return `
                <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-slate-200 to-indigo-100 text-indigo-600 flex items-center justify-center shadow-xs shrink-0 border border-white/80 select-none" title="User">
                    <svg class="w-4 h-4 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
                    </svg>
                </div>
            `;
        }

        function appendMessage(sender, text, agentName = 'AI', requiresApproval = false, suggestedActions = []) {
            const isUser = sender === 'user';
            const timeStr = getFormattedTime();
            const div = document.createElement('div');
            div.className = `flex items-end space-x-2.5 ${isUser ? 'justify-end' : 'justify-start'} mb-3`;
            
            if (!isUser) {
                let approvalBadge = '';
                if (requiresApproval) {
                    approvalBadge = `
                        <div class="mt-2.5 p-2.5 bg-rose-50 border border-rose-200 rounded-lg text-rose-700 text-xs flex items-center space-x-1.5">
                            <span class="font-bold">🔒 Security Gate:</span>
                            <span>Action mutates physical locker hardware and requires verification.</span>
                        </div>
                    `;
                }

                div.innerHTML = `
                    <div class="w-8 h-8 rounded-full bg-white border border-indigo-100 shadow-xs flex items-center justify-center p-0.5 shrink-0 select-none relative">${botAvatarSvg}</div>
                    <div class="bg-white text-slate-800 px-4 py-3 rounded-[18px] rounded-bl-[4px] max-w-[82%] text-sm border border-slate-200/80 shadow-[0_2px_8px_rgba(0,0,0,0.03)] leading-relaxed">
                        <div class="flex items-center justify-between space-x-3 mb-1.5 pb-1 border-b border-slate-100/90">
                            <span class="text-[11px] font-bold uppercase tracking-wider text-indigo-600">${agentName} Assistant</span>
                            <span class="text-[11px] text-slate-400 font-medium">${timeStr}</span>
                        </div>
                        <div class="bot-text-body text-slate-700 text-sm leading-relaxed space-y-1">${formatMarkdown(text)}</div>
                        ${approvalBadge}
                    </div>
                `;
            } else {
                div.innerHTML = `
                    <div class="bg-gradient-to-r from-violet-600 via-indigo-600 to-indigo-700 text-white px-4 py-2.5 rounded-[18px] rounded-br-[4px] max-w-[80%] text-sm shadow-sm shadow-indigo-500/15 leading-relaxed">
                        <div class="break-words font-normal text-sm leading-relaxed">${text}</div>
                        <div class="flex items-center justify-end space-x-1.5 mt-1 text-[11px] text-indigo-200/90 font-medium select-none">
                            <span>${timeStr}</span>
                            <span class="user-tick-status inline-flex items-center">${singleTickSvg}</span>
                        </div>
                    </div>
                    ${getUserAvatarHtml()}
                `;
            }

            messagesContainer.appendChild(div);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            notifyParentHeight();

            // Render dynamic suggested actions if returned
            if (suggestedActions && suggestedActions.length > 0) {
                renderQuickReplies(suggestedActions);
            }
            return div;
        }

        // Live Real-Time Token Streaming Bubble
        let currentStreamDiv = null;
        let currentStreamBody = null;
        let currentStreamText = "";

        function createStreamingBubble(agentName = 'AI') {
            const timeStr = getFormattedTime();
            currentStreamText = "";
            const div = document.createElement('div');
            div.className = "flex items-end space-x-2.5 justify-start mb-3";
            div.innerHTML = `
                <div class="w-8 h-8 rounded-full bg-white border border-indigo-100 shadow-xs flex items-center justify-center p-0.5 shrink-0 select-none relative">${botAvatarSvg}</div>
                <div class="bg-white text-slate-800 px-4 py-3 rounded-[18px] rounded-bl-[4px] max-w-[82%] text-sm border border-slate-200/80 shadow-[0_2px_8px_rgba(0,0,0,0.03)] leading-relaxed">
                    <div class="flex items-center justify-between space-x-3 mb-1.5 pb-1 border-b border-slate-100/90">
                        <span class="text-[11px] font-bold uppercase tracking-wider text-indigo-600">${agentName} Assistant</span>
                        <span class="text-[11px] text-slate-400 font-medium">${timeStr}</span>
                    </div>
                    <div class="streaming-content text-slate-700 text-sm leading-relaxed space-y-1"></div>
                </div>
            `;
            messagesContainer.appendChild(div);
            currentStreamDiv = div;
            currentStreamBody = div.querySelector('.streaming-content');
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            notifyParentHeight();
            return div;
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
                const isLogin = act.toLowerCase().includes('log in') || act.toLowerCase().includes('login');
                btn.className = isLogin
                    ? "text-xs text-white bg-indigo-600 hover:bg-indigo-700 font-semibold py-2 px-3 rounded-xl transition text-center shadow-xs truncate"
                    : "text-xs text-indigo-600 bg-white hover:bg-indigo-50/80 border border-indigo-200/80 hover:border-indigo-300 font-medium py-2 px-3 rounded-xl transition text-center shadow-xs truncate";
                btn.innerText = (isLogin ? "🔑 " : "") + act;
                btn.onclick = () => {
                    if (isLogin) {
                        window.parent.postMessage({ type: 'open-login' }, '*');
                    }
                    sendQuickReply(act);
                };
                quickRepliesContainer.appendChild(btn);
            });
            messagesContainer.appendChild(quickRepliesContainer);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            notifyParentHeight();
        }

        let typingTimeout = null;

        function showTypingIndicator() {
            removeTypingIndicator();
            const typingDiv = document.createElement('div');
            typingDiv.id = 'typing-indicator';
            typingDiv.className = 'flex items-center space-x-2 text-slate-400 text-xs py-1 px-8';
            typingDiv.innerHTML = `
                <div class="flex space-x-1">
                    <span class="w-2 h-2 bg-indigo-500 rounded-full typing-dot"></span>
                    <span class="w-2 h-2 bg-indigo-500 rounded-full typing-dot"></span>
                    <span class="w-2 h-2 bg-indigo-500 rounded-full typing-dot"></span>
                </div>
                <span class="text-[11px] font-medium text-slate-400">Assistant is checking...</span>
            `;
            messagesContainer.appendChild(typingDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

            if (typingTimeout) clearTimeout(typingTimeout);
            typingTimeout = setTimeout(() => {
                if (document.getElementById('typing-indicator')) {
                    removeTypingIndicator();
                    appendMessage('bot', "I apologize, I'm taking a bit longer than expected to look that up. Please try again.", 'Concierge', false, ['Try again', 'Contact support']);
                }
            }, 30000);
        }

        function removeTypingIndicator() {
            if (typingTimeout) {
                clearTimeout(typingTimeout);
                typingTimeout = null;
            }
            const el = document.getElementById('typing-indicator');
            if (el) el.remove();
        }

        // ======================================================================
        // Real-Time WebSocket Implementation
        // ======================================================================
        let wsSocket = null;
        let wsConnected = false;
        let heartbeatTimer = null;

        function initWebSocket() {
            if (heartbeatTimer) clearInterval(heartbeatTimer);
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            let wsUrl = `${protocol}//${window.location.host}/api/v1/chat/ws/${sessionId}`;
            if (residentId) {
                wsUrl += `?resident_id=${encodeURIComponent(residentId)}`;
            }

            console.log("Connecting real-time chat socket to:", wsUrl);
            wsSocket = new WebSocket(wsUrl);

            wsSocket.onopen = () => {
                wsConnected = true;
                console.log("Real-time WebSocket connected!");
                // Keep-alive heartbeat ping every 25s
                heartbeatTimer = setInterval(() => {
                    if (wsSocket && wsSocket.readyState === WebSocket.OPEN) {
                        wsSocket.send("ping");
                    }
                }, 25000);
            };

            wsSocket.onmessage = (event) => {
                if (event.data === "pong") return;
                try {
                    const msg = JSON.parse(event.data);
                    handleIncomingSocketPayload(msg);
                } catch(e) {
                    console.error("Failed to parse WebSocket JSON payload:", e);
                }
            };

            wsSocket.onclose = () => {
                wsConnected = false;
                if (heartbeatTimer) clearInterval(heartbeatTimer);
                console.warn("WebSocket disconnected. Reconnecting in 3s...");
                setTimeout(initWebSocket, 3000);
            };

            wsSocket.onerror = (err) => {
                console.warn("WebSocket error occurred:", err);
            };
        }

        function handleIncomingSocketPayload(msg) {
            if (msg.type === "stream_token") {
                removeTypingIndicator();
                const agentName = msg.sender?.name || "AI";
                const tokenText = (typeof msg.content === 'object' && msg.content !== null) ? (msg.content.token || '') : (msg.content || '');
                if (!currentStreamDiv) {
                    createStreamingBubble(agentName);
                }
                currentStreamText += tokenText;
                if (currentStreamBody) {
                    currentStreamBody.innerHTML = formatMarkdown(currentStreamText);
                }
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            } else if (msg.type === "done" || msg.type === "agent_message" || msg.type === "agent_card") {
                removeTypingIndicator();
                markLastUserMessageDelivered();
                const textContent = (typeof msg.content === 'object' && msg.content !== null) ? (msg.content.text || '') : (msg.content || '');
                const agentName = msg.sender?.name || "AI";
                const requiresApproval = Boolean(msg.metadata?.requires_approval);
                const actions = (typeof msg.content === 'object' && msg.content !== null) ? msg.content.suggested_actions : null;

                if (currentStreamBody) {
                    if (textContent) {
                        currentStreamBody.innerHTML = formatMarkdown(textContent);
                    }
                } else if (textContent) {
                    appendMessage('bot', textContent, agentName, requiresApproval, actions);
                }
                if (actions) {
                    renderQuickReplies(actions);
                }
                currentStreamDiv = null;
                currentStreamBody = null;
                currentStreamText = "";
            } else if (msg.type === "error") {
                removeTypingIndicator();
                const errMsg = (typeof msg.content === 'object' && msg.content !== null) ? (msg.content.text || msg.content.message || "I encountered an issue processing that. Please try again.") : (msg.content || "I encountered an issue processing that. Please try again.");
                appendMessage('bot', errMsg, 'Support', false, ['Try again', 'Contact support']);
            }
        }

        async function executeQuery(messageText) {
            if (quickRepliesContainer) {
                quickRepliesContainer.innerHTML = '';
                quickRepliesContainer.style.display = 'none';
            }
            appendMessage('user', messageText);
            showTypingIndicator();

            if (wsConnected && wsSocket && wsSocket.readyState === WebSocket.OPEN) {
                // Send strictly via Standard Dynamic Message Envelope
                const standardEnvelope = {
                    message_id: "msg_" + Math.random().toString(36).substring(2, 11),
                    conversation_id: sessionId,
                    type: "user_message",
                    sender: {
                        role: "user",
                        name: authenticatedUser?.name || (residentId ? ("Resident " + residentId) : "Guest"),
                        id: residentId || authenticatedUser?.user_id || "guest"
                    },
                    content: {
                        text: messageText,
                        attachments: []
                    },
                    metadata: {
                        locale: navigator.language || "en-US",
                        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
                        client: "webchat",
                        token: chatSessionToken || undefined,
                        parent_token: (authenticatedUser && authenticatedUser.parent_token) ? authenticatedUser.parent_token : undefined,
                    },
                    created_at: new Date().toISOString()
                };
                wsSocket.send(JSON.stringify(standardEnvelope));
            } else {
                // HTTP REST Fallback
                try {
                    const reqHeaders = { 'Content-Type': 'application/json' };
                    if (chatSessionToken) {
                        reqHeaders['Authorization'] = 'Bearer ' + chatSessionToken;
                    }
                    const response = await fetch('/api/v1/chat', {
                        method: 'POST',
                        headers: reqHeaders,
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
                    appendMessage('bot', "I apologize, I'm taking a bit longer than expected to look that up. Please try again.", 'Concierge', false, ['Try again', 'Contact support']);
                }
            }
        }

        function sendQuickReply(text) {
            executeQuery(text);
        }
        window.sendQuickReply = sendQuickReply;
        window.executeQuery = executeQuery;

        function startNewChat() {
            if (confirm("Start a new conversation? Previous messages will be cleared.")) {
                localStorage.removeItem(STORAGE_KEY);
                window.location.reload();
            }
        }
        window.startNewChat = startNewChat;

        function handleSend() {
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            executeQuery(text);
        }

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            handleSend();
        });

        sendBtn.addEventListener('click', (e) => {
            e.preventDefault();
            handleSend();
        });

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleSend();
            }
        });

        // Initialize immediately
        notifyParentHeight();
        initWebSocket();
        if (authenticatedUser || chatSessionToken) {
            setAuthenticatedMascotState(true, authenticatedUser);
        }
        window.addEventListener('load', notifyParentHeight);
        try {
            window.parent.postMessage({ type: 'chatbot-ready' }, '*');
        } catch(e) {}
    </script>
</body>
</html>
"""
    # Inject configurable values into the HTML template
    rendered_html = (
        html_content
        .replace("__WELCOME_TITLE__", active_title)
        .replace("__WELCOME_MESSAGE__", active_msg)
        .replace("__SUBTITLE__", active_subtitle)
        .replace("__ASSISTANT_NAME__", active_name).replace("__BOT_SVG__", BOT_MASCOT_SVG)
    )
    return HTMLResponse(content=rendered_html)


@router.get("/demo", response_class=HTMLResponse, summary="Live Iframe Host Demonstration Page")
async def host_demo_page():
    """Renders a sample host webpage demonstrating seamless iframe embedding and postMessage integration."""
    html_content = r"""<!DOCTYPE html>
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
