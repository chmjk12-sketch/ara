// ARA - Adaptive Reality Agent Frontend

const API_BASE = '/api/v1';

let conversationId = null;
let isSending = false;
let currentDepth = null;
let lastResponse = null;
let lastMeta = null;

// Depth level display config
const DEPTH_DISPLAY = {
    Level0: { label: 'Level 0', desc: '快速回答', color: '#22c55e' },
    Level1: { label: 'Level 1', desc: '标准分析', color: '#6366f1' },
    Level2: { label: 'Level 2', desc: '深入分析', color: '#f59e0b' },
    Level3: { label: 'Level 3', desc: '完整报告', color: '#ef4444' },
};

// Action button config
const ACTIONS = [
    {
        id: 'expand',
        label: '展开',
        icon: '↕',
        message: '展开',
        targetLevel: 1,
        levelClass: '',
        minDepthUpgrade: 0,
    },
    {
        id: 'deep',
        label: '详细分析',
        icon: '→',
        message: '详细分析',
        targetLevel: 2,
        levelClass: 'level-2',
        minDepthUpgrade: 1,
    },
    {
        id: 'report',
        label: '完整报告',
        icon: '◆',
        message: '完整报告',
        targetLevel: 3,
        levelClass: 'level-3',
        minDepthUpgrade: 2,
    },
];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('userInput').focus();
});

// Fill question from hint cards
function fillQuestion(text) {
    document.getElementById('userInput').value = text;
    document.getElementById('userInput').focus();
    autoResize(document.getElementById('userInput'));
}

// New chat
function newChat() {
    conversationId = null;
    currentDepth = null;
    lastResponse = null;
    lastMeta = null;
    document.getElementById('messages').innerHTML = '';
    document.getElementById('welcome').style.display = 'flex';
    document.getElementById('depthBar').style.display = 'none';
    document.getElementById('userInput').value = '';
    document.getElementById('userInput').focus();
}

// Handle keyboard
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Auto resize textarea
function autoResize(el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

// Send an action button command
async function sendAction(actionMessage) {
    if (isSending) return;
    document.getElementById('welcome').style.display = 'none';
    addMessage('user', actionMessage);
    const typingEl = showTyping();
    isSending = true;
    document.getElementById('btnSend').disabled = true;

    try {
        const data = await fetchWithTimeout(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: actionMessage, conversation_id: conversationId }),
        }, 180000);

        if (data.code === 0) {
            conversationId = data.data.conversation_id;
            lastResponse = data.data.response;
            lastMeta = { intent: data.data.intent, depth: data.data.depth, confidence: data.data.intent_confidence, wordRange: data.data.word_range };
            typingEl.remove();
            addMessage('assistant', data.data.response, lastMeta);
            updateDepthBar(data.data);
        } else {
            typingEl.remove();
            addMessage('assistant', `抱歉，${data.message || '处理请求时出现错误'}。请稍后重试。`);
        }
    } catch (error) {
        typingEl.remove();
        if (error.name === 'AbortError' || error.name === 'TimeoutError') {
            addMessage('assistant', '响应超时，AI 正在思考中。请稍后重试，或尝试简化问题。');
        } else {
            addMessage('assistant', '网络错误，请检查连接后重试。');
        }
    } finally {
        isSending = false;
        document.getElementById('btnSend').disabled = false;
        document.getElementById('userInput').focus();
    }
}

// Send message from input
async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    if (!message || isSending) return;

    isSending = true;
    input.value = '';
    autoResize(input);
    document.getElementById('btnSend').disabled = true;

    document.getElementById('welcome').style.display = 'none';
    addMessage('user', message);
    const typingEl = showTyping();

    try {
        const data = await fetchWithTimeout(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message, conversation_id: conversationId }),
        }, 180000);

        if (data.code === 0) {
            conversationId = data.data.conversation_id;
            lastResponse = data.data.response;
            lastMeta = { intent: data.data.intent, depth: data.data.depth, confidence: data.data.intent_confidence, wordRange: data.data.word_range };
            typingEl.remove();
            addMessage('assistant', data.data.response, lastMeta);
            updateDepthBar(data.data);
        } else {
            typingEl.remove();
            addMessage('assistant', `抱歉，${data.message || '处理请求时出现错误'}。请稍后重试。`);
        }
    } catch (error) {
        typingEl.remove();
        if (error.name === 'AbortError' || error.name === 'TimeoutError') {
            addMessage('assistant', '响应超时，AI 正在思考中。请稍后重试，或尝试简化问题。');
        } else {
            addMessage('assistant', '网络错误，请检查连接后重试。');
        }
    } finally {
        isSending = false;
        document.getElementById('btnSend').disabled = false;
        document.getElementById('userInput').focus();
    }
}

