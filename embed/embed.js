/**
 * Smiota AI Chatbot - Universal Embed Script
 * Usage: <script src="https://your-domain.com/embed/embed.js" data-server="http://localhost:8000"></script>
 */
(function () {
    const currentScript = document.currentScript;
    const serverUrl = currentScript?.getAttribute('data-server') || 'http://localhost:8000';

    // Create container
    const container = document.createElement('div');
    container.id = 'smiota-chatbot-root';
    container.style.position = 'fixed';
    container.style.bottom = '24px';
    container.style.right = '24px';
    container.style.zIndex = '999999';
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.alignItems = 'flex-end';

    // Create iframe card
    const iframeCard = document.createElement('div');
    iframeCard.id = 'smiota-chatbot-frame-card';
    iframeCard.style.width = '380px';
    iframeCard.style.height = '580px';
    iframeCard.style.marginBottom = '16px';
    iframeCard.style.borderRadius = '16px';
    iframeCard.style.overflow = 'hidden';
    iframeCard.style.boxShadow = '0 20px 40px rgba(0,0,0,0.25)';
    iframeCard.style.border = '1px solid rgba(255,255,255,0.1)';
    iframeCard.style.display = 'none';

    const iframe = document.createElement('iframe');
    iframe.src = `${serverUrl}/api/v1/channels/webchat/embed`;
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.style.border = 'none';
    iframe.allow = 'clipboard-write';

    iframeCard.appendChild(iframe);

    // Floating action button
    const fab = document.createElement('button');
    fab.id = 'smiota-chatbot-toggle';
    fab.style.width = '56px';
    fab.style.height = '56px';
    fab.style.borderRadius = '50%';
    fab.style.background = 'linear-gradient(135deg, #7C3AED, #4F46E5)';
    fab.style.color = '#FFFFFF';
    fab.style.border = 'none';
    fab.style.boxShadow = '0 10px 25px rgba(79, 70, 229, 0.4)';
    fab.style.cursor = 'pointer';
    fab.style.display = 'flex';
    fab.style.alignItems = 'center';
    fab.style.justifyContent = 'center';
    fab.style.transition = 'transform 0.2s';
    const chatIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="28" height="28" style="pointer-events:none;"><path fill-rule="evenodd" d="M4.804 21.644A6.707 6.707 0 0 0 6 21.75a6.721 6.721 0 0 0 3.583-1.029c.774.182 1.584.279 2.417.279 5.322 0 9.75-3.97 9.75-9 0-5.03-4.428-9-9.75-9s-9.75 3.97-9.75 9c0 2.409 1.025 4.587 2.674 6.192.232.226.277.428.254.543a3.73 3.73 0 0 1-.814 1.686.75.75 0 0 0 .44 1.223ZM8.25 10.875a1.125 1.125 0 1 0 0 2.25 1.125 1.125 0 0 0 0-2.25ZM10.875 12a1.125 1.125 0 1 1 2.25 0 1.125 1.125 0 0 1-2.25 0Zm4.875-1.125a1.125 1.125 0 1 0 0 2.25 1.125 1.125 0 0 0 0-2.25Z" clip-rule="evenodd" /></svg>`;
    const closeIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="24" height="24" style="pointer-events:none;"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`;
    fab.innerHTML = chatIconSvg;

    let isOpen = false;

    function toggleChatbot() {
        isOpen = !isOpen;
        iframeCard.style.display = isOpen ? 'block' : 'none';
        fab.innerHTML = isOpen ? closeIconSvg : chatIconSvg;
    }

    fab.addEventListener('click', toggleChatbot);

    window.addEventListener('message', (event) => {
        if (!event.data) return;
        if (event.data.type === 'close-chatbot' || event.data.type === 'minimize-chatbot') {
            if (isOpen) toggleChatbot();
        }
    });

    container.appendChild(iframeCard);
    container.appendChild(fab);
    document.body.appendChild(container);
})();
