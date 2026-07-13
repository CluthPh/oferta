const state = {
  adminAuthenticated: false,
  currentPage: "dashboard",
  dashboard: null,
  validation: null,
  products: [],
  approvals: [],
  affiliates: [],
  pending: [],
  publications: [],
  sources: [],
  report: null,
  logs: [],
  settings: null,
  settingsOriginal: null,
  nichesConfig: null,
  selectedApprovals: new Set(),
  scanRunning: false,
  pagination: {
    products: { page: 1, perPage: 20 },
    scans: { page: 1, perPage: 8 },
    publications: { page: 1, perPage: 20 },
  },
  logTimer: null,
  confirmResolve: null,
};

const pageLabels = {
  dashboard: "Visao geral",
  products: "Produtos",
  approvals: "Aprovacao",
  affiliates: "Afiliados",
  publications: "Publicacoes",
  sources: "Fontes",
  config: "Configuracoes",
  settings: "Ajustes",
  reports: "Relatorios",
  logs: "Logs",
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

const attr = escapeHtml;

function refreshIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function number(value) {
  return Number(value || 0).toLocaleString("pt-BR");
}

function toNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function money(value) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  return Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function percent(value) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  return `${Number(value).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}%`;
}

function dateTime(value) {
  if (!value) return "-";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "-";
  return parsed.toLocaleString("pt-BR");
}

function dateOnly(value) {
  if (!value) return "-";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "-";
  return parsed.toLocaleDateString("pt-BR");
}