// Export to PDF
async function exportPdf() {
    if (!lastResponse) {
        alert('请先进行一次对话，生成分析内容后再导出 PDF');
        return;
    }
    const title = prompt('请输入报告标题:', 'ARA分析报告');
    if (!title) return;

    const btn = document.getElementById('btnExportPdf');
    if (btn) btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/export/pdf`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: title,
                content: lastResponse,
                intent: lastMeta?.intent || 'Reality',
                depth: lastMeta?.depth || 'Level1',
                word_range: lastMeta?.wordRange || '300~800字',
            }),
        });

        if (!response.ok) {
            const err = await response.json();
            alert('PDF 导出失败: ' + (err.message || '未知错误'));
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${title.replace(/\s+/g, '_').slice(0, 30)}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (e) {
        alert('PDF 导出失败: ' + e.message);
    } finally {
        if (btn) btn.disabled = false;
    }
}

// Save to Notion
async function saveToNotion() {
    if (!lastResponse) {
        alert('请先进行一次对话，生成分析内容后再保存到 Notion');
        return;
    }
    const title = prompt('请输入 Notion 页面标题:', 'ARA分析报告');
    if (!title) return;

    const btn = document.getElementById('btnSaveNotion');
    if (btn) {
        btn.disabled = true;
        btn.textContent = '保存中...';
    }

    try {
        const response = await fetch(`${API_BASE}/export/notion`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: title,
                content: lastResponse,
            }),
        });

        const data = await response.json();
        if (data.code === 0 && data.data?.notion_url) {
            if (confirm('已保存到 Notion！是否打开页面？')) {
                window.open(data.data.notion_url, '_blank');
            }
        } else {
            alert('Notion 保存失败: ' + (data.message || data.data?.error || '未知错误'));
        }
    } catch (e) {
        alert('Notion 保存失败: ' + e.message);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.textContent = '📝 Notion';
        }
    }
}

// Fetch with timeout
async function fetchWithTimeout(url, options, timeout = 60000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, { ...options, signal: controller.signal });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } finally {
        clearTimeout(timeoutId);
    }
}

// Add message to chat
function addMessage(role, content, meta = null) {
    const messagesEl = document.getElementById('messages');
    const messageEl = document.createElement('div');
    messageEl.className = `message ${role}`;

    let headerHTML = `<span class="message-role">${role === 'user' ? '你' : 'ARA'}</span>`;
    if (meta && role === 'assistant') {
        headerHTML += `
            <div class="message-meta">
                <span class="message-badge badge-intent">${meta.intent}</span>
                <span class="message-badge badge-depth">${meta.depth}</span>
            </div>
        `;
    }

    let formattedContent = content
        .replace(/【([^】]+)】/g, '<strong style="color: var(--accent-light); display: block; margin-top: 12px; margin-bottom: 4px; font-size: 14px;">$1</strong>')
        .replace(/---/g, '')
        .replace(/\n/g, '<br>');

    messageEl.innerHTML = `
        <div class="message-header">${headerHTML}</div>
        <div class="message-content">${formattedContent}</div>
    `;
    messagesEl.appendChild(messageEl);

    // Add action buttons for assistant responses
    if (role === 'assistant' && meta) {
        const actionsEl = document.createElement('div');
        actionsEl.className = 'message-actions';
        const depthNum = parseInt((meta.depth || 'Level1').replace('Level', ''));

        ACTIONS.forEach(action => {
            const btn = document.createElement('button');
            btn.className = `btn-action ${action.levelClass}`;
            btn.innerHTML = `<span class="action-icon">${action.icon}</span><span class="action-label">${action.label}</span>`;
            btn.disabled = depthNum >= action.targetLevel || isSending;
            btn.onclick = () => sendAction(action.message);
            actionsEl.appendChild(btn);
        });

        // Export buttons
        const exportPdfBtn = document.createElement('button');
        exportPdfBtn.className = 'btn-action';
        exportPdfBtn.id = 'btnExportPdf';
        exportPdfBtn.innerHTML = '<span class="action-icon">📄</span><span class="action-label">PDF</span>';
        exportPdfBtn.disabled = isSending;
        exportPdfBtn.onclick = exportPdf;
        actionsEl.appendChild(exportPdfBtn);

        const notionBtn = document.createElement('button');
        notionBtn.className = 'btn-action';
        notionBtn.id = 'btnSaveNotion';
        notionBtn.innerHTML = '<span class="action-icon">📝</span><span class="action-label">Notion</span>';
        notionBtn.disabled = isSending;
        notionBtn.onclick = saveToNotion;
        actionsEl.appendChild(notionBtn);

        messagesEl.appendChild(actionsEl);
    }

    scrollToBottom();
}

// Show typing indicator
function showTyping() {
    const messagesEl = document.getElementById('messages');
    const typingEl = document.createElement('div');
    typingEl.className = 'message assistant';
    typingEl.innerHTML = `
        <div class="message-header"><span class="message-role">ARA</span></div>
        <div class="typing">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    messagesEl.appendChild(typingEl);
    scrollToBottom();
    return typingEl;
}

// Update depth bar
function updateDepthBar(data) {
    const bar = document.getElementById('depthBar');
    bar.style.display = 'flex';
    const depthInfo = DEPTH_DISPLAY[data.depth] || DEPTH_DISPLAY.Level1;
    currentDepth = data.depth;

    document.getElementById('depthLabel').textContent = depthInfo.label;
    document.getElementById('depthLabel').style.color = depthInfo.color;
    document.getElementById('depthDesc').textContent = depthInfo.desc;
    document.getElementById('intentLabel').textContent = data.intent;
    document.getElementById('wordRange').textContent = data.wordRange;

    const dots = document.querySelectorAll('.depth-dot');
    const level = parseInt(data.depth.replace('Level', ''));
    dots.forEach((dot, i) => {
        dot.className = 'depth-dot';
        if (i < level) dot.classList.add('passed');
        if (i === level) dot.classList.add('active');
    });
}

// Scroll to bottom
function scrollToBottom() {
    const chatArea = document.getElementById('chatArea');
    requestAnimationFrame(() => { chatArea.scrollTop = chatArea.scrollHeight; });
}
