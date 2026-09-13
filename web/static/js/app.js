// MUCAMBO Nexus - Real-Time Dashboard Controller

let currentLang = document.body.dataset.lang || 'pt';
let currentFilter = 'ALL';
let ws = null;

let outreachCampaignData = [];

document.addEventListener('DOMContentLoaded', () => {
    initWebSocket();
    refreshAllData();
    refreshOutreach();

    // Periodic backup poll in case WebSocket disconnects
    setInterval(refreshSummary, 4000);
    setInterval(refreshLogs, 3000);
});

// WebSocket Connection for instant updates
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('[WS] Connected to MUCAMBO Nexus Telemetry.');
    };

    ws.onmessage = (event) => {
        try {
            const msg = JSON.parse(event.data);
            if (msg.type === 'new_opportunities') {
                refreshCatalog();
                refreshSummary();
            } else if (msg.type === 'trade_executed') {
                refreshTrades();
                refreshSummary();
                refreshCatalog();
                refreshLogs();
            }
        } catch (e) {
            console.error('[WS] Parse error', e);
        }
    };

    ws.onclose = () => {
        console.warn('[WS] Disconnected. Retrying in 3s...');
        setTimeout(initWebSocket, 3000);
    };
}

// Data Fetching
async function refreshAllData() {
    await Promise.all([
        refreshSummary(),
        refreshCatalog(),
        refreshTrades(),
        refreshLogs()
    ]);
}

async function refreshSummary() {
    try {
        const res = await fetch(`/api/summary?lang=${currentLang}`);
        const data = await res.json();

        document.getElementById('kpiTotalProfit').textContent = data.formatted_profit || '$0.00';
        document.getElementById('kpiActiveCatalog').textContent = data.active_catalog || '0';
        document.getElementById('kpiScanned').textContent = data.total_scanned || '0';
        document.getElementById('kpiTradesCount').textContent = data.total_trades || '0';
        document.getElementById('kpiAvgMargin').textContent = `Margem média: ${data.avg_margin_pct?.toFixed(1) || 0}%`;
    } catch (e) {
        console.error('Failed to load summary', e);
    }
}

async function refreshCatalog() {
    try {
        const res = await fetch(`/api/catalog?lang=${currentLang}`);
        const data = await res.json();
        renderCatalog(data.catalog);
    } catch (e) {
        console.error('Failed to load catalog', e);
    }
}