function duration(start, end) {
  if (!start) return "-";
  const begin = new Date(start).getTime();
  const finish = end ? new Date(end).getTime() : Date.now();
  if (!Number.isFinite(begin) || !Number.isFinite(finish)) return "-";
  const seconds = Math.max(0, Math.round((finish - begin) / 1000));
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const rest = seconds % 60;
  if (minutes < 60) return `${minutes}m ${rest}s`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m`;
}

function safeUrl(value) {
  if (!value) return "";
  try {
    const parsed = new URL(String(value), window.location.origin);
    return ["http:", "https:"].includes(parsed.protocol) ? parsed.href : "";
  } catch (_error) {
    return "";
  }
}

function icon(name) {
  return `<i data-lucide="${attr(name)}"></i>`;
}

function pill(text, kind = "neutral") {
  return `<span class="pill ${kind}">${escapeHtml(text)}</span>`;
}

function dot(kind = "warn") {
  return `<span class="dot ${kind}"></span>`;
}

function emptyState(title, message = "") {
  return `
    <div class="empty-state">
      <strong>${escapeHtml(title)}</strong>
      ${message ? `<p>${escapeHtml(message)}</p>` : ""}
    </div>
  `;
}

function skeleton() {
  return '<div class="skeleton"></div>';
}

function setLoading(selector) {
  const node = $(selector);
  if (node) node.innerHTML = skeleton();
}

function toast(message, kind = "ok") {
  const region = $("#toast-region");
  const node = document.createElement("div");
  node.className = `toast ${kind}`;
  node.textContent = message;
  region.appendChild(node);
  window.setTimeout(() => node.remove(), 3800);
}

async function api(path, options = {}, meta = {}) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }
  const response = await fetch(path, {
    credentials: "same-origin",
    ...options,
    headers,
  });
  if (!response.ok) {
    const error = await responseError(response, path);
    if (response.status === 401) {
      setAuthenticated(false);
      if (!meta.silentAuth) openLogin();
    }
    throw error;
  }
  const contentType = response.headers.get("content-type") || "";
  return contentType.includes("application/json") ? response.json() : response.text();
}

async function responseError(response, path) {
  let detail = response.statusText;
  try {
    const body = await response.json();
    detail = body.detail || body.message || JSON.stringify(body);
  } catch (_jsonError) {
    try {
      detail = await response.text();
    } catch (_textError) {
      detail = response.statusText;
    }
  }
  console.debug("API error", { path, status: response.status, detail });
  const messages = {
    401: "Sessao administrativa invalida. Entre novamente.",
    403: "Voce nao tem permissao para esta acao.",
    404: "Registro nao encontrado.",
    500: "Falha interna no servidor. Verifique os logs.",
  };
  let message = messages[response.status] || "Falha ao comunicar com a API.";
  if (response.status === 422 && detail) {
    message = `Dados invalidos: ${String(detail).slice(0, 180)}`;
  }
  if (response.status === 503 && detail) {
    message = String(detail).slice(0, 180);
  }
  const error = new Error(message);
  error.status = response.status;
  error.detail = detail;
  return error;
}

function setAuthenticated(value) {
  state.adminAuthenticated = Boolean(value);
  $("#admin-label").textContent = state.adminAuthenticated ? "Admin ativo" : "Entrar";
  $("#open-login").classList.toggle("hidden", state.adminAuthenticated);
  $("#logout").classList.toggle("hidden", !state.adminAuthenticated);
}

async function checkAuth() {
  try {
    await api("/auth/status", {}, { silentAuth: true });
    setAuthenticated(true);
  } catch (error) {
    if (![401, 503].includes(error.status)) {
      toast(error.message, "warn");
    }
    setAuthenticated(false);
  }
}

function openLogin() {
  $("#login-modal").classList.remove("hidden");
  $("#login-error").textContent = "";
  $("#admin-key").value = "";
  window.setTimeout(() => $("#admin-key").focus(), 50);
}

function closeLogin() {
  $("#login-modal").classList.add("hidden");
  $("#login-error").textContent = "";
  $("#admin-key").value = "";
}

async function login(event) {
  event.preventDefault();
  const key = $("#admin-key").value.trim();
  $("#login-error").textContent = "";
  if (!key) {
    $("#login-error").textContent = "Informe a chave administrativa.";
    return;
  }
  try {
    await api("/auth/login", { method: "POST", body: JSON.stringify({ admin_key: key }) });
    setAuthenticated(true);
    closeLogin();
    toast("Acesso administrativo liberado.");
    await refreshAll();
  } catch (error) {
    $("#login-error").textContent = error.message;
  }
}

async function logout() {
  await api("/auth/logout", { method: "POST" });
  setAuthenticated(false);
  toast("Sessao encerrada.");
}

function requireAdmin() {
  if (state.adminAuthenticated) return true;
  openLogin();
  toast("Entre para executar acoes administrativas.", "warn");
  return false;
}

function openConfirm(message) {
  $("#confirm-message").textContent = message;
  $("#confirm-modal").classList.remove("hidden");
  return new Promise((resolve) => {
    state.confirmResolve = resolve;
  });
}

function closeConfirm(value) {
  $("#confirm-modal").classList.add("hidden");
  if (state.confirmResolve) state.confirmResolve(value);
  state.confirmResolve = null;
}

function table(headersList, rows) {
  if (!rows.length) return emptyState("Nenhum registro encontrado.");
  const head = headersList
    .map((item) => {
      const label = typeof item === "string" ? item : item.label;
      const extra = typeof item === "string" ? "" : item.className || "";
      return `<th class="${attr(extra)}">${escapeHtml(label)}</th>`;
    })
    .join("");
  return `
    <table>
      <thead><tr>${head}</tr></thead>
      <tbody>${rows.join("")}</tbody>
    </table>
  `;
}

function getPagination(key, total) {
  const pageState = state.pagination[key];
  const pages = Math.max(1, Math.ceil(total / pageState.perPage));
  pageState.page = Math.min(pageState.page, pages);
  const start = (pageState.page - 1) * pageState.perPage;
  return {
    start,
    end: start + pageState.perPage,
    page: pageState.page,
    pages,
    perPage: pageState.perPage,
  };
}

function pager(key, total) {
  const item = getPagination(key, total);
  return `
    <div class="pager">
      <span class="muted-chip">${item.page}/${item.pages} - ${number(total)} registros</span>
      <button class="button small secondary" data-page-nav="${attr(key)}" data-direction="-1" ${item.page <= 1 ? "disabled" : ""}>Anterior</button>
      <button class="button small secondary" data-page-nav="${attr(key)}" data-direction="1" ${item.page >= item.pages ? "disabled" : ""}>Proxima</button>
    </div>
  `;
}

function setLastUpdated() {
  $("#last-updated").textContent = `Atualizado ${new Date().toLocaleTimeString("pt-BR")}`;
}

async function refreshAll() {
  await Promise.allSettled([
    loadDashboard(),
    loadValidation(),
    loadProducts(),
    loadAffiliates(),
    loadPending(),
    loadSources(),
    loadPublications(),
  ]);
  if (state.adminAuthenticated) {
    await Promise.allSettled([
      loadApprovals({ silentAuth: true }),
      loadSettings({ silentAuth: true }),
      state.currentPage === "reports" ? loadReport({ silentAuth: true }) : Promise.resolve(),
      state.currentPage === "logs" ? loadLogs({ silentAuth: true }) : Promise.resolve(),
    ]);
  }
  renderConfigViews();
  setLastUpdated();
  refreshIcons();
}

async function showPage(page) {
  if (!pageLabels[page]) return;
  state.currentPage = page;
  $$(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.page === page));
  $$(".page").forEach((item) => item.classList.toggle("active", item.id === page));
  $("#page-title").textContent = pageLabels[page];
  $("#breadcrumb").textContent = `Oferta Telegram / ${pageLabels[page]}`;
  document.body.classList.remove("sidebar-open");

  if (page === "dashboard") await Promise.allSettled([loadDashboard(), loadValidation()]);
  if (page === "products") await loadProducts();
  if (page === "approvals") {
    if (!requireAdmin()) return;
    await loadApprovals();
  }
  if (page === "affiliates") await Promise.allSettled([loadAffiliates(), loadPending()]);
  if (page === "publications") await loadPublications();
  if (page === "sources") await loadSources();
  if (page === "config") {
    if (!requireAdmin()) return;
    await Promise.allSettled([loadNiches(), loadConfig(), loadSettings({ silentAuth: true })]);
  }
  if (page === "settings") {
    if (!requireAdmin()) return;
    await loadSettings();
  }
  if (page === "reports") {
    if (!requireAdmin()) return;
    await loadReport();
  }
  if (page === "logs") {
    if (!requireAdmin()) return;
    await loadLogs();
  }
  refreshIcons();
}

async function loadDashboard() {
  setLoading("#cards");
  const data = await api("/dashboard");
  state.dashboard = data;
  renderDashboard();
  renderConfigViews();
}

function renderDashboard() {
  if (!state.dashboard) return;
  const { counts, settings, latest_scan: latestScan } = state.dashboard;
  renderSystemStatus();
  renderMetricCards(counts, latestScan);
  renderPipeline(counts, latestScan);
  renderAutomation(settings, latestScan);
  renderScans(state.dashboard.recent_scans || []);
  renderEvents(state.dashboard.recent_events || []);
  renderRecentApprovals(state.dashboard.recent_approvals || []);
}

function renderSystemStatus() {
  const hasErrors = Boolean(state.validation?.checks?.some((item) => !item.ok && item.level !== "warning"));
  const hasWarnings = Boolean(state.validation?.checks?.some((item) => !item.ok));
  const kind = hasErrors ? "err" : hasWarnings ? "warn" : "ok";
  const label = hasErrors ? "Erro" : hasWarnings ? "Atencao" : "Operacional";
  $("#top-system-status").className = `status-badge ${kind}`;
  $("#top-system-status").innerHTML = `${dot(kind)}${label}`;
  $("#sidebar-system-dot").className = `dot ${kind}`;
  $("#sidebar-system-status").textContent = label;
}

function renderMetricCards(counts, latestScan) {
  const metrics = [
    ["package-search", "Produtos coletados", counts.products, "Total salvo no banco", "feature", latestScan ? `Ultimo ciclo: ${number(latestScan.collected_count)}` : "Sem ciclo recente"],
    ["archive-x", "Produtos ignorados", counts.ignored_products, "Itens filtrados ou marcados", "", "Sem comparativo"],
    ["badge-check", "Aprovacoes pendentes", counts.pending_approvals, "Aguardando revisao", "warn feature", "Fila atual"],
    ["link-2", "Afiliados ativos", counts.affiliate_links, "Links cadastrados", "good", "Total de links"],
    ["unlink", "Links pendentes", counts.pending_affiliate_links, "Produtos sem afiliado", "warn", "CSV de pendencias"],
    ["radio", "Publicacoes realizadas", counts.publications, "Registros de publicacao", "feature", `Enviadas: ${number(counts.sent_publications)}`],
    ["send", "Mensagens enviadas", counts.sent_publications, "Status sent", "good", "Telegram/API"],
    ["circle-alert", "Falhas", counts.failed_publications, "Publicacoes com erro", counts.failed_publications ? "bad feature" : "good feature", "Monitorar logs"],
    ["repeat-2", "Ciclos executados", counts.scan_runs, "Execucoes registradas", "", latestScan ? `Duracao: ${duration(latestScan.started_at, latestScan.finished_at)}` : "Sem dados"],
  ];
  $("#cards").innerHTML = metrics
    .map(
      ([iconName, title, value, desc, kind, foot]) => `
        <article class="metric-card ${kind}" title="${attr(desc)}">
          <div class="metric-head">
            <span class="metric-icon">${icon(iconName)}</span>
            <span class="metric-title">${escapeHtml(title)}</span>
          </div>
          <strong class="metric-value">${number(value)}</strong>
          <p class="metric-desc">${escapeHtml(desc)}</p>
          <div class="metric-foot"><span>${escapeHtml(foot)}</span>${icon("info")}</div>
        </article>
      `,
    )
    .join("");
}

function renderPipeline(counts, latestScan) {
  const collected = counts.products || 0;
  const ignored = counts.ignored_products || 0;
  const pendingApprovals = counts.pending_approvals || 0;
  const affiliateLinks = counts.affiliate_links || 0;
  const pendingLinks = counts.pending_affiliate_links || 0;
  const publications = counts.publications || 0;
  const sent = counts.sent_publications || 0;
  const stages = [
    ["Coleta", collected, "Produtos no banco", latestScan ? `${number(latestScan.collected_count)} no ultimo ciclo` : "Sem ciclo recente", "ok"],
    ["Filtro", ignored, "Ignorados", collected ? `${percent((ignored / collected) * 100)} do total` : "Sem base", ignored ? "warn" : "ok"],
    ["Aprovacao", pendingApprovals, "Pendencias", pendingApprovals ? "Revisao manual" : "Fila limpa", pendingApprovals ? "warn" : "ok"],
    ["Link afiliado", affiliateLinks, "Links ativos", pendingLinks ? `${number(pendingLinks)} pendentes` : "Sem pendencias", pendingLinks ? "warn" : "ok"],
    ["Publicacao", publications, "Registros", collected ? `${percent((publications / collected) * 100)} sobre produtos` : "Sem base", "info"],
    ["Telegram", sent, "Enviadas", publications ? `${percent((sent / publications) * 100)} de sucesso` : "Sem base", counts.failed_publications ? "warn" : "ok"],
  ];
  $("#pipeline").innerHTML = stages
    .map(
      ([title, value, label, meta, kind]) => `
        <div class="pipeline-step">
          <div class="pipeline-meta">${dot(kind)}<span>${escapeHtml(label)}</span></div>
          <strong>${escapeHtml(title)}</strong>
          <span class="pipeline-value">${number(value)}</span>
          <p>${escapeHtml(meta)}</p>
        </div>
      `,
    )
    .join("");
}

function renderAutomation(settings, latestScan) {
  const nextRun = latestScan?.started_at
    ? new Date(new Date(latestScan.started_at).getTime() + Number(settings.scan_interval_minutes || 0) * 60000)
    : null;
  const nextRunLabel = nextRun && nextRun.getTime() > Date.now() ? dateTime(nextRun) : "Aguardando novo ciclo";
  const isDryRun = Boolean(settings.dry_run);
  const approval = Boolean(settings.require_approval);
  const active = Boolean(settings.run_scan_on_startup || latestScan);
  $("#automation-card").innerHTML = `
    <div class="automation-state">
      <div>
        <h3>Automacao</h3>
        <strong>${active ? "Configurada" : "Manual"}</strong>
      </div>
      <span class="status-badge ${active ? "ok" : "warn"}">${dot(active ? "ok" : "warn")}${active ? "Ativa" : "Pausada"}</span>
    </div>
    <div class="automation-grid">
      ${settingCard("Proxima execucao", nextRun ? nextRunLabel : "Indisponivel", "Previsao baseada no ultimo ciclo")}
      ${settingCard("Modo de teste", isDryRun ? "Ativo" : "Desativado", "DRY_RUN", isDryRun ? "warn" : "ok")}
      ${settingCard("Aprovacao automatica", approval ? "Desativada" : "Ativa", "REQUIRE_APPROVAL", approval ? "warn" : "ok")}
      ${settingCard("Intervalo", `${settings.scan_interval_minutes} minutos`, "Entre ciclos")}
      ${settingCard("Ultimo ciclo", latestScan ? dateTime(latestScan.finished_at || latestScan.started_at) : "Sem dados", latestScan ? scanStatus(latestScan).label : "Nenhum ciclo")}
      ${settingCard("Telegram", settings.telegram_token_configured ? "Configurado" : isDryRun ? "Modo teste" : "Nao configurado", "Envio de mensagens", settings.telegram_token_configured || isDryRun ? "ok" : "err")}
      ${settingCard("Banco de dados", databaseLabel(settings.database_url), "Persistencia")}
      ${settingCard("Fontes", settings.marketplace_sources || "-", "Marketplaces")}
    </div>
  `;
}

function settingCard(label, value, description = "", kind = "") {
  return `
    <div class="setting-card ${kind}">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
      ${description ? `<p>${escapeHtml(description)}</p>` : ""}
    </div>
  `;
}

function databaseLabel(value) {
  if (!value) return "Nao configurado";
  if (String(value).startsWith("sqlite")) return "SQLite local";
  return "Configurado";
}

function scanStatus(row) {
  if (!row.finished_at) return { label: "Executando", kind: "info", code: "running" };
  if (row.error_count > 0 && row.collected_count === 0) return { label: "Falhou", kind: "err", code: "failed" };
  if (row.error_count > 0) return { label: "Concluido com alertas", kind: "warn", code: "warning" };
  return { label: "Concluido", kind: "ok", code: "completed" };
}

function renderScans(scans) {
  const search = $("#scan-search")?.value.trim().toLowerCase() || "";
  const status = $("#scan-status-filter")?.value || "";
  let rows = scans.filter((row) => {
    const info = scanStatus(row);
    const text = [row.id, info.label, row.error_message].join(" ").toLowerCase();
    return (!status || info.code === status) && (!search || text.includes(search));
  });
  rows = rows.sort((a, b) => new Date(b.started_at) - new Date(a.started_at));
  const page = getPagination("scans", rows.length);
  const visible = rows.slice(page.start, page.end);
  $("#scan-runs").innerHTML =
    table(
      ["ID", "Inicio", "Duracao", "Coletados", "Aprovados", "Publicados", "Ignorados", "Erros", "Status", "Acoes"],
      visible.map((row) => {
        const statusInfo = scanStatus(row);
        return `
          <tr>
            <td>#${row.id}</td>
            <td>${dateTime(row.started_at)}</td>
            <td>${duration(row.started_at, row.finished_at)}</td>
            <td>${number(row.collected_count)}</td>
            <td>${number(row.approved_count)}</td>
            <td>${number(row.published_count)}</td>
            <td>${number(row.ignored_count)}</td>
            <td>${number(row.error_count)}</td>
            <td>${pill(statusInfo.label, statusInfo.kind)}</td>
            <td><button class="button small secondary" data-view-scan="${row.id}">${icon("eye")}Detalhes</button></td>
          </tr>
        `;
      }),
    ) + pager("scans", rows.length);
}

function renderEvents(events) {
  $("#events").innerHTML = table(
    ["Quando", "Nivel", "Modulo", "Acao", "Mensagem"],
    events.map((row) => {
      const kind = row.level === "ERROR" || row.level === "CRITICAL" ? "err" : row.level === "WARNING" ? "warn" : "ok";
      return `
        <tr>
          <td>${dateTime(row.created_at)}</td>
          <td>${pill(row.level, kind)}</td>
          <td>${escapeHtml(row.module)}</td>
          <td>${escapeHtml(row.action)}</td>
          <td class="truncate" title="${attr(row.message)}">${escapeHtml(row.message)}</td>
        </tr>
      `;
    }),
  );
}

function renderRecentApprovals(rows) {
  $("#recent-approvals").innerHTML = table(
    ["Quando", "Produto", "Nicho", "Score", "Status"],
    rows.map((row) => `
      <tr>
        <td>${dateTime(row.created_at)}</td>
        <td>${escapeHtml(row.product_id)}</td>
        <td>${escapeHtml(row.niche_name)}</td>
        <td>${number(row.score)}</td>
        <td>${pill(statusLabel(row.status), statusKind(row.status))}</td>
      </tr>
    `),
  );
}

async function loadValidation() {
  const data = await api("/config/validate");
  state.validation = data;
  renderValidation();
  renderSystemStatus();
  renderConfigViews();
}

function renderValidation() {
  const checks = [...(state.validation?.checks || [])].sort((a, b) => Number(a.ok) - Number(b.ok));
  $("#validation").innerHTML = checks.length
    ? checks
        .map((item) => {
          const kind = item.ok ? "ok" : item.level === "warning" ? "warn" : "err";
          return `
            <div class="health-item">
              ${dot(kind)}
              <div>
                <strong>${friendlyCheckName(item.name)}</strong>
                <p>${escapeHtml(item.message)}</p>
              </div>
              ${pill(item.ok ? "Operacional" : item.level === "warning" ? "Atencao" : "Erro", kind)}
            </div>
          `;
        })
        .join("")
    : emptyState("Sem diagnostico disponivel.");
  renderConfigViews();
}

function friendlyCheckName(name) {
  const names = {
    data_dir: "Diretorio de dados",
    logs_dir: "Diretorio de logs",
    niches_config: "Arquivo de nichos",
    niches_yaml: "Configuracao de nichos",
    admin_api_key: "Chave administrativa",
    telegram: "Bot do Telegram",
    database: "Banco de dados",
    marketplace_sources: "Fontes de marketplace",
  };
  return names[name] || String(name).replaceAll("_", " ");
}

function productQuery() {
  const params = new URLSearchParams({ limit: "500" });
  const q = $("#product-filter").value.trim();
  const status = $("#product-status").value;
  const shipping = $("#product-shipping").value;
  const minDiscount = $("#product-min-discount").value;
  const minPrice = $("#product-min-price").value;
  const maxPrice = $("#product-max-price").value;
  if (q) params.set("q", q);
  if (status === "active") params.set("ignored", "false");
  if (status === "ignored") params.set("ignored", "true");
  if (shipping) params.set("free_shipping", shipping);
  if (minDiscount) params.set("min_discount", minDiscount);
  if (minPrice) params.set("min_price", minPrice);
  if (maxPrice) params.set("max_price", maxPrice);
  return params.toString();
}

async function loadProducts() {
  setLoading("#products-table");
  state.products = await api(`/products?${productQuery()}`);
  renderProducts();
  renderPublications();
  renderApprovals();
}

function productMap() {
  return new Map(state.products.map((item) => [item.product_id, item]));
}

function approvalMap() {
  const rows = [...state.approvals, ...(state.dashboard?.recent_approvals || [])];
  const map = new Map();
  rows.forEach((row) => {
    if (!map.has(row.product_id)) map.set(row.product_id, row);
  });
  return map;
}

function filteredProducts() {
  const marketplace = $("#product-marketplace").value.trim().toLowerCase();
  const dateFrom = $("#product-date-from").value;
  const sort = $("#product-sort").value;
  let rows = state.products.filter((row) => {
    const productDate = row.collected_at ? String(row.collected_at).slice(0, 10) : "";
    return (
      (!marketplace || String(row.marketplace || "").toLowerCase().includes(marketplace)) &&
      (!dateFrom || productDate >= dateFrom)
    );
  });
  rows = rows.sort((a, b) => {
    if (sort === "discount_desc") return toNumber(b.discount_percent) - toNumber(a.discount_percent);
    if (sort === "price_asc") return toNumber(a.current_price) - toNumber(b.current_price);
    if (sort === "price_desc") return toNumber(b.current_price) - toNumber(a.current_price);
    return new Date(b.collected_at) - new Date(a.collected_at);
  });
  return rows;
}

function renderProducts() {
  const rows = filteredProducts();
  const approvals = approvalMap();
  const page = getPagination("products", rows.length);
  const visible = rows.slice(page.start, page.end);
  $("#products-table").innerHTML =
    table(
      ["Produto", "Marketplace", "Preco original", "Preco atual", "Desconto", "Comissao", "Nicho", "Status", "Coleta", "Acoes"],
      visible.map((row) => {
        const approval = approvals.get(row.product_id);
        const pendingApproval = approval?.status === "pending";
        return `
          <tr>
            <td>
              <div class="product-cell">
                ${productImage(row.image_url, row.title)}
                <div>
                  <div class="product-title" title="${attr(row.title)}">${escapeHtml(row.title)}</div>
                  <div class="product-meta">${escapeHtml(row.product_id)} ${row.free_shipping ? "- frete gratis" : ""}</div>
                </div>
              </div>
            </td>
            <td>${escapeHtml(row.marketplace)}</td>
            <td>${money(row.original_price)}</td>
            <td><strong>${money(row.current_price)}</strong></td>
            <td>${row.discount_percent ? pill(percent(row.discount_percent), "info") : "-"}</td>
            <td>-</td>
            <td>${approval?.niche_name ? escapeHtml(approval.niche_name) : "-"}</td>
            <td>${row.ignored ? pill("Ignorado", "warn") : pill("Ativo", "ok")}</td>
            <td>${dateOnly(row.collected_at)}</td>
            <td>
              <div class="row-actions">
                <button class="icon-button small" data-view-product="${attr(row.product_id)}" aria-label="Visualizar produto">${icon("eye")}</button>
                <button class="icon-button small" data-preview="${attr(row.product_id)}" aria-label="Previa">${icon("message-square-text")}</button>
                <button class="icon-button small" data-create-affiliate="${attr(row.product_id)}" aria-label="Gerar link">${icon("link-2")}</button>
                ${pendingApproval ? `<button class="icon-button small" data-approve-product="${approval.id}" aria-label="Aprovar">${icon("badge-check")}</button>` : ""}
                <button class="icon-button small" data-publish="${attr(row.product_id)}" aria-label="Publicar">${icon("send")}</button>
                <button class="icon-button small" data-ignore="${attr(row.product_id)}" aria-label="Ignorar" ${row.ignored ? "disabled" : ""}>${icon("archive-x")}</button>
              </div>
            </td>
          </tr>
        `;
      }),
    ) + pager("products", rows.length);
  refreshIcons();
}

function productImage(url, title) {
  const safe = safeUrl(url);
  if (!safe) return `<div class="product-image image-fallback">${icon("image-off")}</div>`;
  return `<img class="product-image" src="${attr(safe)}" alt="${attr(title || "Produto")}" loading="lazy" data-image-fallback />`;
}

function renderPriceChart(history) {
  const points = history
    .map((row) => ({ price: Number(row.price), date: row.collected_at }))
    .filter((row) => Number.isFinite(row.price));
  if (points.length < 2) {
    $("#price-chart").innerHTML = emptyState("Historico insuficiente", "Sao necessarios pelo menos dois pontos de preco.");
    return;
  }
  const width = 760;
  const height = 180;
  const min = Math.min(...points.map((row) => row.price));
  const max = Math.max(...points.map((row) => row.price));
  const range = Math.max(1, max - min);
  const path = points
    .map((row, index) => {
      const x = (index / (points.length - 1)) * width;
      const y = height - ((row.price - min) / range) * (height - 24) - 12;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  $("#price-chart").innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Historico de preco" style="color: var(--primary)">
      <polyline points="${path}" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
      <text x="0" y="18" fill="currentColor">${money(max)}</text>
      <text x="0" y="${height - 6}" fill="currentColor">${money(min)}</text>
    </svg>
  `;
}

