const isAdmin = true; // ← 如果要一般使用者版改 false

const adminUser = { id: 'admin', name: 'Admin（管理者）', avatar: 'A' };
const users = [
  { id: 'u01', name: '陳廷軒', status: 'A13 剛結束', avatar: '廷' },
  { id: 'u02', name: '李冠彣', status: '休息中', avatar: '冠' },
  { id: 'u03', name: '吳柏丞', status: '行車中', avatar: '柏' }
];

const conversations = new Map();
function ensureConv(targetId) {
  if (!conversations.has(targetId)) conversations.set(targetId, []);
}

const peopleEl = document.getElementById('people');
const chatTitle = document.getElementById('chatTitle');
const chatSub = document.getElementById('chatSub');
const chatAvatar = document.getElementById('chatAvatar');
const msgsEl = document.getElementById('msgs');
const composer = document.getElementById('composer');
const sendBtn = document.getElementById('sendBtn');
const searchEl = document.getElementById('search');
const peoplePanel = document.getElementById('peoplePanel');
const toggleList = document.getElementById('toggleList');
const roleBadge = document.getElementById('roleBadge');

let currentTarget = null;

function setupRoleView() {
  if (isAdmin) {
    roleBadge.textContent = 'ADMIN';
    renderPeople(users);
  } else {
    roleBadge.textContent = 'USER';
    document.querySelector('.layout').style.gridTemplateColumns = '1fr';
    peoplePanel.style.display = 'none';
    selectTarget(adminUser);
  }
}

function renderPeople(list) {
  peopleEl.innerHTML = '';
  list.forEach(u => {
    const row = document.createElement('div');
    row.className = 'person';
    row.dataset.id = u.id;
    row.innerHTML = `<div class="avatar">${u.avatar}</div>
                     <div class="meta">
                       <div class="name">${u.name}</div>
                       <div class="sub">${u.status || ''}</div>
                     </div>`;
    row.addEventListener('click', () => selectTarget(u));
    peopleEl.appendChild(row);
  });
}

function selectTarget(user) {
  currentTarget = user.id;
  document.querySelectorAll('.person').forEach(p => p.classList.toggle('active', p.dataset.id === user.id));
  chatTitle.textContent = user.name;
  chatSub.textContent = '立即回覆 · 安全守護中';
  chatAvatar.textContent = (user.avatar || '?').toString().slice(0, 2);
  ensureConv(currentTarget);
  renderMessages();
  composer.focus();
}

function renderMessages() {
  const items = conversations.get(currentTarget) || [];
  msgsEl.innerHTML = '';
  items.forEach(m => {
    const b = document.createElement('div');
    b.className = 'msg ' + (m.me ? 'me' : 'you');
    b.innerHTML = `${escapeHtml(m.text)}<span class="time">${m.time}</span>`;
    msgsEl.appendChild(b);
  });
  msgsEl.parentElement.scrollTop = msgsEl.parentElement.scrollHeight;
}

function send() {
  const text = composer.value.trim();
  if (!text || !currentTarget) return;
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  ensureConv(currentTarget);
  conversations.get(currentTarget).push({ me: true, text, time });
  composer.value = '';
  renderMessages();
  setTimeout(() => {
    conversations.get(currentTarget).push({ me: false, text: '收到：' + text, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) });
    renderMessages();
  }, 600);
}

searchEl?.addEventListener('input', e => {
  const q = e.target.value.toLowerCase();
  renderPeople(users.filter(u => (u.name + u.status).toLowerCase().includes(q)));
});

toggleList.addEventListener('click', () => {
  if (peoplePanel.style.display === 'none') {
    peoplePanel.style.display = 'flex';
    document.querySelector('.layout').style.gridTemplateColumns = '1fr 320px';
  } else {
    peoplePanel.style.display = 'none';
    document.querySelector('.layout').style.gridTemplateColumns = '1fr';
  }
});

sendBtn.addEventListener('click', send);
composer.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
});

function escapeHtml(str) {
  return str.replace(/[&<>\"']/g, s => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[s]));
}

setupRoleView();
if (isAdmin) selectTarget(users[0]);

const layout = document.querySelector('.layout');
toggleList.addEventListener('click', () => {
  layout.classList.toggle('show-list');
});