function renderCatalog(items) {
    const container = document.getElementById('catalogContainer');
    const filtered = currentFilter === 'ALL' 
        ? items 
        : items.filter(i => i.asset_type === currentFilter);

    document.getElementById('catalogCount').textContent = filtered.length;

    if (!filtered || filtered.length === 0) {
        container.innerHTML = `<div class="empty-state">Nenhum ativo intangível nesta categoria no momento. O scanner está buscando novas oportunidades...</div>`;
        return;
    }

    container.innerHTML = filtered.map(item => {
        let badgeClass = 'badge-domain';
        let badgeLabel = 'Domínio Web';
        if (item.asset_type === 'DIGITAL_SERVICE') {
            badgeClass = 'badge-service';
            badgeLabel = 'Serviço IA / B2B';
        } else if (item.asset_type === 'PREDICTION_CONTRACT') {
            badgeClass = 'badge-prediction';
            badgeLabel = 'Mercado Preditivo';
        }

        return `
            <div class="catalog-card">
                <div class="card-top">
                    <div>
                        <span class="asset-badge ${badgeClass}">${badgeLabel}</span>
                        <h3 class="card-title">${item.title}</h3>
                    </div>
                </div>
                <p class="card-desc">${item.description}</p>
                
                <div class="financial-spread-bar">
                    <div class="spread-col">
                        <span class="label">Custo Fonte (JIT)</span>
                        <span class="val">${item.formatted_cost}</span>
                    </div>
                    <div class="spread-col">
                        <span class="label">Preço Venda</span>
                        <span class="val">${item.formatted_price}</span>
                    </div>
                    <div class="spread-col profit">
                        <span class="label">Spread (+${item.profit_margin_pct}%)</span>
                        <span class="val">${item.formatted_profit}</span>
                    </div>
                </div>

                <div class="card-actions">
                    <span class="source-route">Fonte: ${item.source_platform}</span>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn-control" style="font-size: 0.72rem; padding: 6px 10px;" onclick="copyClientLink('${item.id}')">
                            🔗 Copiar Link Cliente
                        </button>
                        <button class="btn-buy-jit" onclick="openOrderModal('${item.id}', '${item.identifier}', '${item.formatted_price}', ${item.target_price_usd}, '${item.title}')">
                            💳 Comprar Agora (Stripe)
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function copyClientLink(oppId) {
    const url = `${window.location.origin}/p/${oppId}`;
    navigator.clipboard.writeText(url);
    alert(`Link copiado com sucesso!\n\nEnvie este link para o cliente:\n${url}`);
}

async function refreshTrades() {
    try {
        const res = await fetch(`/api/trades?lang=${currentLang}`);
        const data = await res.json();
        const container = document.getElementById('tradesContainer');

        if (!data.trades || data.trades.length === 0) {
            container.innerHTML = `<div class="empty-state">Aguardando primeiras liquidações autônomas...</div>`;
            return;
        }

        container.innerHTML = data.trades.map(tx => `
            <div class="trade-row">
                <div>
                    <div class="trade-asset">${tx.opportunity_identifier}</div>
                    <div class="trade-buyer">Comprador: ${tx.buyer_country} | Latência: ${tx.execution_time_ms}ms</div>
                    <a href="javascript:void(0)" onclick="showReceiptModal('${tx.id}')" style="color: var(--accent-blue); font-size: 0.7rem; text-decoration: underline; display: inline-block; margin-top: 3px;">
                        🛡️ Ver Comprovante de Entrega (SHA-256)
                    </a>
                </div>
                <div class="trade-profit">
                    +${tx.formatted_profit}
                </div>
            </div>
        `).join('');
    } catch (e) {
        console.error('Failed to load trades', e);
    }
}

async function showReceiptModal(txId) {
    try {
        const res = await fetch(`/api/receipt/${txId}`);
        const data = await res.json();
        
        const modal = document.getElementById('orderModal');
        const modalBody = document.getElementById('modalBody');

        modalBody.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 12px; font-size: 0.85rem;">
                <div style="text-align: center; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">
                    <div style="font-size: 1.5rem;">🛡️</div>
                    <h4 style="color: var(--accent-green); margin-top: 4px;">CERTIFICADO DE ENTREGA DIGITAL</h4>
                    <p style="font-size: 0.75rem; color: var(--text-secondary);">Protocolo Just-in-Time Escrow Verificado</p>
                </div>
                <div>
                    <strong>Transação:</strong> <code>${data.transaction_id}</code><br>
                    <strong>Ordem ID:</strong> <code>${data.order_id}</code><br>
                    <strong>Ativo Intangível:</strong> <code>${data.asset}</code><br>
                    <strong>Jurisdição do Comprador:</strong> ${data.buyer_jurisdiction}<br>
                    <strong>Status da Entrega:</strong> <span style="color: var(--accent-green); font-weight: bold;">${data.delivery_status}</span><br>
                    <strong>Data/Hora UTC:</strong> ${data.timestamp_utc}
                </div>
                <div style="background: rgba(0,0,0,0.4); padding: 10px; border-radius: 6px; border: 1px dashed var(--border-color);">
                    <div style="font-size: 0.7rem; color: var(--text-secondary); margin-bottom: 4px;">HASH CRIPTOGRÁFICO DE PROVA (SHA-256):</div>
                    <code style="word-break: break-all; font-size: 0.75rem; color: var(--accent-blue);">${data.delivery_proof_hash_sha256}</code>
                </div>
                <p style="font-size: 0.75rem; color: var(--text-secondary); line-height: 1.4;">
                    Este recibo é gerado imutavelmente no momento da entrega e serve como <strong>prova irrefutável de cumprimento de pedido</strong> perante adquirentes de cartão (Stripe), bancos (PIX) e órgãos reguladores.
                </p>
                <button class="btn-control" style="width: 100%; padding: 8px;" onclick="closeOrderModal()">Fechar Comprovante</button>
            </div>
        `;
        modal.style.display = 'flex';
    } catch (e) {
        console.error('Error loading receipt', e);
    }
}

async function refreshLogs() {
    try {
        const res = await fetch('/api/logs');
        const data = await res.json();
        const container = document.getElementById('terminalLogs');

        if (!data.logs) return;

        container.innerHTML = data.logs.map(log => `
            <div class="terminal-line ${log.level}">
                [${log.timestamp.slice(11, 19)}] [${log.source}] ${log.message}
            </div>
        `).join('');
    } catch (e) {
        console.error('Failed to load logs', e);
    }
}

// Filtering
function filterCatalog(type) {
    currentFilter = type;
    document.querySelectorAll('.filter-pills .pill').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    refreshCatalog();
}

// Language / Currency switch
function changeLanguage(newLang) {
    currentLang = newLang;
    window.location.href = `/?lang=${newLang}`;
}

// Bot Control (Start / Pause)
async function toggleBot() {
    const btn = document.getElementById('toggleBotBtn');
    const statusPill = document.getElementById('statusPill');
    const isRunning = statusPill.classList.contains('active');
    const action = isRunning ? 'stop' : 'start';

    try {
        const res = await fetch('/api/control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
        });
        const data = await res.json();

        if (data.is_running) {
            statusPill.className = 'status-pill active';
            document.getElementById('statusText').textContent = 'ATIVO 24/7 (VARREDURA GLOBAL)';
            btn.textContent = 'Pausar Motor';
        } else {
            statusPill.className = 'status-pill paused';
            document.getElementById('statusText').textContent = 'PAUSADO';
            btn.textContent = 'Iniciar Motor 24/7';
        }
    } catch (e) {
        console.error('Error toggling bot', e);
    }
}

