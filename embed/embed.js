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
    fab.innerHTML = '💬';

    let isOpen = false;

    function toggleChatbot() {
        isOpen = !isOpen;
        iframeCard.style.display = isOpen ? 'block' : 'none';
        fab.innerHTML = isOpen ? '✕' : '💬';
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