async function previewProduct(productId) {
  if (!requireAdmin()) return;
  $("#preview-output").textContent = "Carregando previa...";
  $("#price-chart").innerHTML = skeleton();
  const [data, history] = await Promise.all([
    api("/offers/preview", { method: "POST", body: JSON.stringify({ product_id: productId }) }),
    api(`/products/${encodeURIComponent(productId)}/price-history`),
  ]);
  renderPriceChart(history);
  const channels = (data.channels || [])
    .map((row) => `${row.chat_id}: ${row.can_post ? "postar" : "bloqueado"} (${row.reason})`)
    .join("\n");
  $("#preview-output").textContent = [
    `Produto: ${data.product_id}`,
    `Nicho: ${data.niche}`,
    `Score: ${data.score}`,
    `Aprovado: ${data.approved}`,
    `Afiliado: ${data.affiliate_link_found}`,
    `Link: ${data.link}`,
    "",
    channels,
    "",
    data.message_html,
  ].join("\n");
  showPage("products");
}

async function publishProduct(productId) {
  if (!requireAdmin()) return;
  if (!(await openConfirm("Publicar este produto agora?"))) return;
  const result = await api(
    `/products/${encodeURIComponent(productId)}/publish?force=true`,
    { method: "POST" },
  );
  toast(`Publicacao concluida: ${result.published ?? 0}`);
  await refreshAll();
}

