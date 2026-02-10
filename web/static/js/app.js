/* ============================================
   CRM de Relacionamentos - Frontend App
   ============================================ */

// --- State ---
let currentPage = 'dashboard';
let currentAgent = 'advisor';
let chatHistory = [];

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
  loadProfile();
  loadDashboard();
});

// --- Navigation ---
function showPage(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  const el = document.getElementById(`page-${page}`);
  if (el) el.classList.remove('hidden');

  const nav = document.querySelector(`.nav-item[data-page="${page}"]`);
  if (nav) nav.classList.add('active');

  currentPage = page;

  // Load data per page
  if (page === 'dashboard') loadDashboard();
  else if (page === 'contacts') loadContacts();
  else if (page === 'scores') loadScores();
  else if (page === 'network') loadNetwork();
  else if (page === 'settings') loadSettings();
}

// --- API helpers ---
async function api(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  return res.json();
}

function toast(msg, isError = false) {
  const el = document.createElement('div');
  el.className = `toast${isError ? ' toast-error' : ''}`;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

function catLabel(cat) {
  const map = {
    familia: 'Familia', amigo_proximo: 'Amigo', colega_trabalho: 'Colega',
    cliente: 'Cliente', fornecedor: 'Fornecedor', parceiro: 'Parceiro',
    mentor: 'Mentor', mentorado: 'Mentorado', networking: 'Networking',
    governo: 'Governo', investidor: 'Investidor', paciente: 'Paciente',
    referencia_medica: 'Ref. Medica', outro: 'Outro',
  };
  return map[cat] || cat;
}

function initials(name) {
  return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase();
}

function forcaClass(forca) {
  return `score-${forca}`;
}

function priorityClass(p) {
  return `priority-${p}`;
}

function urgencyClass(u) {
  return `urgency-${u}`;
}

function formatDate(d) {
  if (!d) return '--';
  return d.slice(0, 10);
}

function typeLabel(tipo) {
  const map = {
    mensagem: 'Mensagem', ligacao: 'Ligacao', reuniao: 'Reuniao',
    email: 'Email', encontro_presencial: 'Presencial', rede_social: 'Rede social',
    evento: 'Evento', favor_feito: 'Favor feito', favor_recebido: 'Favor recebido',
    indicacao: 'Indicacao', presente: 'Presente', outro: 'Outro',
  };
  return map[tipo] || tipo;
}

function sentimentEmoji(s) {
  return s === 'positivo' ? '+' : s === 'negativo' ? '-' : '~';
}

// --- Profile ---
async function loadProfile() {
  const data = await api('/profile');
  if (data.profile && data.profile.nome) {
    document.getElementById('profileName').textContent = data.profile.nome;
    document.getElementById('profileType').textContent = catLabel(data.profile.tipo) || data.profile.tipo;
    document.getElementById('profileAvatar').textContent = initials(data.profile.nome);
  }
}

// --- Dashboard ---
async function loadDashboard() {
  try {
    const data = await api('/dashboard');

    document.getElementById('mContatos').textContent = data.stats.total_contatos || 0;
    document.getElementById('mInteracoes').textContent = data.stats.total_interacoes || 0;
    document.getElementById('mScore').textContent = data.scores.score_medio || '--';
    document.getElementById('mAlertas').textContent = data.scores.total_alertas || 0;

    // Suggestions
    const sugEl = document.getElementById('dashSuggestions');
    const suggestions = data.suggestions || [];
    if (suggestions.length === 0) {
      sugEl.innerHTML = '<div class="empty-state"><p>Nenhuma sugestao no momento. Seus relacionamentos estao em dia!</p></div>';
    } else {
      sugEl.innerHTML = suggestions.map(s => `
        <div class="suggestion-item">
          <div class="suggestion-urgency ${urgencyClass(s.urgencia)}"></div>
          <div class="suggestion-body">
            <h4>${s.contato_nome}</h4>
            <p>${s.motivo}</p>
          </div>
          <span class="badge ${priorityClass(s.urgencia)}">${s.urgencia}</span>
        </div>
      `).join('');
    }

    // Activity
    const actEl = document.getElementById('dashActivity');
    const actData = await api('/interactions/recent?limit=5');
    const ints = actData.interactions || [];
    if (ints.length === 0) {
      actEl.innerHTML = '<div class="empty-state"><p>Nenhuma interacao registrada ainda.</p></div>';
    } else {
      actEl.innerHTML = ints.map(i => `
        <div class="suggestion-item">
          <div class="contact-avatar cat-${i.contato_id ? 'outro' : 'outro'}" style="width:36px;height:36px;font-size:12px">${sentimentEmoji(i.sentimento)}</div>
          <div class="suggestion-body">
            <h4>${i.contato_nome || 'Contato'} &middot; ${typeLabel(i.tipo)}</h4>
            <p>${i.descricao}</p>
          </div>
          <span style="font-size:11px;color:var(--text-muted);white-space:nowrap">${formatDate(i.data)}</span>
        </div>
      `).join('');
    }

    // Scores mini-table
    const scEl = document.getElementById('dashScoresTable');
    const scores = (data.scores.scores || []).slice(0, 8);
    if (scores.length === 0) {
      scEl.innerHTML = '<div class="empty-state"><p>Adicione contatos e interacoes para ver scores.</p></div>';
    } else {
      scEl.innerHTML = `
        <table>
          <thead><tr><th>Contato</th><th>Categoria</th><th>Score</th><th>Forca</th><th>Sem contato</th><th>Tendencia</th></tr></thead>
          <tbody>${scores.map(s => `
            <tr style="cursor:pointer" onclick="openContactDetail('${s.contato_id}')">
              <td><div class="contact-row"><div class="contact-avatar cat-${s.categoria}" style="width:32px;height:32px;font-size:12px">${initials(s.contato_nome)}</div><span style="font-weight:600">${s.contato_nome}</span></div></td>
              <td><span class="badge cat-${s.categoria}">${catLabel(s.categoria)}</span></td>
              <td><div class="score-ring ${forcaClass(s.forca)}" style="width:40px;height:40px;font-size:14px">${s.score}</div></td>
              <td><span class="badge ${forcaClass(s.forca)}">${s.forca}</span></td>
              <td>${s.dias_sem_contato === 999 ? 'Nunca' : s.dias_sem_contato + 'd'}</td>
              <td style="color:${s.tendencia === 'melhorando' ? 'var(--green)' : s.tendencia === 'piorando' ? 'var(--red)' : 'var(--text-muted)'}">${s.tendencia}</td>
            </tr>
          `).join('')}</tbody>
        </table>
      `;
    }
  } catch (e) {
    console.error('Dashboard error:', e);
  }
}

// --- Contacts ---
async function loadContacts() {
  const name = document.getElementById('searchName')?.value || '';
  const cat = document.getElementById('searchCategory')?.value || '';
  const params = new URLSearchParams();
  if (name) params.set('nome', name);
  if (cat) params.set('categoria', cat);

  const data = await api(`/contacts?${params}`);
  const contacts = data.contacts || [];
  const el = document.getElementById('contactsTable');

  if (contacts.length === 0) {
    el.innerHTML = '<div class="empty-state"><h3>Nenhum contato encontrado</h3><p>Adicione seu primeiro contato clicando no botao acima.</p></div>';
    return;
  }

  el.innerHTML = `
    <table>
      <thead><tr><th>Nome</th><th>Categoria</th><th>Empresa</th><th>Cidade</th><th>Interacoes</th><th>Ultimo contato</th><th></th></tr></thead>
      <tbody>${contacts.map(c => `
        <tr style="cursor:pointer" onclick="openContactDetail('${c.id}')">
          <td><div class="contact-row"><div class="contact-avatar cat-${c.categoria}" style="width:36px;height:36px;font-size:13px">${initials(c.nome)}</div><div class="contact-info"><h4>${c.nome}</h4><p>${c.cargo || ''}</p></div></div></td>
          <td><span class="badge cat-${c.categoria}">${catLabel(c.categoria)}</span></td>
          <td>${c.empresa || '--'}</td>
          <td>${c.cidade || '--'}</td>
          <td>${c.total_interacoes || 0}</td>
          <td>${c.ultima_interacao || 'Nunca'}</td>
          <td><button class="btn btn-ghost btn-sm" onclick="event.stopPropagation();openInteractionModal('${c.id}','${c.nome}')">+ Interacao</button></td>
        </tr>
      `).join('')}</tbody>
    </table>
  `;
}

let _searchTimeout;
function searchContacts() {
  clearTimeout(_searchTimeout);
  _searchTimeout = setTimeout(loadContacts, 300);
}

// --- Contact Detail ---
async function openContactDetail(id) {
  showPage('contact-detail');
  // Deactivate nav items since detail isn't in nav
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelector('.nav-item[data-page="contacts"]')?.classList.add('active');

  const el = document.getElementById('contactDetailContent');
  el.innerHTML = '<div class="empty-state"><div class="loading-spinner"></div><p>Carregando...</p></div>';

  const data = await api(`/contacts/${id}`);
  if (data.error) {
    el.innerHTML = `<div class="empty-state"><p>${data.error}</p></div>`;
    return;
  }

  const c = data.contact;
  const score = data.score || {};
  const interactions = data.interactions || [];

  el.innerHTML = `
    <div class="detail-header">
      <div class="detail-avatar cat-${c.categoria}" style="font-size:24px">${initials(c.nome)}</div>
      <div class="detail-info">
        <h2>${c.nome}${c.apelido ? ` (${c.apelido})` : ''}</h2>
        <div class="detail-meta">
          <span class="badge cat-${c.categoria}">${catLabel(c.categoria)}</span>
          ${c.empresa ? `<span>${c.cargo ? c.cargo + ' @ ' : ''}${c.empresa}</span>` : ''}
          ${c.cidade ? `<span>${c.cidade}</span>` : ''}
          ${c.email ? `<span>${c.email}</span>` : ''}
          ${c.telefone ? `<span>${c.telefone}</span>` : ''}
        </div>
      </div>
    </div>

    <div class="detail-stats">
      <div class="metric-card">
        <div class="metric-label">Score</div>
        <div class="metric-value" style="color:${score.forca === 'forte' ? 'var(--green)' : score.forca === 'moderado' ? 'var(--yellow)' : 'var(--red)'}">${score.score || '--'}</div>
        <div class="metric-sub">${score.forca || '--'}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Sem Contato</div>
        <div class="metric-value">${score.dias_sem_contato === 999 ? 'N/A' : (score.dias_sem_contato || 0)}</div>
        <div class="metric-sub">dias</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Interacoes</div>
        <div class="metric-value">${score.total_interacoes || 0}</div>
        <div class="metric-sub">${score.interacoes_ultimo_mes || 0} no ultimo mes</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Tendencia</div>
        <div class="metric-value" style="font-size:20px;color:${score.tendencia === 'melhorando' ? 'var(--green)' : score.tendencia === 'piorando' ? 'var(--red)' : 'var(--text-muted)'}">${score.tendencia || '--'}</div>
        <div class="metric-sub">sentimento: ${score.sentimento_medio || '--'}</div>
      </div>
    </div>

    ${score.alerta ? `<div class="card" style="border-color:var(--orange);margin-bottom:24px;padding:16px"><strong style="color:var(--orange)">Alerta:</strong> ${score.alerta}</div>` : ''}
    ${score.sugestao ? `<div class="card" style="border-color:var(--accent);margin-bottom:24px;padding:16px"><strong style="color:var(--accent)">Sugestao:</strong> ${score.sugestao}</div>` : ''}

    ${c.notas ? `<div class="card" style="margin-bottom:24px"><div class="card-header"><span class="card-title">Notas</span></div><p style="font-size:14px;color:var(--text-secondary)">${c.notas}</p></div>` : ''}
    ${c.como_conheceu ? `<p style="font-size:13px;color:var(--text-muted);margin-bottom:16px">Como conheceu: ${c.como_conheceu}</p>` : ''}

    <div class="section">
      <div class="section-header">
        <span class="section-title">Historico de Interacoes (${interactions.length})</span>
        <button class="btn btn-primary btn-sm" onclick="openInteractionModal('${c.id}','${c.nome}')">+ Interacao</button>
      </div>
      <div class="card">
        ${interactions.length === 0 ? '<div class="empty-state"><p>Nenhuma interacao registrada</p></div>' : `
          <table>
            <thead><tr><th>Data</th><th>Tipo</th><th>Descricao</th><th>Sentimento</th><th>Follow-up</th></tr></thead>
            <tbody>${interactions.map(i => `
              <tr>
                <td style="white-space:nowrap">${formatDate(i.data)}</td>
                <td><span class="badge badge-blue">${typeLabel(i.tipo)}</span></td>
                <td>${i.descricao}</td>
                <td><span class="badge ${i.sentimento === 'positivo' ? 'badge-green' : i.sentimento === 'negativo' ? 'badge-red' : 'badge-purple'}">${i.sentimento || 'neutro'}</span></td>
                <td>${i.follow_up_necessario ? `<span class="badge badge-orange">${i.follow_up_descricao || 'Pendente'}</span>` : '--'}</td>
              </tr>
            `).join('')}</tbody>
          </table>
        `}
      </div>
    </div>

    <div style="margin-top:16px">
      <button class="btn btn-danger btn-sm" onclick="deleteContactConfirm('${c.id}','${c.nome}')">Remover contato</button>
    </div>
  `;
}

async function deleteContactConfirm(id, name) {
  if (!confirm(`Deseja remover o contato "${name}"?`)) return;
  await api(`/contacts/${id}`, { method: 'DELETE' });
  toast('Contato removido');
  showPage('contacts');
}

// --- Scores ---
async function loadScores() {
  const data = await api('/scores');
  const el = document.getElementById('scoresFullTable');
  const scores = data.scores || [];

  if (scores.length === 0) {
    el.innerHTML = '<div class="empty-state"><h3>Sem dados</h3><p>Adicione contatos e interacoes para ver scores.</p></div>';
    return;
  }

  el.innerHTML = `
    <table>
      <thead><tr><th>Contato</th><th>Categoria</th><th>Score</th><th>Forca</th><th>Prioridade</th><th>Sem contato</th><th>Mes atual</th><th>Tendencia</th><th>Alerta</th></tr></thead>
      <tbody>${scores.map(s => `
        <tr style="cursor:pointer" onclick="openContactDetail('${s.contato_id}')">
          <td><div class="contact-row"><div class="contact-avatar cat-${s.categoria}" style="width:32px;height:32px;font-size:12px">${initials(s.contato_nome)}</div><span style="font-weight:600">${s.contato_nome}</span></div></td>
          <td><span class="badge cat-${s.categoria}">${catLabel(s.categoria)}</span></td>
          <td><div class="score-ring ${forcaClass(s.forca)}" style="width:40px;height:40px;font-size:14px">${s.score}</div></td>
          <td><span class="badge ${forcaClass(s.forca)}">${s.forca}</span></td>
          <td><span class="badge ${priorityClass(s.prioridade)}">${s.prioridade}</span></td>
          <td>${s.dias_sem_contato === 999 ? 'Nunca' : s.dias_sem_contato + 'd'}</td>
          <td>${s.interacoes_ultimo_mes}</td>
          <td style="color:${s.tendencia === 'melhorando' ? 'var(--green)' : s.tendencia === 'piorando' ? 'var(--red)' : 'var(--text-muted)'}">${s.tendencia}</td>
          <td style="font-size:12px;color:var(--orange)">${s.alerta || '--'}</td>
        </tr>
      `).join('')}</tbody>
    </table>
  `;
}

// --- Network ---
async function loadNetwork() {
  const data = await api('/network');
  if (data.status !== 'success') return;

  const r = data.resumo || {};
  document.getElementById('netMetrics').innerHTML = `
    <div class="metric-card"><div class="metric-label">Total Contatos</div><div class="metric-value">${r.total_contatos || 0}</div></div>
    <div class="metric-card"><div class="metric-label">Categorias</div><div class="metric-value">${r.categorias_ativas || 0}</div></div>
    <div class="metric-card"><div class="metric-label">Ativos (30d)</div><div class="metric-value">${r.contatos_ativos_ultimo_mes || 0}</div></div>
    <div class="metric-card"><div class="metric-label">Atividade</div><div class="metric-value">${r.taxa_atividade_percentual || 0}%</div></div>
  `;

  // Categories
  const cats = data.distribuicao_categorias || {};
  const catEl = document.getElementById('netCategories');
  if (Object.keys(cats).length === 0) {
    catEl.innerHTML = '<div class="empty-state"><p>Sem dados</p></div>';
  } else {
    const maxVal = Math.max(...Object.values(cats));
    catEl.innerHTML = Object.entries(cats).map(([cat, count]) => `
      <div style="display:flex;align-items:center;gap:12px;padding:8px 0">
        <span class="badge cat-${cat}" style="min-width:100px;justify-content:center">${catLabel(cat)}</span>
        <div style="flex:1;background:var(--bg-input);border-radius:4px;height:24px;overflow:hidden">
          <div style="width:${(count/maxVal)*100}%;height:100%;background:var(--accent-subtle);border-radius:4px"></div>
        </div>
        <span style="font-weight:700;min-width:30px;text-align:right">${count}</span>
      </div>
    `).join('');
  }

  // Gaps
  const gaps = data.gaps || [];
  const gapEl = document.getElementById('netGaps');
  if (gaps.length === 0) {
    gapEl.innerHTML = '<div class="empty-state"><p>Nenhum gap identificado. Sua rede esta bem estruturada!</p></div>';
  } else {
    gapEl.innerHTML = gaps.map(g => `
      <div class="insight-item ${g.tipo === 'gap_critico' ? 'insight-alerta' : 'insight-atencao'}">
        <div class="insight-icon">${g.tipo === 'gap_critico' ? '!' : '~'}</div>
        <div class="insight-text">
          <h4>${g.mensagem}</h4>
          <p>${g.acao}</p>
        </div>
      </div>
    `).join('');
  }

  // Insights
  const insights = data.insights || [];
  const insEl = document.getElementById('netInsights');
  if (insights.length === 0) {
    insEl.innerHTML = '<div class="empty-state"><p>Adicione mais contatos para gerar insights.</p></div>';
  } else {
    insEl.innerHTML = insights.map(i => `
      <div class="insight-item insight-${i.tipo}">
        <div class="insight-icon">${i.tipo === 'positivo' ? '+' : i.tipo === 'alerta' ? '!' : '~'}</div>
        <div class="insight-text">
          <h4>${i.titulo}</h4>
          <p>${i.descricao}${i.acao ? ` | ${i.acao}` : ''}</p>
        </div>
      </div>
    `).join('');
  }
}

// --- Settings ---
async function loadSettings() {
  const data = await api('/profile');
  if (data.profile) {
    document.getElementById('settingsName').value = data.profile.nome || '';
    document.getElementById('settingsType').value = data.profile.tipo || 'custom';
  }
  updateProfileInfo();
  document.getElementById('settingsType').addEventListener('change', updateProfileInfo);
}

function updateProfileInfo() {
  const tipo = document.getElementById('settingsType').value;
  const infoEl = document.getElementById('settingsProfileInfo');
  const descriptions = {
    empresario: 'Foco em clientes, parceiros, investidores e networking comercial.',
    diretor: 'Foco em equipe, stakeholders, mentorados e aliancas internas.',
    servidor_publico: 'Foco em relacoes institucionais, parcerias e comunidade.',
    saude: 'Foco em pacientes, referencias medicas e comunidade cientifica.',
    custom: 'Perfil personalizado, configuravel conforme suas necessidades.',
  };
  infoEl.innerHTML = `<p style="font-size:13px;color:var(--text-secondary);padding:8px 0">${descriptions[tipo] || ''}</p>`;
}

async function saveProfile() {
  const nome = document.getElementById('settingsName').value.trim();
  const tipo = document.getElementById('settingsType').value;
  if (!nome) { toast('Informe seu nome', true); return; }
  await api('/profile', {
    method: 'POST',
    body: JSON.stringify({ nome, tipo, objetivos: [] }),
  });
  toast('Perfil salvo com sucesso!');
  loadProfile();
}

// --- Modals ---
function openModal(name) {
  document.getElementById(`modal-${name}`).classList.add('active');
}

function closeModal(name) {
  document.getElementById(`modal-${name}`).classList.remove('active');
}

function openInteractionModal(contactId, contactName) {
  document.getElementById('intContactId').value = contactId;
  document.getElementById('intContactName').textContent = contactName;
  document.getElementById('intType').value = 'mensagem';
  document.getElementById('intSentiment').value = 'neutro';
  document.getElementById('intDesc').value = '';
  document.getElementById('intLocal').value = '';
  document.getElementById('intDuration').value = '';
  document.getElementById('intFollowUp').checked = false;
  document.getElementById('intFollowUpGroup').classList.add('hidden');
  document.getElementById('intFollowUpDesc').value = '';
  openModal('addInteraction');
}

document.getElementById('intFollowUp')?.addEventListener('change', function() {
  document.getElementById('intFollowUpGroup').classList.toggle('hidden', !this.checked);
});

// --- Submit Contact ---
async function submitNewContact() {
  const nome = document.getElementById('newName').value.trim();
  if (!nome) { toast('Nome e obrigatorio', true); return; }

  const data = {
    nome,
    categoria: document.getElementById('newCategory').value,
    email: document.getElementById('newEmail').value || null,
    telefone: document.getElementById('newPhone').value || null,
    empresa: document.getElementById('newCompany').value || null,
    cargo: document.getElementById('newRole').value || null,
    cidade: document.getElementById('newCity').value || null,
    aniversario: document.getElementById('newBirthday').value || null,
    como_conheceu: document.getElementById('newHowMet').value || null,
    notas: document.getElementById('newNotes').value || null,
    interesses: [],
    tags: [],
  };

  await api('/contacts', { method: 'POST', body: JSON.stringify(data) });
  closeModal('addContact');
  toast('Contato adicionado!');

  // Clear form
  ['newName','newEmail','newPhone','newCompany','newRole','newCity','newBirthday','newHowMet','newNotes'].forEach(id => {
    document.getElementById(id).value = '';
  });

  if (currentPage === 'contacts') loadContacts();
  else if (currentPage === 'dashboard') loadDashboard();
}

// --- Submit Interaction ---
async function submitInteraction() {
  const desc = document.getElementById('intDesc').value.trim();
  if (!desc) { toast('Descricao e obrigatoria', true); return; }

  const dur = document.getElementById('intDuration').value;

  const data = {
    contato_id: document.getElementById('intContactId').value,
    tipo: document.getElementById('intType').value,
    descricao: desc,
    sentimento: document.getElementById('intSentiment').value,
    duracao_minutos: dur ? parseInt(dur) : null,
    local: document.getElementById('intLocal').value || null,
    follow_up_necessario: document.getElementById('intFollowUp').checked,
    follow_up_descricao: document.getElementById('intFollowUpDesc').value || null,
    tags: [],
  };

  const result = await api('/interactions', { method: 'POST', body: JSON.stringify(data) });
  closeModal('addInteraction');

  if (result.status === 'success') {
    toast('Interacao registrada!');
    // Refresh current view
    if (currentPage === 'contact-detail') openContactDetail(data.contato_id);
    else if (currentPage === 'contacts') loadContacts();
    else if (currentPage === 'dashboard') loadDashboard();
  } else {
    toast(result.message || 'Erro ao registrar', true);
  }
}

// --- Chat ---
function selectAgent(agent, btn) {
  currentAgent = agent;
  document.querySelectorAll('.agent-tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
}

async function sendChat() {
  const input = document.getElementById('chatInput');
  const msg = input.value.trim();
  if (!msg) return;

  input.value = '';
  const messagesEl = document.getElementById('chatMessages');

  // Add user message
  const userMsgEl = document.createElement('div');
  userMsgEl.className = 'chat-msg chat-msg-user';
  userMsgEl.textContent = msg;
  messagesEl.appendChild(userMsgEl);

  // Add typing indicator
  const typingEl = document.createElement('div');
  typingEl.className = 'chat-typing';
  typingEl.innerHTML = '<div class="loading-spinner" style="display:inline-block;margin-right:8px"></div> Agente pensando...';
  messagesEl.appendChild(typingEl);
  messagesEl.scrollTop = messagesEl.scrollHeight;

  try {
    const data = await api('/chat', {
      method: 'POST',
      body: JSON.stringify({ message: msg, agent: currentAgent }),
    });

    typingEl.remove();

    const agentMsgEl = document.createElement('div');
    agentMsgEl.className = 'chat-msg chat-msg-agent';

    if (data.status === 'success') {
      agentMsgEl.innerHTML = renderMarkdown(data.response);
    } else {
      agentMsgEl.innerHTML = `<strong style="color:var(--red)">Erro:</strong> ${data.message}`;
    }

    messagesEl.appendChild(agentMsgEl);
  } catch (e) {
    typingEl.remove();
    const errEl = document.createElement('div');
    errEl.className = 'chat-msg chat-msg-agent';
    errEl.innerHTML = `<strong style="color:var(--red)">Erro de conexao:</strong> ${e.message}`;
    messagesEl.appendChild(errEl);
  }

  messagesEl.scrollTop = messagesEl.scrollHeight;
}

// --- Simple markdown renderer ---
function renderMarkdown(text) {
  if (!text) return '';
  let html = text
    // Code blocks
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Headers
    .replace(/^### (.*$)/gm, '<h4>$1</h4>')
    .replace(/^## (.*$)/gm, '<h3>$1</h3>')
    .replace(/^# (.*$)/gm, '<h2>$1</h2>')
    // Lists
    .replace(/^\- (.*$)/gm, '<li>$1</li>')
    .replace(/^\* (.*$)/gm, '<li>$1</li>')
    .replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
    // Tables (basic)
    .replace(/\|(.+)\|/g, (match) => {
      const cells = match.split('|').filter(c => c.trim());
      if (cells.every(c => /^[\s-:]+$/.test(c))) return '';
      const tag = 'td';
      return '<tr>' + cells.map(c => `<${tag}>${c.trim()}</${tag}>`).join('') + '</tr>';
    })
    // Line breaks
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>');

  // Wrap in paragraphs
  if (!html.startsWith('<')) html = '<p>' + html + '</p>';

  // Wrap consecutive li in ul
  html = html.replace(/(<li>.*?<\/li>(\s*<br>)*)+/g, (match) => {
    return '<ul>' + match.replace(/<br>/g, '') + '</ul>';
  });

  // Wrap consecutive tr in table
  html = html.replace(/(<tr>.*?<\/tr>\s*)+/g, (match) => {
    return '<table>' + match + '</table>';
  });

  return html;
}
