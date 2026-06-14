/**
 * CalcPro — script.js
 * Lógica principal da calculadora profissional.
 *
 * Estrutura:
 *  1. Estado da aplicação
 *  2. Utilitários (formatação, localStorage)
 *  3. Lógica da calculadora
 *  4. Lógica de memória
 *  5. Conversor de moedas
 *  6. Histórico
 *  7. UI helpers (tema, toast, tabs, modal)
 *  8. Event listeners
 *  9. Inicialização
 */

/* ══════════════════════════════════════════════
   1. ESTADO DA APLICAÇÃO
══════════════════════════════════════════════ */

const state = {
  // Calculadora
  expression: '0',        // expressão sendo montada
  result:     '',          // resultado prévia (preview)
  waitingForOperand: true, // true logo após um operador ou =
  lastOperator: '',
  lastOperand:  '',

  // Memória
  memory: 0,
  hasMemory: false,

  // Histórico (persiste no localStorage)
  history: [],

  // Câmbio
  rates:      {},          // { USD: 1, BRL: 5.1, ... }
  ratesAt:    null,        // Date da última busca
};

/* ══════════════════════════════════════════════
   2. UTILITÁRIOS
══════════════════════════════════════════════ */

/**
 * Formata um número com separadores de milhar no locale pt-BR.
 * Ex: 1000000 → "1.000.000"
 */
function formatNumber(value) {
  const num = parseFloat(value);
  if (isNaN(num)) return value;

  const maximumFractionDigits = String(value).includes('.')
    ? Math.max(0, String(value).split('.')[1]?.length ?? 0)
    : 0;

  return num.toLocaleString('pt-BR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: Math.min(maximumFractionDigits, 10),
  });
}

/** Carrega dados do localStorage com fallback seguro */
function loadFromStorage(key, fallback = null) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

/** Salva dados no localStorage */
function saveToStorage(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    console.warn('localStorage indisponível.');
  }
}

/** Retorna hora formatada no padrão HH:mm:ss */
function formatTime(date = new Date()) {
  return date.toLocaleTimeString('pt-BR');
}

/** Retorna data + hora formatadas */
function formatDateTime(date = new Date()) {
  return date.toLocaleString('pt-BR');
}

/* ══════════════════════════════════════════════
   3. LÓGICA DA CALCULADORA
══════════════════════════════════════════════ */

const elExpression = document.getElementById('expression');
const elResult     = document.getElementById('result');