async function ignoreProduct(productId) {
  if (!requireAdmin()) return;
  if (!(await openConfirm("Ignorar este produto?"))) return;
  await api(`/products/${encodeURIComponent(productId)}/ignore`, { method: "POST" });
  toast("Produto ignorado.");
  await Promise.allSettled([loadProducts(), loadDashboard()]);
}

function viewProduct(productId) {
  const product = productMap().get(productId);
  if (!product) return;
  const approval = approvalMap().get(productId);
  const url = safeUrl(product.canonical_url);
  openDrawer("Produto", product.title, `
    <div class="product-cell">
      ${productImage(product.image_url, product.title)}
      <div>
        <strong>${escapeHtml(product.title)}</strong>
        <p>${escapeHtml(product.product_id)}</p>
      </div>
    </div>
    ${drawerKv("Marketplace", product.marketplace)}
    ${drawerKv("Preco atual", money(product.current_price))}
    ${drawerKv("Preco original", money(product.original_price))}
    ${drawerKv("Desconto", product.discount_percent ? percent(product.discount_percent) : "-")}
    ${drawerKv("Nicho", approval?.niche_name || "-")}
    ${drawerKv("Vendedor", product.seller_name || "-")}
    ${drawerKv("Frete", product.free_shipping ? "Gratis" : "Pago")}
    ${drawerKv("Status", product.ignored ? "Ignorado" : "Ativo")}
    ${drawerKv("Coletado em", dateTime(product.collected_at))}
    ${url ? `<button class="button secondary" data-open-url="${attr(url)}">${icon("external-link")}Abrir produto original</button>` : ""}
  `);
}

function createAffiliateFromProduct(productId) {
  const product = productMap().get(productId);
  if (!product) return;
  showPage("affiliates");
  const form = $("#affiliate-form");
  form.elements.marketplace.value = product.marketplace || "mercadolivre";
  form.elements.product_id.value = product.product_id || "";
  form.elements.canonical_url.value = product.canonical_url || "";
  form.elements.affiliate_url.value = "";
  form.elements.affiliate_url.focus();
}

function drawerKv(label, value) {
  return `<div class="drawer-kv"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`;
}

function openDrawer(eyebrow, title, body) {
  $("#drawer-eyebrow").textContent = eyebrow;
  $("#drawer-title").textContent = title;
  $("#drawer-body").innerHTML = body;
  $("#detail-drawer").classList.add("open");
  refreshIcons();
}

function closeDrawer() {
  $("#detail-drawer").classList.remove("open");
}

async function loadApprovals(options = {}) {
  if (!state.adminAuthenticated && !options.silentAuth) {
    $("#approval-table").innerHTML = emptyState("Acesso administrativo necessario.");
    return;
  }
  const status = $("#approval-status").value;
  const path = status ? `/approvals?status=${encodeURIComponent(status)}` : "/approvals";
  const rows = await api(path, {}, { silentAuth: options.silentAuth });
  state.approvals = rows;
  state.selectedApprovals.clear();
  renderApprovals();
  renderProducts();
}

function filteredApprovals() {
  const search = $("#approval-search").value.trim().toLowerCase();
  return state.approvals.filter((row) => {
    const text = [row.product_id, row.niche_name, row.search_query, row.reason, row.status].join(" ").toLowerCase();
    return !search || text.includes(search);
  });
}

function renderApprovals() {
  const container = $("#approval-table");
  if (!container) return;
  if (!state.adminAuthenticated) {
    container.innerHTML = emptyState("Entre para revisar aprovacoes.");
    return;
  }
  const products = productMap();
  const affiliates = new Set(state.affiliates.filter((item) => item.active).map((item) => item.product_id));
  const rows = filteredApprovals();
  container.innerHTML = rows.length
    ? rows
        .map((row) => {
          const product = products.get(row.product_id);
          const title = product?.title || row.product_id;
          const originalUrl = safeUrl(product?.canonical_url);
          return `
            <article class="review-card">
              <input type="checkbox" data-select-approval="${row.id}" ${state.selectedApprovals.has(String(row.id)) ? "checked" : ""} aria-label="Selecionar aprovacao" />
              ${productImage(product?.image_url, title)}
              <div class="review-main">
                <h3 title="${attr(title)}">${escapeHtml(title)}</h3>
                <div class="review-meta">
                  ${pill(row.marketplace || product?.marketplace || "-", "neutral")}
                  ${pill(row.niche_name || "-", "info")}
                  ${pill(`Score ${row.score ?? 0}`, "neutral")}
                  ${pill(statusLabel(row.status), statusKind(row.status))}
                  ${affiliates.has(row.product_id) ? pill("Afiliado ok", "ok") : pill("Afiliado pendente", "warn")}
                </div>
                <p class="review-reason">${escapeHtml(row.reason || row.search_query || "-")}</p>
                <p class="review-reason">Preco: ${money(product?.original_price)} -> ${money(product?.current_price)} ${product?.discount_percent ? `(${percent(product.discount_percent)})` : ""}</p>
              </div>
              <div class="review-actions">
                <button class="button small secondary" data-preview="${attr(row.product_id)}">${icon("message-square-text")}Anuncio</button>
                <button class="button small secondary" data-create-affiliate="${attr(row.product_id)}">${icon("link-2")}Link</button>
                ${originalUrl ? `<button class="button small secondary" data-open-url="${attr(originalUrl)}">${icon("external-link")}Original</button>` : ""}
                <button class="button small secondary" data-approve="${row.id}">${icon("check")}Aprovar</button>
                <button class="button small danger" data-reject="${row.id}">${icon("x")}Rejeitar</button>
                <button class="button small primary" data-publish-approval="${row.id}">${icon("send")}Publicar</button>
              </div>
            </article>
          `;
        })
        .join("")
    : emptyState("Nenhuma aprovacao encontrada.");
  refreshIcons();
}

function statusLabel(status) {
  const labels = {
    pending: "Pendente",
    approved: "Aprovado",
    rejected: "Rejeitado",
    published: "Publicado",
    sent: "Enviado",
    failed: "Falhou",
    dry_run: "Dry run",
  };
  return labels[status] || status || "-";
}

function statusKind(status) {
  if (["approved", "published", "sent"].includes(status)) return "ok";
  if (["pending", "dry_run"].includes(status)) return "warn";
  if (["rejected", "failed", "error"].includes(status)) return "err";
  return "neutral";
}

async function updateApproval(id, action) {
  if (!requireAdmin()) return;
  if (action === "reject" && !(await openConfirm("Rejeitar esta aprovacao?"))) return;
  await api(`/approvals/${id}/${action}`, { method: "POST", body: JSON.stringify({ note: "" }) });
  toast(action === "approve" ? "Produto aprovado." : "Produto rejeitado.");
  await Promise.allSettled([loadApprovals(), loadDashboard()]);
}

async function publishApproval(id) {
  if (!requireAdmin()) return;
  if (!(await openConfirm("Publicar esta aprovacao agora?"))) return;
  const result = await api(`/approvals/${id}/publish`, { method: "POST" });
  toast(`Publicacao concluida: ${result.published ?? 0}`);
  await Promise.allSettled([loadApprovals(), loadDashboard(), loadPublications()]);
}