// Mode Toggle (Simulation vs Real Production)
async function toggleSimulationMode() {
    const btn = document.getElementById('modeToggleBtn');
    const isSim = btn.classList.contains('mode-sim');
    const newSimMode = !isSim;

    if (newSimMode === false) {
        const confirmed = confirm(
            "ATENÇÃO: Deseja ativar o MODO PRODUÇÃO (REAL)?\n\n" +
            "No modo real, o sistema tentará acionar compras reais de ativos usando as chaves configuradas no arquivo .env!\n" +
            "Se ainda não preencheu suas chaves de API reais, o robô operará em contingência segura."
        );
        if (!confirmed) return;
    }

    try {
        const res = await fetch('/api/mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ simulation_mode: newSimMode })
        });
        const data = await res.json();
        updateModeUI(data.simulation_mode);
    } catch (e) {
        console.error('Error toggling simulation mode', e);
    }
}

function updateModeUI(isSim) {
    const btn = document.getElementById('modeToggleBtn');
    const badge = document.getElementById('simBadge');
    if (!btn) return;

    if (isSim) {
        btn.className = 'btn-mode-toggle mode-sim';
        btn.textContent = '🧪 MODO SIMULAÇÃO';
        if (badge) {
            badge.textContent = 'MODO SIMULAÇÃO ATIVO (SEGURO)';
            badge.style.borderColor = 'rgba(157, 78, 221, 0.4)';
            badge.style.color = '#c77dff';
        }
    } else {
        btn.className = 'btn-mode-toggle mode-real';
        btn.textContent = '⚡ MODO PRODUÇÃO (REAL)';
        if (badge) {
            badge.textContent = 'MODO LIVE ATIVO (PRODUÇÃO)';
            badge.style.borderColor = '#ff477e';
            badge.style.color = '#ff477e';
        }
    }
}