/** Atualiza o display com a expressão atual e um preview do resultado */
function renderDisplay() {
  const raw = state.expression;

  // Formata operadores para exibição amigável
  const display = raw
    .replace(/\*/g,  ' × ')
    .replace(/\//g,  ' ÷ ')
    .replace(/\+/g,  ' + ')
    .replace(/-/g,   ' − ')
    .replace(/%/g,   '%')
    .trim();

  elExpression.textContent = display || '0';

  // Encolhe a fonte para expressões longas
  elExpression.classList.toggle('shrink', raw.length > 14);

  // Preview do resultado enquanto ainda não foi calculado
  if (!state.waitingForOperand && raw !== state.result && !isNaN(parseFloat(raw))) {
    try {
      const preview = evaluateExpression(raw);
      elResult.textContent = (preview !== null && preview !== raw)
        ? `= ${formatNumber(String(preview))}`
        : '';
    } catch {
      elResult.textContent = '';
    }
  } else {
    elResult.textContent = state.result ? `= ${state.result}` : '';
  }
}

/**
 * Avalia a expressão matemática de forma segura.
 * Usa Function() com whitelist de caracteres para evitar injeção.
 * Retorna o resultado numérico ou null em caso de erro.
 */
function evaluateExpression(expr) {
  // Whitelist: apenas dígitos e operadores matemáticos
  if (!/^[\d\s\+\-\*\/\.\%\(\)]+$/.test(expr)) return null;

  // Previne divisão por zero antes de avaliar
  if (/\/\s*0(?!\d)/.test(expr)) {
    throw new Error('DIVISION_BY_ZERO');
  }

  try {
    // eslint-disable-next-line no-new-func
    const raw = new Function(`"use strict"; return (${expr})`)();
    if (!isFinite(raw)) throw new Error('INFINITE');
    return parseFloat(raw.toFixed(10)); // evita flutuação do IEEE 754
  } catch (err) {
    throw err;
  }
}

/** Insere um dígito ou ponto decimal na expressão */
function inputDigit(digit) {
  // Impede múltiplos pontos no mesmo número
  const parts = state.expression.split(/[\+\-\*\/]/);
  const currentPart = parts[parts.length - 1];
  if (digit === '.' && currentPart.includes('.')) return;

  if (state.waitingForOperand) {
    // Começa um novo número
    state.expression = digit === '.' ? '0.' : digit;
    state.waitingForOperand = false;
    state.result = '';
  } else {
    // Anexa ao número atual
    state.expression = state.expression === '0' && digit !== '.'
      ? digit
      : state.expression + digit;
  }

  renderDisplay();
}

/** Insere um operador binário (+, -, *, /, %) */
function inputOperator(op) {
  state.lastOperator = op;
  state.lastOperand  = state.expression;

  const lastChar = state.expression.slice(-1);
  const isOperator = /[\+\-\*\/]/.test(lastChar);

  if (isOperator) {
    // Substitui o operador anterior em vez de acumular
    state.expression = state.expression.slice(0, -1) + op;
  } else {
    state.expression += op;
  }

  state.waitingForOperand = false;
  state.result = '';
  renderDisplay();
}

/** Calcula a expressão e exibe o resultado */
function calculate() {
  if (!state.expression || state.expression === '0') return;

  try {
    const resultValue = evaluateExpression(state.expression);
    if (resultValue === null) return;

    const resultStr = String(resultValue);
    const formatted = formatNumber(resultStr);

    // Expressão amigável para histórico
    const prettyExpr = state.expression
      .replace(/\*/g, '×')
      .replace(/\//g, '÷')
      .replace(/\-/g, '−');

    addToHistory(prettyExpr, formatted);

    state.result = formatted;
    state.expression = resultStr;
    state.waitingForOperand = true;

    renderDisplay();

  } catch (err) {
    if (err.message === 'DIVISION_BY_ZERO') {
      showError('Divisão por zero não é permitida');
    } else if (err.message === 'INFINITE') {
      showError('Resultado inválido');
    } else {
      showError('Expressão inválida');
    }
  }
}

/** Limpa tudo (AC) */
function clearAll() {
  state.expression = '0';
  state.result = '';
  state.waitingForOperand = true;
  renderDisplay();
}

/** Apaga o último caractere */
function backspace() {
  if (state.waitingForOperand) {
    clearAll();
    return;
  }

  state.expression = state.expression.slice(0, -1) || '0';
  if (state.expression === '0') state.waitingForOperand = true;
  renderDisplay();
}

/** Raiz quadrada do valor atual */
function squareRoot() {
  const num = parseFloat(state.expression);
  if (isNaN(num)) return;

  if (num < 0) {
    showError('Raiz de número negativo');
    return;
  }

  const result = Math.sqrt(num);
  state.expression = String(parseFloat(result.toFixed(10)));
  state.result = `√${formatNumber(String(num))} = ${formatNumber(state.expression)}`;
  state.waitingForOperand = true;
  renderDisplay();
}

/** Eleva ao quadrado o valor atual */
function squareValue() {
  const num = parseFloat(state.expression);
  if (isNaN(num)) return;

  const result = num * num;
  state.result = `${formatNumber(String(num))}² = ${formatNumber(String(result))}`;
  state.expression = String(result);
  state.waitingForOperand = true;
  renderDisplay();
}

/** Exibe uma mensagem de erro no display temporariamente */
function showError(message) {
  elExpression.textContent = message;
  elResult.textContent = '';
  setTimeout(() => {
    clearAll();
  }, 1800);
}

/* ══════════════════════════════════════════════
   4. LÓGICA DE MEMÓRIA
══════════════════════════════════════════════ */

const elMemIndicator = document.getElementById('mem-indicator');

function renderMemIndicator() {
  elMemIndicator.textContent = state.hasMemory
    ? `M: ${formatNumber(String(state.memory))}`
    : '';
}

function memoryAction(action) {
  const current = parseFloat(state.expression) || 0;

  switch (action) {
    case 'mc':
      state.memory = 0;
      state.hasMemory = false;
      showToast('Memória apagada');
      break;

    case 'mr':
      if (!state.hasMemory) { showToast('Memória vazia'); return; }
      state.expression = String(state.memory);
      state.waitingForOperand = true;
      state.result = '';
      renderDisplay();
      showToast(`Recuperado: ${formatNumber(String(state.memory))}`);
      break;

    case 'm-plus':
      state.memory += current;
      state.hasMemory = true;
      showToast(`M+ → ${formatNumber(String(state.memory))}`);
      break;

    case 'm-minus':
      state.memory -= current;
      state.hasMemory = true;
      showToast(`M− → ${formatNumber(String(state.memory))}`);
      break;
  }

  renderMemIndicator();
}

/* ══════════════════════════════════════════════
   5. CONVERSOR DE MOEDAS
══════════════════════════════════════════════ */

// Moedas suportadas com emoji de bandeira
const CURRENCIES = [
  { code: 'USD', name: 'Dólar Americano',    flag: '🇺🇸' },
  { code: 'BRL', name: 'Real Brasileiro',    flag: '🇧🇷' },
  { code: 'EUR', name: 'Euro',               flag: '🇪🇺' },
  { code: 'GBP', name: 'Libra Esterlina',    flag: '🇬🇧' },
  { code: 'JPY', name: 'Iene Japonês',       flag: '🇯🇵' },
  { code: 'CNY', name: 'Yuan Chinês',        flag: '🇨🇳' },
  { code: 'CAD', name: 'Dólar Canadense',    flag: '🇨🇦' },
  { code: 'AUD', name: 'Dólar Australiano',  flag: '🇦🇺' },
  { code: 'CHF', name: 'Franco Suíço',       flag: '🇨🇭' },
  { code: 'ARS', name: 'Peso Argentino',     flag: '🇦🇷' },
  { code: 'MXN', name: 'Peso Mexicano',      flag: '🇲🇽' },
  { code: 'INR', name: 'Rúpia Indiana',      flag: '🇮🇳' },
  { code: 'KRW', name: 'Won Sul-Coreano',    flag: '🇰🇷' },
  { code: 'ZAR', name: 'Rand Sul-Africano',  flag: '🇿🇦' },
];

const POPULAR_PAIRS = [
  { from: 'USD', to: 'BRL' },
  { from: 'EUR', to: 'BRL' },
  { from: 'USD', to: 'EUR' },
  { from: 'GBP', to: 'BRL' },
];

/** Preenche os <select> com as moedas disponíveis */
function populateCurrencySelects() {
  const fromEl = document.getElementById('currency-from');
  const toEl   = document.getElementById('currency-to');

  CURRENCIES.forEach(({ code, name, flag }) => {
    const optFrom = new Option(`${flag} ${code} — ${name}`, code);
    const optTo   = new Option(`${flag} ${code} — ${name}`, code);
    fromEl.appendChild(optFrom);
    toEl.appendChild(optTo);
  });

  fromEl.value = 'USD';
  toEl.value   = 'BRL';
}

/**
 * Busca cotações da API gratuita exchangerate-api.
 * Usa USD como base e converte para os pares necessários.
 */
async function fetchRates() {
  // Evita nova busca se os dados têm menos de 15 min
  if (state.ratesAt && (Date.now() - state.ratesAt < 15 * 60 * 1000)) return;

  try {
    const res  = await fetch('https://api.exchangerate-api.com/v4/latest/USD');
    if (!res.ok) throw new Error('Resposta inválida da API');
    const data = await res.json();
    state.rates  = data.rates;
    state.ratesAt = Date.now();

    const el = document.getElementById('rate-timestamp');
    el.textContent = `Cotações atualizadas em ${formatDateTime()}`;

    renderPopularPairs();
    saveToStorage('calcpro_rates',   state.rates);
    saveToStorage('calcpro_ratesAt', state.ratesAt);
  } catch {
    // Tenta usar cotações em cache
    const cached   = loadFromStorage('calcpro_rates');
    const cachedAt = loadFromStorage('calcpro_ratesAt');
    if (cached) {
      state.rates  = cached;
      state.ratesAt = cachedAt;
      const el = document.getElementById('rate-timestamp');
      el.textContent = `⚠ Offline — cotações de ${formatDateTime(new Date(cachedAt))}`;
      renderPopularPairs();
    } else {
      document.getElementById('rate-timestamp').textContent = '⚠ Não foi possível carregar cotações.';
    }
  }
}

/** Converte um valor entre duas moedas */
function convertCurrency(amount, from, to) {
  if (!state.rates[from] || !state.rates[to]) return null;
  // Converte para USD primeiro, depois para moeda destino
  const inUSD = amount / state.rates[from];
  return inUSD * state.rates[to];
}

/** Exibe o resultado da conversão no painel */
function renderConversionResult(amount, from, to) {
  const result = convertCurrency(amount, from, to);
  const el     = document.getElementById('currency-result');

  if (result === null) {
    el.innerHTML = '<p style="color:var(--accent-coral);font-size:.85rem">Cotações indisponíveis.</p>';
    return;
  }

  const rate = convertCurrency(1, from, to);
  const fromInfo = CURRENCIES.find(c => c.code === from);
  const toInfo   = CURRENCIES.find(c => c.code === to);

  el.classList.add('has-result');
  el.innerHTML = `
    <div class="currency-result__from">
      ${fromInfo?.flag ?? ''} ${formatNumber(String(amount))} ${from}
    </div>
    <div class="currency-result__to">
      ${toInfo?.flag ?? ''} ${formatNumber(result.toFixed(4))} ${to}
    </div>
    <div class="currency-result__rate">
      1 ${from} = ${formatNumber(rate.toFixed(6))} ${to}
    </div>
  `;
}

/** Renderiza os pares populares de moedas */
function renderPopularPairs() {
  const grid = document.getElementById('popular-grid');
  grid.innerHTML = '';

  POPULAR_PAIRS.forEach(({ from, to }) => {
    const rate = convertCurrency(1, from, to);
    if (rate === null) return;

    const btn = document.createElement('button');
    btn.className = 'popular-pair';
    btn.setAttribute('aria-label', `Converter ${from} para ${to}`);
    btn.innerHTML = `
      <div class="popular-pair__label">${from} → ${to}</div>
      <div class="popular-pair__rate">${formatNumber(rate.toFixed(4))}</div>
    `;

    btn.addEventListener('click', () => {
      document.getElementById('currency-from').value = from;
      document.getElementById('currency-to').value   = to;
      document.getElementById('currency-amount').value = '1';
      renderConversionResult(1, from, to);
    });

    grid.appendChild(btn);
  });
}

/* ══════════════════════════════════════════════
   6. HISTÓRICO
══════════════════════════════════════════════ */

const elHistoryList  = document.getElementById('history-list');
const elHistoryEmpty = document.getElementById('history-empty');

/** Adiciona uma operação ao histórico e atualiza a UI */
function addToHistory(expression, result) {
  const item = {
    expression,
    result,
    time: new Date().toISOString(),
  };

  state.history.unshift(item); // mais recente primeiro

  // Limita a 50 entradas
  if (state.history.length > 50) state.history.pop();

  saveToStorage('calcpro_history', state.history);
  renderHistory();
}

/** Renderiza toda a lista de histórico */
function renderHistory() {
  elHistoryList.innerHTML = '';
  const isEmpty = state.history.length === 0;
  elHistoryEmpty.style.display = isEmpty ? 'block' : 'none';

  state.history.forEach(item => {
    const li = document.createElement('li');
    li.className = 'history-item';
    li.setAttribute('role', 'listitem');
    li.setAttribute('title', 'Clique para reutilizar este resultado');

    li.innerHTML = `
      <div class="history-item__expr">${item.expression}</div>
      <div class="history-item__result">= ${item.result}</div>
      <div class="history-item__time">${formatDateTime(new Date(item.time))}</div>
    `;

    // Clica para carregar o resultado de volta na calculadora
    li.addEventListener('click', () => {
      const rawResult = item.result.replace(/\./g, '').replace(',', '.');
      state.expression = rawResult;
      state.result = '';
      state.waitingForOperand = true;
      renderDisplay();

      // Muda para a aba da calculadora
      switchTab('calc');
      showToast('Resultado carregado!');
    });

    elHistoryList.appendChild(li);
  });
}

/** Limpa todo o histórico */
function clearHistory() {
  state.history = [];
  saveToStorage('calcpro_history', []);
  renderHistory();
  showToast('Histórico apagado');
}

/* ══════════════════════════════════════════════
   7. UI HELPERS
══════════════════════════════════════════════ */

/** Toast de notificação */
let toastTimer = null;
const elToast = document.getElementById('toast');

function showToast(message, duration = 2200) {
  elToast.textContent = message;
  elToast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => elToast.classList.remove('show'), duration);
}

/** Alterna entre tema claro e escuro */
function toggleTheme() {
  const html    = document.documentElement;
  const current = html.getAttribute('data-theme');
  const next    = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  saveToStorage('calcpro_theme', next);
}

/** Alterna entre abas */
function switchTab(tabId) {
  document.querySelectorAll('.tab').forEach(tab => {
    const isActive = tab.dataset.tab === tabId;
    tab.classList.toggle('tab--active', isActive);
    tab.setAttribute('aria-selected', isActive);
  });

  document.querySelectorAll('.tab-panel').forEach(panel => {
    const isActive = panel.id === `panel-${tabId}`;
    panel.classList.toggle('tab-panel--active', isActive);
    panel.hidden = !isActive;
  });

  // Carrega cotações ao entrar na aba de moedas
  if (tabId === 'currency') fetchRates();
}

/** Copia o resultado para a área de transferência */
async function copyResult() {
  const text = state.result || state.expression;
  if (!text || text === '0') return;

  try {
    await navigator.clipboard.writeText(text);
    showToast('✓ Resultado copiado!');
  } catch {
    showToast('Não foi possível copiar');
  }
}

/** Efeito visual de "clique" no botão do teclado */
function flashKey(key) {
  key.classList.add('pressed');
  setTimeout(() => key.classList.remove('pressed'), 150);
}

/* ══════════════════════════════════════════════
   8. EVENT LISTENERS
══════════════════════════════════════════════ */

/** Keypad: cliques nos botões */
document.querySelector('.keypad').addEventListener('click', e => {
  const key = e.target.closest('.key');
  if (!key) return;

  const { action, value } = key.dataset;

  if (action) {
    switch (action) {
      case 'clear':     clearAll();     break;
      case 'backspace': backspace();    break;
      case 'sqrt':      squareRoot();   break;
      case 'square':    squareValue();  break;
      case 'equals':    calculate();    break;
    }
  } else if (value !== undefined) {
    if (['+', '-', '*', '/', '%'].includes(value)) {
      inputOperator(value);
    } else {
      inputDigit(value);
    }
  }
});

/** Memória */
document.querySelector('.memory-bar').addEventListener('click', e => {
  const btn = e.target.closest('.mem-btn');
  if (btn) memoryAction(btn.dataset.mem);
});

/** Teclado físico */
document.addEventListener('keydown', e => {
  const key = e.key;

  // Atalhos globais
  if (key === 'Escape') { clearAll(); return; }
  if (key === 'Enter' || key === '=') { calculate(); return; }
  if (key === 'Backspace') { backspace(); return; }

  // Dígitos e pontos
  if (/^\d$/.test(key))       { inputDigit(key); return; }
  if (key === '.' || key === ',') { inputDigit('.'); return; }

  // Operadores
  if (['+', '-', '*', '/'].includes(key)) { inputOperator(key); return; }
  if (key === '%') { inputOperator('%'); return; }
});

/** Tema */
document.getElementById('btn-theme').addEventListener('click', toggleTheme);

/** Copiar resultado */
document.getElementById('btn-copy').addEventListener('click', copyResult);

/** Tabs */
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => switchTab(tab.dataset.tab));
});