async function batchApprovals(action) {
  if (!requireAdmin()) return;
  const ids = [...state.selectedApprovals];
  if (!ids.length) {
    toast("Selecione ao menos uma aprovacao.", "warn");
    return;
  }
  const label = action === "approve" ? "aprovar" : action === "reject" ? "rejeitar" : "publicar";
  if (!(await openConfirm(`Confirmar ${label} ${ids.length} item(ns)?`))) return;
  for (const id of ids) {
    if (action === "publish") {
      await api(`/approvals/${id}/publish`, { method: "POST" });
    } else {
      await api(`/approvals/${id}/${action}`, { method: "POST", body: JSON.stringify({ note: "acao em lote" }) });
    }
  }
  toast("Acao em lote concluida.");
  await Promise.allSettled([loadApprovals(), loadDashboard(), loadPublications()]);
}

async function loadAffiliates() {
  state.affiliates = await api("/affiliate-links");
  renderAffiliates();
  renderApprovals();
  renderConfigViews();
}

function maskSecret(value) {
  const text = String(value || "");
  if (!text) return "-";
  if (text.length <= 10) return `${text.slice(0, 2)}******`;
  return `${text.slice(0, 8)}...${text.slice(-5)}`;
}

function renderAffiliates() {
  const rows = state.affiliates;
  const active = rows.filter((row) => row.active).length;
  const inactive = rows.length - active;
  const marketplaces = new Set(rows.map((row) => row.marketplace)).size;
  $("#affiliate-summary").innerHTML = [
    ["link-2", "Links gerados", rows.length, "Total cadastrado", ""],
    ["check-circle", "Links ativos", active, "Disponiveis para uso", "good"],
    ["clock", "Links pendentes", state.pending.length, "Arquivo de pendencias", state.pending.length ? "warn" : "good"],
    ["store", "Marketplaces", marketplaces, "Com links cadastrados", ""],
    ["circle-alert", "Links inativos", inactive, "Sem falhas detalhadas no endpoint", inactive ? "warn" : "good"],
  ]
    .map(([iconName, title, value, desc, kind]) => `
      <article class="metric-card ${kind}">
        <div class="metric-head"><span class="metric-icon">${icon(iconName)}</span><span class="metric-title">${escapeHtml(title)}</span></div>
        <strong class="metric-value">${number(value)}</strong>
        <p class="metric-desc">${escapeHtml(desc)}</p>
      </article>
    `)
    .join("");

  $("#affiliate-table").innerHTML = table(
    ["Marketplace", "Produto", "Identificador", "Nicho", "Status", "Atualizado", "Acoes"],
    rows.map((row) => `
      <tr>
        <td>${escapeHtml(row.marketplace)}</td>
        <td>${escapeHtml(row.product_id)}</td>
        <td class="truncate" title="Valor mascarado">${escapeHtml(maskSecret(row.affiliate_url))}</td>
        <td>${row.niche_id ?? "-"}</td>
        <td>${row.active ? pill("Ativo", "ok") : pill("Inativo", "warn")}</td>
        <td>${dateTime(row.updated_at || row.created_at)}</td>
        <td>
          <div class="row-actions">
            <button class="button small secondary" data-toggle-affiliate="${row.id}" data-active="${row.active ? "false" : "true"}">${row.active ? "Desativar" : "Ativar"}</button>
            <button class="button small danger" data-delete-affiliate="${row.id}">${icon("trash-2")}Excluir</button>
          </div>
        </td>
      </tr>
    `),
  );
  refreshIcons();
}

async function loadPending() {
  state.pending = await api("/offers/pending");
  renderPending();
  renderAffiliates();
}

function renderPending() {
  $("#pending-table").innerHTML = table(
    ["Produto", "URL", "Nicho", "Acoes"],
    state.pending.map((row) => `
      <tr>
        <td>${escapeHtml(row.product_id)}</td>
        <td class="truncate" title="${attr(row.canonical_url)}">${escapeHtml(maskSecret(row.canonical_url))}</td>
        <td>${escapeHtml(row.niche || "-")}</td>
        <td><button class="button small secondary" data-fill-pending="${attr(row.product_id)}">${icon("corner-down-left")}Usar</button></td>
      </tr>
    `),
  );
}

async function saveAffiliate(event) {
  event.preventDefault();
  if (!requireAdmin()) return;
  const form = new FormData(event.currentTarget);
  const payload = Object.fromEntries(form.entries());
  payload.active = form.get("active") === "on";
  if (payload.niche_id) payload.niche_id = Number(payload.niche_id);
  else delete payload.niche_id;
  await api("/affiliate-links", { method: "POST", body: JSON.stringify(payload) });
  event.currentTarget.reset();
  event.currentTarget.elements.marketplace.value = "mercadolivre";
  event.currentTarget.elements.active.checked = true;
  toast("Link salvo.");
  await Promise.allSettled([loadAffiliates(), loadDashboard(), loadPending()]);
}

async function toggleAffiliate(id, active) {
  if (!requireAdmin()) return;
  await api(`/affiliate-links/${id}`, { method: "PATCH", body: JSON.stringify({ active }) });
  toast("Link atualizado.");
  await loadAffiliates();
}

async function deleteAffiliate(id) {
  if (!requireAdmin()) return;
  if (!(await openConfirm("Excluir este link afiliado?"))) return;
  await api(`/affiliate-links/${id}`, { method: "DELETE" });
  toast("Link excluido.");
  await Promise.allSettled([loadAffiliates(), loadDashboard()]);
}

function fillPending(productId) {
  const row = state.pending.find((item) => item.product_id === productId);
  if (!row) return;
  const form = $("#affiliate-form");
  form.elements.marketplace.value = row.marketplace || "mercadolivre";
  form.elements.product_id.value = row.product_id || "";
  form.elements.canonical_url.value = row.canonical_url || "";
  form.elements.affiliate_url.value = row.affiliate_url || "";
  form.elements.affiliate_url.focus();
}

async function exportAffiliates() {
  if (!requireAdmin()) return;
  const response = await fetch("/affiliate-links/export", { credentials: "same-origin" });
  if (!response.ok) throw await responseError(response, "/affiliate-links/export");
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "affiliate_links.csv";
  link.click();
  URL.revokeObjectURL(url);
}

async function importAffiliates() {
  if (!requireAdmin()) return;
  await api(
    "/affiliate-links/import",
    { method: "POST", body: JSON.stringify({ csv: $("#import-csv").value }) },
  );
  $("#import-csv").value = "";
  toast("CSV importado.");
  await Promise.allSettled([loadAffiliates(), loadDashboard(), loadPending()]);
}

async function loadPublications() {
  state.publications = await api("/publications?limit=300");
  renderPublications();
}

function filteredPublications() {
  const products = productMap();
  const approvals = approvalMap();
  const channel = $("#publication-channel").value.trim().toLowerCase();
  const status = $("#publication-status").value.trim().toLowerCase();
  const marketplace = $("#publication-marketplace").value.trim().toLowerCase();
  const niche = $("#publication-niche").value.trim().toLowerCase();
  const productId = $("#publication-product").value.trim().toLowerCase();
  const dateFrom = $("#publication-date-from").value;
  return state.publications
    .filter((row) => {
      const product = products.get(row.product_id);
      const approval = approvals.get(row.product_id);
      const rowDate = (row.published_at || row.created_at || "").slice(0, 10);
      return (
        (!channel || String(row.channel_id || "").toLowerCase().includes(channel)) &&
        (!status || String(row.status || "").toLowerCase().includes(status)) &&
        (!marketplace || String(product?.marketplace || row.marketplace || "").toLowerCase().includes(marketplace)) &&
        (!niche || String(approval?.niche_name || "").toLowerCase().includes(niche)) &&
        (!productId || String(row.product_id || "").toLowerCase().includes(productId)) &&
        (!dateFrom || rowDate >= dateFrom)
      );
    })
    .sort((a, b) => new Date(b.published_at || b.created_at) - new Date(a.published_at || a.created_at));
}

function renderPublications() {
  const container = $("#publications-table");
  if (!container) return;
  const rows = filteredPublications();
  const products = productMap();
  const approvals = approvalMap();
  const page = getPagination("publications", rows.length);
  const visible = rows.slice(page.start, page.end);
  container.innerHTML =
    table(
      ["Produto", "Canal", "Data", "Status", "Mensagem", "Link", "Tentativas", "Erro", "Acoes"],
      visible.map((row) => {
        const product = products.get(row.product_id);
        const approval = approvals.get(row.product_id);
        const link = safeUrl(row.link_used);
        return `
          <tr>
            <td>
              <div class="product-title" title="${attr(product?.title || row.product_id)}">${escapeHtml(product?.title || row.product_id)}</div>
              <div class="product-meta">${escapeHtml(approval?.niche_name || product?.marketplace || "-")}</div>
            </td>
            <td>${escapeHtml(row.channel_id)}</td>
            <td>${dateTime(row.published_at || row.created_at)}</td>
            <td>${pill(statusLabel(row.status), statusKind(row.status))}${row.dry_run ? " " + pill("Teste", "warn") : ""}</td>
            <td class="truncate" title="${attr(row.reason)}">${escapeHtml(row.reason || "-")}</td>
            <td>${link ? `<button class="button small secondary" data-open-url="${attr(link)}">${icon("external-link")}Abrir</button>` : "-"}</td>
            <td>-</td>
            <td>${row.status === "failed" ? escapeHtml(row.reason || "-") : "-"}</td>
            <td>
              <div class="row-actions">
                <button class="icon-button small" data-preview="${attr(row.product_id)}" aria-label="Visualizar mensagem">${icon("eye")}</button>
                <button class="icon-button small" data-copy-publication="${attr(row.product_id)}" aria-label="Copiar mensagem">${icon("copy")}</button>
                <button class="icon-button small" data-republish="${attr(row.product_id)}" aria-label="Reenviar">${icon("send")}</button>
              </div>
            </td>
          </tr>
        `;
      }),
    ) + pager("publications", rows.length);
  refreshIcons();
}