// JIT Order Modal
function openOrderModal(oppId, identifier, formattedPrice, priceUsd, title) {
    const modal = document.getElementById('orderModal');
    const modalBody = document.getElementById('modalBody');

    modalBody.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 14px;">
            <p><strong>Ativo:</strong> <code>${identifier}</code></p>
            <p><strong>Preço de Venda:</strong> <span style="color: var(--accent-green); font-size: 1.2rem; font-weight: bold;">${formattedPrice}</span></p>
            <div style="background: rgba(0, 180, 216, 0.1); padding: 10px; border-radius: 6px; font-size: 0.8rem; border-left: 3px solid var(--accent-blue);">
                A compra é processada em ambiente seguro. O ativo é adquirido e transferido instantaneamente na confirmação do pagamento com certificado criptográfico.
            </div>
            
            <button class="btn-buy-jit" style="padding: 12px; font-size: 0.95rem; background: linear-gradient(90deg, #635bff, #00d2ff); color: #fff; font-weight: bold;" onclick="payWithStripe('${oppId}')">
                💳 Pagar Agora com Cartão (Stripe Checkout)
            </button>

            <div style="text-align: center; font-size: 0.75rem; color: var(--text-secondary); margin: 4px 0;">— ou para teste interno imediato —</div>

            <button class="btn-control" style="width: 100%; padding: 8px; font-size: 0.8rem;" onclick="confirmOrder('${oppId}')">
                ⚡ Executar Liquidação Direta (Interna)
            </button>
        </div>
    `;
    modal.style.display = 'flex';
}

async function payWithStripe(oppId) {
    try {
        const res = await fetch('/api/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ opportunity_id: oppId })
        });
        const data = await res.json();
        if (data.checkout_url) {
            window.location.href = data.checkout_url;
        } else {
            alert('Erro ao abrir checkout: ' + (data.error || 'Verifique as chaves'));
        }
    } catch (e) {
        console.error('Error opening Stripe checkout', e);
    }
}

function closeOrderModal() {
    document.getElementById('orderModal').style.display = 'none';
}

async function confirmOrder(oppId) {
    const buyerName = document.getElementById('buyerNameInput')?.value || 'Client';
    closeOrderModal();

    try {
        const res = await fetch('/api/trade', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                opportunity_id: oppId,
                buyer_name: buyerName,
                buyer_country: currentLang === 'pt' ? 'BR' : (currentLang === 'es' ? 'ES' : 'US'),
                buyer_currency: currentLang === 'pt' ? 'BRL' : (currentLang === 'es' ? 'EUR' : 'USD'),
            })
        });

        const data = await res.json();
        if (data.success) {
            refreshAllData();
        } else {
            alert('Falha ao liquidar ordem: ' + (data.error || 'Erro desconhecido'));
        }
    } catch (e) {
        console.error('Error confirming trade', e);
    }
}

// B2B Outreach and Syndication Handlers
async function refreshOutreach() {
    try {
        const res = await fetch('/api/outreach/campaign');
        const data = await res.json();
        outreachCampaignData = data.campaign || [];
        const container = document.getElementById('outreachContainer');

        if (!outreachCampaignData || outreachCampaignData.length === 0) {
            container.innerHTML = `<div class="empty-state">Gerando alvos corporativos...</div>`;
            return;
        }

        container.innerHTML = outreachCampaignData.map((item, idx) => `
            <div class="outreach-row">
                <div>
                    <strong>${item.company}</strong> (${item.role})<br>
                    <span style="color: var(--text-secondary); font-size: 0.72rem;">${item.email}</span>
                </div>
                <button class="btn-copy-email" onclick="previewEmail(${idx})">
                    ✉️ Ver Proposta & Link
                </button>
            </div>
        `).join('');
    } catch (e) {
        console.error('Error loading outreach campaign', e);
    }
}

function previewEmail(idx) {
    const item = outreachCampaignData[idx];
    if (!item) return;

    const modal = document.getElementById('orderModal');
    const modalBody = document.getElementById('modalBody');

    modalBody.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 12px; font-size: 0.85rem;">
            <h4 style="color: var(--accent-blue);">Proposta Comercial Pronta (Com Link de Pagamento)</h4>
            <div>
                <strong>Para:</strong> <code>${item.email}</code><br>
                <strong>Assunto:</strong> ${item.subject}
            </div>
            <div style="background: rgba(0,0,0,0.4); padding: 12px; border-radius: 6px; font-family: var(--font-mono); font-size: 0.75rem; white-space: pre-wrap; line-height: 1.4; border: 1px solid var(--border-color); max-height: 200px; overflow-y: auto;">${item.body}</div>
            <div style="display: flex; gap: 10px;">
                <button class="btn-buy-jit" style="flex: 1;" onclick="navigator.clipboard.writeText(\`${item.body}\`); alert('E-mail copiado com sucesso!');">
                    📋 Copiar E-mail Completo
                </button>
                <button class="btn-control" onclick="closeOrderModal()">Fechar</button>
            </div>
        </div>
    `;
    modal.style.display = 'flex';
}

// 1-Click Validation Test (Stripe Test Loop)
async function triggerStripeValidation() {
    try {
        const res = await fetch('/api/stripe/test-checkout');
        const data = await res.json();

        const modal = document.getElementById('orderModal');
        const modalBody = document.getElementById('modalBody');

        if (data.mode === "REAL" && data.checkout_url) {
            window.open(data.checkout_url, '_blank');
        } else {
            modalBody.innerHTML = `
                <div style="display: flex; flex-direction: column; gap: 12px; font-size: 0.85rem;">
                    <div style="text-align: center;">
                        <span style="font-size: 2rem;">💳</span>
                        <h4 style="color: var(--accent-green); margin-top: 4px;">Validador de 1ª Venda Real (Stripe Loop)</h4>
                    </div>
                    <p style="color: var(--text-secondary); line-height: 1.4;">
                        Para realizar um teste real oficial na Stripe, você pode colocar sua chave de teste gratuita (<code>sk_test_...</code>) no arquivo <code>.env</code>.
                    </p>
                    <div style="background: rgba(99, 91, 255, 0.15); border-left: 3px solid #635bff; padding: 10px; border-radius: 6px;">
                        <strong>Cartão de Teste Oficial da Stripe:</strong><br>
                        Número: <code>4242 4242 4242 4242</code><br>
                        Validade: Qualquer data futura | CVC: <code>123</code>
                    </div>
                    <p style="font-size: 0.75rem; color: var(--text-secondary);">
                        Assim que o webhook receber a aprovação, o sistema dispara a compra na fonte e entrega instantaneamente o relatório!
                    </p>
// 1-Click Reset to Zero for Clean Real Production
async function resetLedgerToZero() {
    const confirmed = confirm("Deseja ZERAR todos os dados e transações de teste para começar do zero em R$ 0,00 reais?");
    if (!confirmed) return;

    try {
        const res = await fetch('/api/reset-ledger', { method: 'POST' });
        const data = await res.json();
        if (data.status === "success") {
            await refreshAllData();
            alert("Histórico de testes zerado com sucesso! O painel agora computará apenas vendas reais.");
        }
    } catch (e) {
        console.error('Error resetting ledger', e);
    }
}