/** Histórico: limpar */
document.getElementById('btn-clear-history').addEventListener('click', clearHistory);

/** Modal: atalhos */
const shortcutsModal = document.getElementById('shortcuts-modal');

document.getElementById('btn-shortcuts').addEventListener('click', () => {
  shortcutsModal.hidden = false;
});

document.getElementById('btn-close-shortcuts').addEventListener('click', () => {
  shortcutsModal.hidden = true;
});

shortcutsModal.addEventListener('click', e => {
  if (e.target === shortcutsModal) shortcutsModal.hidden = true;
});

document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && !shortcutsModal.hidden) {
    shortcutsModal.hidden = true;
  }
});

/** Conversor: botão converter */
document.getElementById('btn-convert').addEventListener('click', async () => {
  const amount = parseFloat(document.getElementById('currency-amount').value);
  const from   = document.getElementById('currency-from').value;
  const to     = document.getElementById('currency-to').value;

  if (isNaN(amount) || amount < 0) {
    showToast('Informe um valor válido');
    return;
  }

  await fetchRates();
  renderConversionResult(amount, from, to);
});

/** Conversor: inverter moedas */
document.getElementById('btn-swap-currency').addEventListener('click', () => {
  const fromEl = document.getElementById('currency-from');
  const toEl   = document.getElementById('currency-to');
  [fromEl.value, toEl.value] = [toEl.value, fromEl.value];
});

/* ══════════════════════════════════════════════
   9. INICIALIZAÇÃO
══════════════════════════════════════════════ */

function init() {
  // Restaura tema salvo
  const savedTheme = loadFromStorage('calcpro_theme', 'dark');
  document.documentElement.setAttribute('data-theme', savedTheme);

  // Restaura histórico
  state.history = loadFromStorage('calcpro_history', []);
  renderHistory();

  // Preenche selects de moeda
  populateCurrencySelects();

  // Display inicial
  renderDisplay();
  renderMemIndicator();
}

init();