async function copyPublication(productId) {
  if (!requireAdmin()) return;
  const data = await api("/offers/preview", { method: "POST", body: JSON.stringify({ product_id: productId }) });
  await copyText(data.message_html || "");
  toast("Mensagem copiada.");
}

async function copyText(text) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  const textarea = document.createElement("textarea");
  textarea.value = text;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  textarea.remove();
}

async function loadSources() {
  state.sources = await api("/sources");
  renderSources();
  renderConfigViews();
}

function renderSources() {
  const html = state.sources.length
    ? state.sources
        .map((row) => `
          <article class="source-card">
            <header>
              <strong>${escapeHtml(row.name)}</strong>
              ${row.supported ? pill("Operacional", "ok") : pill("Atencao", "warn")}
            </header>
            <p>${escapeHtml(row.message || "-")}</p>
            <button class="button small secondary" data-run-source-diagnostic="${attr(row.name)}">${icon("activity")}Validar</button>
          </article>
        `)
        .join("")
    : emptyState("Nenhuma fonte configurada.");
  $("#sources-table").innerHTML = html;
  $("#config-sources-table").innerHTML = html;
  refreshIcons();
}

async function loadConfig() {
  if (!requireAdmin()) return;
  const data = await api("/config/raw");
  $("#config-editor").value = data.content || "";
}

async function saveConfig() {
  if (!requireAdmin()) return;
  if (!(await openConfirm("Salvar alteracoes no niches.yml?"))) return;
  await api("/config/raw", { method: "PUT", body: JSON.stringify({ content: $("#config-editor").value }) });
  toast("Configuracao salva.");
  await Promise.allSettled([loadValidation(), loadDashboard(), loadNiches()]);
}

async function loadNiches() {
  if (!requireAdmin()) return;
  state.nichesConfig = await api("/config/niches");
  renderNiches();
}

function renderNiches() {
  const niches = state.nichesConfig?.niches || [];
  $("#niche-visual").innerHTML = niches.length
    ? niches
        .map((niche, index) => {
          const telegram = niche.telegram || {};
          const publication = niche.publication || {};
          return `
            <div class="niche-editor" data-niche-index="${index}">
              <h3>${escapeHtml(niche.name || `Nicho ${index + 1}`)}</h3>
              <div class="form-grid">
                <label>Nome<input data-field="name" value="${attr(niche.name)}" /></label>
                <label>Prioridade<input data-field="priority" type="number" value="${attr(niche.priority ?? 0)}" /></label>
                <label class="switch-line"><input data-field="enabled" type="checkbox" ${niche.enabled ? "checked" : ""} /><span>Ativo</span></label>
                <label>Canais<input data-field="chat_ids" value="${attr((telegram.chat_ids || []).join(","))}" /></label>
                <label>Cabecalho<input data-field="header" value="${attr(telegram.header || "")}" /></label>
                <label>Posts por ciclo<input data-field="max_posts_per_cycle" type="number" value="${attr(publication.max_posts_per_cycle ?? 3)}" /></label>
                <label>Segundos entre posts<input data-field="seconds_between_posts" type="number" value="${attr(publication.seconds_between_posts ?? 5)}" /></label>
                <label>Repostar apos horas<input data-field="repost_after_hours" type="number" value="${attr(publication.repost_after_hours ?? 168)}" /></label>
                <label>Queda minima %<input data-field="min_price_drop_percent" type="number" value="${attr(publication.min_price_drop_percent ?? 3)}" /></label>
              </div>
            </div>
          `;
        })
        .join("")
    : emptyState("Nenhum nicho configurado.");
}

async function saveNiches() {
  if (!requireAdmin()) return;
  if (!state.nichesConfig) await loadNiches();
  $$(".niche-editor").forEach((node) => {
    const index = Number(node.dataset.nicheIndex);
    const niche = state.nichesConfig.niches[index];
    niche.telegram = niche.telegram || {};
    niche.publication = niche.publication || {};
    niche.name = node.querySelector('[data-field="name"]').value.trim();
    niche.priority = Number(node.querySelector('[data-field="priority"]').value || 0);
    niche.enabled = node.querySelector('[data-field="enabled"]').checked;
    niche.telegram.chat_ids = node
      .querySelector('[data-field="chat_ids"]')
      .value.split(",")
      .map((item) => item.trim())
      .filter(Boolean);
    niche.telegram.header = node.querySelector('[data-field="header"]').value;
    niche.publication.max_posts_per_cycle = Number(node.querySelector('[data-field="max_posts_per_cycle"]').value || 3);
    niche.publication.seconds_between_posts = Number(node.querySelector('[data-field="seconds_between_posts"]').value || 5);
    niche.publication.repost_after_hours = Number(node.querySelector('[data-field="repost_after_hours"]').value || 168);
    niche.publication.min_price_drop_percent = Number(node.querySelector('[data-field="min_price_drop_percent"]').value || 3);
  });
  if (!(await openConfirm("Salvar editor visual de nichos?"))) return;
  await api("/config/niches", { method: "PUT", body: JSON.stringify(state.nichesConfig) });
  toast("Nichos salvos.");
  await Promise.allSettled([loadConfig(), loadValidation(), loadDashboard()]);
}

async function loadSettings(options = {}) {
  if (!state.adminAuthenticated && !options.silentAuth) return;
  const data = await api("/settings/runtime", {}, { silentAuth: options.silentAuth });
  state.settings = data;
  const form = $("#settings-form");
  Object.entries(data).forEach(([key, value]) => {
    const field = form.elements[key];
    if (!field) return;
    if (field.type === "checkbox") field.checked = Boolean(value);
    else field.value = value;
  });
  state.settingsOriginal = JSON.stringify(settingsPayload());
  $("#settings-dirty-state").textContent = "Nenhuma alteracao pendente.";
  $("#env-label").textContent = data.APP_ENV || data.app_env || "development";
  renderSettingsViews();
  renderConfigViews();
}

function settingsPayload() {
  const form = $("#settings-form");
  return {
    DRY_RUN: form.elements.DRY_RUN.checked,
    POST_WITHOUT_AFFILIATE_LINK: form.elements.POST_WITHOUT_AFFILIATE_LINK.checked,
    RUN_SCAN_ON_STARTUP: form.elements.RUN_SCAN_ON_STARTUP.checked,
    REQUIRE_APPROVAL: form.elements.REQUIRE_APPROVAL.checked,
    SCAN_INTERVAL_MINUTES: Number(form.elements.SCAN_INTERVAL_MINUTES.value || 60),
    MARKETPLACE_SOURCES: form.elements.MARKETPLACE_SOURCES.value || "mercadolivre",
  };
}

async function saveSettings(event) {
  event.preventDefault();
  if (!requireAdmin()) return;
  const payload = settingsPayload();
  await api("/settings/runtime", { method: "PATCH", body: JSON.stringify(payload) });
  toast("Ajustes salvos.");
  await Promise.allSettled([loadSettings(), loadDashboard(), loadValidation(), loadSources()]);
}

function updateSettingsDirty() {
  if (!state.settingsOriginal) return;
  const dirty = JSON.stringify(settingsPayload()) !== state.settingsOriginal;
  $("#settings-dirty-state").textContent = dirty ? "Alteracoes nao salvas." : "Nenhuma alteracao pendente.";
}

function renderSettingsViews() {
  if (!state.settings) return;
  $("#runtime-settings-view").innerHTML = [
    settingCard("Modo de teste", state.settings.DRY_RUN ? "Ativo" : "Desativado", "DRY_RUN", state.settings.DRY_RUN ? "warn" : "ok"),
    settingCard("Aprovacao manual", state.settings.REQUIRE_APPROVAL ? "Ativa" : "Desativada", "REQUIRE_APPROVAL"),
    settingCard("Intervalo", `${state.settings.SCAN_INTERVAL_MINUTES || 60} minutos`, "SCAN_INTERVAL_MINUTES"),
    settingCard("Fontes", state.settings.MARKETPLACE_SOURCES || "mercadolivre", "MARKETPLACE_SOURCES"),
  ].join("");
}

function renderConfigViews() {
  const settings = state.dashboard?.settings || {};
  const counts = state.dashboard?.counts || {};
  $("#config-summary").innerHTML = [
    settingCard("Produto", "Oferta Telegram", "Central de coleta e publicacao"),
    settingCard("Modo principal", settings.dry_run ? "Teste" : "Producao", "Baseado em DRY_RUN", settings.dry_run ? "warn" : "ok"),
    settingCard("Produtos", number(counts.products), "Total coletado"),
    settingCard("Publicacoes", number(counts.publications), "Total registrado"),
  ].join("");
  $("#automation-settings-view").innerHTML = [
    settingCard("Scan ao iniciar", settings.run_scan_on_startup ? "Ativo" : "Desativado"),
    settingCard("Intervalo", settings.scan_interval_minutes ? `${settings.scan_interval_minutes} minutos` : "-"),
    settingCard("Exigir aprovacao", settings.require_approval ? "Sim" : "Nao"),
    settingCard("Postar sem afiliado", settings.post_without_affiliate_link ? "Sim" : "Nao"),
  ].join("");
  $("#config-affiliate-view").innerHTML = [
    settingCard("Links cadastrados", number(state.affiliates.length)),
    settingCard("Links ativos", number(state.affiliates.filter((row) => row.active).length)),
    settingCard("Pendencias", number(state.pending.length)),
  ].join("");
  $("#security-view").innerHTML = [
    settingCard("Chave administrativa", settings.admin_api_key_configured ? "Configurada" : "Ausente", "Valor nunca exibido", settings.admin_api_key_configured ? "ok" : "warn"),
    settingCard("Sessao", state.adminAuthenticated ? "Ativa" : "Inativa", "Cookie HTTP-only"),
    settingCard("Telegram token", settings.telegram_token_configured ? "Configurado" : "Nao exibido", "Valor mascarado"),
  ].join("");
  $("#storage-view").innerHTML = [
    settingCard("Banco de dados", databaseLabel(settings.database_url), "DATABASE_URL"),
    settingCard("Arquivo de nichos", settings.niches_config_path ? "Configurado" : "Indisponivel", "NICHES_CONFIG_PATH"),
  ].join("");
  $("#logs-settings-view").innerHTML = [
    settingCard("Application log", "logs/application.log"),
    settingCard("Error log", "logs/errors.log"),
    settingCard("Redacao", "Ativa", "Tokens e cookies sensiveis"),
  ].join("");
}

async function testTelegram(event) {
  event.preventDefault();
  if (!requireAdmin()) return;
  const chatId = event.currentTarget.elements.chat_id.value.trim() || null;
  const result = await api("/telegram/test", {
    method: "POST",
    body: JSON.stringify({ chat_id: chatId }),
  });
  $("#telegram-test-output").textContent = JSON.stringify(result, null, 2);
}

async function loadReport(options = {}) {
  if (!state.adminAuthenticated && !options.silentAuth) return;
  state.report = await api("/reports/daily", {}, { silentAuth: options.silentAuth });
  renderReport();
}

function renderReport() {
  const report = state.report;
  if (!report) return;
  const publicationRate = report.publications ? (report.sent_publications / report.publications) * 100 : null;
  $("#report-output").innerHTML = `
    ${reportCard("repeat-2", "Ciclos 24h", report.scans, "Execucoes no periodo")}
    ${reportCard("package-search", "Produtos 24h", report.products_collected, "Coletados no periodo")}
    ${reportCard("radio", "Publicacoes 24h", report.publications, "Registros criados")}
    ${reportCard("send", "Taxa de publicacao", publicationRate === null ? "-" : percent(publicationRate), "Enviadas / publicacoes")}
    ${reportCard("badge-check", "Aprovacoes pendentes", report.pending_approvals, "Fila atual")}
    ${reportCard("flask-conical", "Dry runs", report.dry_runs, "Publicacoes de teste")}
    <section class="panel report-wide">
      <div class="section-head"><div><h3>Maiores descontos</h3><p>Produtos coletados nas ultimas 24 horas.</p></div></div>
      ${table(
        ["Produto", "Titulo", "Preco", "Desconto"],
        (report.top_discounts || []).map((row) => `
          <tr>
            <td>${escapeHtml(row.product_id)}</td>
            <td class="truncate" title="${attr(row.title)}">${escapeHtml(row.title)}</td>
            <td>${money(row.current_price)}</td>
            <td>${row.discount_percent ? pill(percent(row.discount_percent), "info") : "-"}</td>
          </tr>
        `),
      )}
    </section>
    <section class="panel report-wide">
      <div class="section-head"><div><h3>Marketplaces e nichos</h3><p>O backend atual nao retorna agregacoes por marketplace ou nicho neste relatorio.</p></div></div>
      ${emptyState("Dados agregados indisponiveis.")}
    </section>
  `;
  refreshIcons();
}

function reportCard(iconName, title, value, desc) {
  return `
    <article class="metric-card">
      <div class="metric-head"><span class="metric-icon">${icon(iconName)}</span><span class="metric-title">${escapeHtml(title)}</span></div>
      <strong class="metric-value">${typeof value === "number" ? number(value) : escapeHtml(value)}</strong>
      <p class="metric-desc">${escapeHtml(desc)}</p>
    </article>
  `;
}

async function loadLogs(options = {}) {
  if (!state.adminAuthenticated && !options.silentAuth) return;
  const kind = $("#log-kind").value;
  const data = await api(`/logs/recent?kind=${encodeURIComponent(kind)}&lines=300`, {}, { silentAuth: options.silentAuth });
  state.logs = data.lines || [];
  renderLogs();
}

function parseLogLine(line, index) {
  const match = String(line).match(/^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| ([A-Z]+) \| ([^|]+) \| (.*)$/);
  if (!match) return { index, raw: line, time: "-", level: "INFO", service: "-", message: line };
  return { index, raw: line, time: match[1], level: match[2], service: match[3].trim(), message: match[4] };
}

function renderLogs() {
  const level = $("#log-level").value;
  const search = $("#log-search").value.trim().toLowerCase();
  const rows = state.logs
    .map(parseLogLine)
    .filter((row) => (!level || row.level === level) && (!search || row.raw.toLowerCase().includes(search)));
  $("#logs-output").innerHTML = rows.length
    ? rows
        .map((row) => `
          <article class="log-line">
            <div class="log-meta">
              ${pill(row.level, statusKind(row.level === "ERROR" || row.level === "CRITICAL" ? "failed" : row.level === "WARNING" ? "pending" : "sent"))}
              <span>${escapeHtml(row.time)}</span>
              <span>${escapeHtml(row.service)}</span>
              <button class="button small secondary" data-copy-log="${row.index}">${icon("copy")}Copiar</button>
              <button class="button small secondary" data-expand-log="${row.index}">${icon("maximize-2")}Detalhes</button>
            </div>
            <div class="log-message">${escapeHtml(row.message)}</div>
          </article>
        `)
        .join("")
    : emptyState("Nenhuma linha encontrada.");
  refreshIcons();
}

async function runScan() {
  if (!requireAdmin()) return;
  if (state.scanRunning) return;
  state.scanRunning = true;
  const button = $("#run-scan");
  const original = button.innerHTML;
  button.disabled = true;
  button.classList.add("loading");
  button.innerHTML = `${icon("loader-2")}<span>Coletando ofertas...</span>`;
  refreshIcons();
  try {
    const result = await api("/jobs/scan", { method: "POST" });
    toast(`Coleta concluida: ${result.published ?? 0} publicacao(oes).`);
    await refreshAll();
  } catch (error) {
    toast(error.message, "err");
  } finally {
    state.scanRunning = false;
    button.disabled = false;
    button.classList.remove("loading");
    button.innerHTML = original;
    refreshIcons();
  }
}

function viewScan(id) {
  const row = (state.dashboard?.recent_scans || []).find((item) => String(item.id) === String(id));
  if (!row) return;
  const statusInfo = scanStatus(row);
  openDrawer("Ciclo", `Ciclo #${row.id}`, `
    ${drawerKv("Inicio", dateTime(row.started_at))}
    ${drawerKv("Fim", dateTime(row.finished_at))}
    ${drawerKv("Duracao", duration(row.started_at, row.finished_at))}
    ${drawerKv("Produtos encontrados", number(row.collected_count))}
    ${drawerKv("Produtos descartados", number(row.ignored_count))}
    ${drawerKv("Produtos aprovados", number(row.approved_count))}
    ${drawerKv("Produtos publicados", number(row.published_count))}
    ${drawerKv("Erros", number(row.error_count))}
    ${drawerKv("Status", statusInfo.label)}
    ${row.error_message ? `<pre class="logbox small">${escapeHtml(row.error_message)}</pre>` : ""}
  `);
}

function openUrl(url) {
  const safe = safeUrl(url);
  if (safe) window.open(safe, "_blank", "noopener,noreferrer");
}

function bindEvents() {
  $("#login-form").addEventListener("submit", (event) => login(event));
  $("#close-login").addEventListener("click", closeLogin);
  $("#open-login").addEventListener("click", openLogin);
  $("#logout").addEventListener("click", () => logout().catch((error) => toast(error.message, "err")));
  $("#admin-menu-button").addEventListener("click", () => $("#admin-dropdown").classList.toggle("open"));
  $("#confirm-cancel").addEventListener("click", () => closeConfirm(false));
  $("#confirm-ok").addEventListener("click", () => closeConfirm(true));
  $("#close-drawer").addEventListener("click", closeDrawer);
  $("#collapse-sidebar").addEventListener("click", () => document.body.classList.toggle("sidebar-collapsed"));
  $("#open-sidebar").addEventListener("click", () => document.body.classList.add("sidebar-open"));
  $("#mobile-scrim").addEventListener("click", () => document.body.classList.remove("sidebar-open"));
  $("#refresh-all").addEventListener("click", () => refreshAll().catch((error) => toast(error.message, "err")));
  $("#dashboard-refresh").addEventListener("click", () => refreshAll().catch((error) => toast(error.message, "err")));
  $("#run-diagnostics").addEventListener("click", () => loadValidation().then(() => toast("Diagnostico atualizado.")).catch((error) => toast(error.message, "err")));
  $("#run-scan").addEventListener("click", runScan);
  $("#reload-products").addEventListener("click", () => loadProducts().catch((error) => toast(error.message, "err")));
  $("#apply-product-filters").addEventListener("click", () => {
    state.pagination.products.page = 1;
    loadProducts().catch((error) => toast(error.message, "err"));
  });
  ["product-sort", "product-marketplace", "product-date-from"].forEach((id) => {
    $(`#${id}`).addEventListener("change", () => {
      state.pagination.products.page = 1;
      renderProducts();
    });
  });
  $("#product-filter").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      state.pagination.products.page = 1;
      loadProducts().catch((error) => toast(error.message, "err"));
    }
  });
  $("#scan-search").addEventListener("input", () => renderScans(state.dashboard?.recent_scans || []));
  $("#scan-status-filter").addEventListener("change", () => renderScans(state.dashboard?.recent_scans || []));
  $("#load-approvals").addEventListener("click", () => loadApprovals().catch((error) => toast(error.message, "err")));
  $("#approval-status").addEventListener("change", () => loadApprovals().catch((error) => toast(error.message, "err")));
  $("#approval-search").addEventListener("input", renderApprovals);
  $("#batch-approve").addEventListener("click", () => batchApprovals("approve").catch((error) => toast(error.message, "err")));
  $("#batch-reject").addEventListener("click", () => batchApprovals("reject").catch((error) => toast(error.message, "err")));
  $("#batch-publish").addEventListener("click", () => batchApprovals("publish").catch((error) => toast(error.message, "err")));
  $("#affiliate-form").addEventListener("submit", (event) => saveAffiliate(event).catch((error) => toast(error.message, "err")));
  $("#export-affiliates").addEventListener("click", () => exportAffiliates().catch((error) => toast(error.message, "err")));
  $("#import-affiliates").addEventListener("click", () => importAffiliates().catch((error) => toast(error.message, "err")));
  $("#load-publications").addEventListener("click", () => loadPublications().catch((error) => toast(error.message, "err")));
  $("#apply-publication-filters").addEventListener("click", () => {
    state.pagination.publications.page = 1;
    renderPublications();
  });
  ["publication-channel", "publication-status", "publication-marketplace", "publication-niche", "publication-product", "publication-date-from"].forEach((id) => {
    $(`#${id}`).addEventListener("input", () => {
      state.pagination.publications.page = 1;
      renderPublications();
    });
  });
  $("#load-sources").addEventListener("click", () => loadSources().then(() => toast("Fontes validadas.")).catch((error) => toast(error.message, "err")));
  $("#load-config").addEventListener("click", () => loadConfig().catch((error) => toast(error.message, "err")));
  $("#save-config").addEventListener("click", () => saveConfig().catch((error) => toast(error.message, "err")));
  $("#load-niches").addEventListener("click", () => loadNiches().catch((error) => toast(error.message, "err")));
  $("#save-niches").addEventListener("click", () => saveNiches().catch((error) => toast(error.message, "err")));
  $("#settings-form").addEventListener("submit", (event) => saveSettings(event).catch((error) => toast(error.message, "err")));
  $("#settings-form").addEventListener("input", updateSettingsDirty);
  $("#load-settings").addEventListener("click", () => loadSettings().catch((error) => toast(error.message, "err")));
  $("#telegram-test-form").addEventListener("submit", (event) => testTelegram(event).catch((error) => toast(error.message, "err")));
  $("#load-report").addEventListener("click", () => loadReport().catch((error) => toast(error.message, "err")));
  $("#load-logs").addEventListener("click", () => loadLogs().catch((error) => toast(error.message, "err")));
  $("#log-level").addEventListener("change", renderLogs);
  $("#log-search").addEventListener("input", renderLogs);
  $("#clear-log-filters").addEventListener("click", () => {
    $("#log-level").value = "";
    $("#log-search").value = "";
    renderLogs();
  });
  $("#log-autorefresh").addEventListener("change", (event) => {
    if (state.logTimer) window.clearInterval(state.logTimer);
    state.logTimer = event.currentTarget.checked
      ? window.setInterval(() => loadLogs({ silentAuth: true }).catch(() => undefined), 30000)
      : null;
  });
  document.body.addEventListener("error", handleImageError, true);
  document.body.addEventListener("change", handleChange);
  document.body.addEventListener("click", handleClick);
  document.addEventListener("click", (event) => {
    if (!event.target.closest(".admin-menu")) $("#admin-dropdown").classList.remove("open");
  });
}

function handleImageError(event) {
  const target = event.target;
  if (!(target instanceof HTMLImageElement) || !target.dataset.imageFallback) return;
  const fallback = document.createElement("div");
  fallback.className = `${target.className} image-fallback`;
  fallback.innerHTML = icon("image-off");
  target.replaceWith(fallback);
  refreshIcons();
}

function handleChange(event) {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;
  if (target.dataset.selectApproval) {
    if (target.checked) state.selectedApprovals.add(target.dataset.selectApproval);
    else state.selectedApprovals.delete(target.dataset.selectApproval);
  }
}

function handleClick(event) {
  const target = event.target.closest("button");
  if (!target) return;
  if (target.dataset.page) showPage(target.dataset.page).catch((error) => toast(error.message, "err"));
  if (target.dataset.subtab) showSubtab(target.dataset.subtab);
  if (target.dataset.viewScan) viewScan(target.dataset.viewScan);
  if (target.dataset.viewProduct) viewProduct(target.dataset.viewProduct);
  if (target.dataset.preview) previewProduct(target.dataset.preview).catch((error) => toast(error.message, "err"));
  if (target.dataset.publish) publishProduct(target.dataset.publish).catch((error) => toast(error.message, "err"));
  if (target.dataset.ignore) ignoreProduct(target.dataset.ignore).catch((error) => toast(error.message, "err"));
  if (target.dataset.createAffiliate) createAffiliateFromProduct(target.dataset.createAffiliate);
  if (target.dataset.approveProduct) updateApproval(target.dataset.approveProduct, "approve").catch((error) => toast(error.message, "err"));
  if (target.dataset.approve) updateApproval(target.dataset.approve, "approve").catch((error) => toast(error.message, "err"));
  if (target.dataset.reject) updateApproval(target.dataset.reject, "reject").catch((error) => toast(error.message, "err"));
  if (target.dataset.publishApproval) publishApproval(target.dataset.publishApproval).catch((error) => toast(error.message, "err"));
  if (target.dataset.toggleAffiliate) toggleAffiliate(target.dataset.toggleAffiliate, target.dataset.active === "true").catch((error) => toast(error.message, "err"));
  if (target.dataset.deleteAffiliate) deleteAffiliate(target.dataset.deleteAffiliate).catch((error) => toast(error.message, "err"));
  if (target.dataset.fillPending) fillPending(target.dataset.fillPending);
  if (target.dataset.copyPublication) copyPublication(target.dataset.copyPublication).catch((error) => toast(error.message, "err"));
  if (target.dataset.republish) publishProduct(target.dataset.republish).catch((error) => toast(error.message, "err"));
  if (target.dataset.openUrl) openUrl(target.dataset.openUrl);
  if (target.dataset.copyLog) copyText(state.logs[Number(target.dataset.copyLog)] || "").then(() => toast("Linha copiada."));
  if (target.dataset.expandLog) {
    const line = parseLogLine(state.logs[Number(target.dataset.expandLog)] || "", target.dataset.expandLog);
    openDrawer("Log", line.service, `
      ${drawerKv("Data", line.time)}
      ${drawerKv("Nivel", line.level)}
      ${drawerKv("Servico", line.service)}
      <pre class="logbox small">${escapeHtml(line.raw)}</pre>
    `);
  }
  if (target.dataset.pageNav) {
    const key = target.dataset.pageNav;
    state.pagination[key].page += Number(target.dataset.direction);
    if (key === "products") renderProducts();
    if (key === "scans") renderScans(state.dashboard?.recent_scans || []);
    if (key === "publications") renderPublications();
  }
  if (target.dataset.runSourceDiagnostic) {
    loadSources().then(() => toast("Fonte validada.")).catch((error) => toast(error.message, "err"));
  }
}

function showSubtab(id) {
  $$(".subtab").forEach((item) => item.classList.toggle("active", item.dataset.subtab === id));
  $$(".subpanel").forEach((item) => item.classList.toggle("active", item.id === id));
}

async function init() {
  bindEvents();
  refreshIcons();
  setLoading("#cards");
  setLoading("#validation");
  setLoading("#products-table");
  setAuthenticated(false);
  await refreshAll();
}

init().catch((error) => toast(error.message, "err"));
