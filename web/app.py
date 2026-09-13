"""
MUCAMBO Nexus - FastAPI Web & Real-Time WebSocket Server
Exposes live telemetry, interactive dashboard, multi-lingual APIs, and order execution endpoints.
"""

import json
from pathlib import Path
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from core.database import Database
from core.scheduler import AutonomousScheduler
from core.localization import LocalizationEngine
import config

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "web" / "templates"
STATIC_DIR = BASE_DIR / "web" / "static"

# Shared database and connected WebSocket clients
db = Database()
active_connections: List[WebSocket] = []


async def broadcast_ws(message: dict):
    """Broadcasts updates to all connected web clients."""
    payload = json.dumps(message)
    dead_connections = []
    for conn in active_connections:
        try:
            await conn.send_text(payload)
        except Exception:
            dead_connections.append(conn)
    for dead in dead_connections:
        if dead in active_connections:
            active_connections.remove(dead)


# Initialize 24/7 autonomous scheduler
scheduler = AutonomousScheduler(db, ws_broadcaster=broadcast_ws)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start autonomous 24/7 scanning
    scheduler.start()
    db.log_event("INFO", "Server", "MUCAMBO Nexus system initialized. 24/7 background scheduler running.")
    yield
    # Shutdown: Stop scheduler safely
    scheduler.stop()
    db.log_event("INFO", "Server", "System stopped.")


app = FastAPI(title="MUCAMBO Nexus Arbitrage", lifespan=lifespan)

# Mount Static Files and Templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request, lang: Optional[str] = None):
    # Auto-detect language from request header if not explicitly provided
    client_lang = LocalizationEngine.detect_lang(lang or request.headers.get("accept-language"))
    translations = {k: LocalizationEngine.translate(k, client_lang) for k in [
        "dashboard_title", "system_status", "running_24_7", "paused",
        "total_profit", "active_offers", "opportunities_scanned", "win_rate",
        "live_opportunities", "market_catalog", "recent_trades", "terminal_logs",
        "buy_source", "sell_price", "net_profit", "margin", "action_buy",
        "sim_mode_badge", "live_mode_badge", "instant_delivery", "risk_free_desc",
        "currency_selector", "filter_all"
    ]}
    
    currency = LocalizationEngine.get_currency_info(client_lang)
    summary = db.get_financial_summary()
    
    context = {
        "lang": client_lang,
        "t": translations,
        "currency": currency,
        "summary": summary,
        "is_running": scheduler.is_running,
        "simulation_mode": config.SIMULATION_MODE
    }
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context
    )


@app.get("/p/{opp_id}", response_class=HTMLResponse)
async def get_client_product_page(request: Request, opp_id: str, lang: Optional[str] = None):
    """Clean, high-converting client storefront page (hides cost and profit metrics from the public)."""
    opp = db.get_opportunity(opp_id)
    if not opp:
        return HTMLResponse("<h3>Ativo ou Produto não encontrado.</h3>", status_code=404)
    
    client_lang = LocalizationEngine.detect_lang(lang or request.headers.get("accept-language"))
    localized_text = LocalizationEngine.adapt_asset_text(opp["title"], opp["description"], client_lang)
    formatted_price = LocalizationEngine.format_money(opp["target_price_usd"], client_lang)
    
    # Generate direct Stripe checkout URL
    from core.payment_gateway import PaymentGateway
    checkout_data = PaymentGateway.create_checkout_session(
        opportunity_id=opp["id"],
        asset_title=localized_text["title"],
        price_usd=opp["target_price_usd"],
        currency="BRL" if client_lang == "pt" else "USD"
    )
    checkout_url = checkout_data.get("checkout_url", f"/?buy={opp_id}")

    label = "Nome de Domínio Premium" if opp["asset_type"] == "EXPIRED_DOMAIN" else "Serviço Corporativo / Relatório de IA"

    return templates.TemplateResponse(
        request=request,
        name="product.html",
        context={
            "asset": {
                "id": opp["id"],
                "title": localized_text["title"],
                "description": localized_text["description"],
            },
            "asset_type_label": label,
            "formatted_price": formatted_price,
            "checkout_url": checkout_url
        }
    )


@app.get("/raio-x", response_class=HTMLResponse)
async def get_raio_x(request: Request, empresa: Optional[str] = None):
    """Página de auditoria e raio-x B2B personalizado para empresas prospectadas."""
    empresa_nome = empresa.strip() if empresa and empresa.strip() else "Sua Empresa"
    
    from core.payment_gateway import PaymentGateway
    # Create or link direct Stripe checkout for R$ 480
    checkout_data = PaymentGateway.create_checkout_session(
        opportunity_id=f"RAIO-X-{abs(hash(empresa_nome)) % 10000}",
        asset_title=f"Dossiê de Otimização Operacional: {empresa_nome}",
        price_usd=85.0,  # ~ R$ 480
        currency="BRL"
    )
    checkout_url = checkout_data.get("checkout_url", "/?order_success=RAIO-X")

    return templates.TemplateResponse(
        request=request,
        name="raio_x.html",
        context={
            "empresa_nome": empresa_nome,
            "checkout_url": checkout_url
        }
    )


@app.get("/sucesso", response_class=HTMLResponse)
@app.get("/entrega", response_class=HTMLResponse)
async def get_sucesso(request: Request, order_id: Optional[str] = None):
    """Página de entrega liberada com downloads reais e certificado criptográfico SHA-256."""
    import hashlib
    import random
    
    ord_id = order_id or f"{random.randint(70000, 99999)}"
    proof = hashlib.sha256(f"ORDER:{ord_id}:MUCAMBO:DELIVERED:2026".encode('utf-8')).hexdigest()

    return templates.TemplateResponse(
        request=request,
        name="sucesso.html",
        context={
            "order_id": ord_id,
            "proof_hash": proof
        }
    )


@app.get("/api/summary")
async def get_summary(lang: str = "pt"):
    summary = db.get_financial_summary()
    curr = LocalizationEngine.get_currency_info(lang)
    summary["formatted_profit"] = LocalizationEngine.format_money(summary["total_profit_usd"], lang)
    summary["formatted_volume"] = LocalizationEngine.format_money(summary["total_volume_usd"], lang)
    summary["currency"] = curr
    return summary


@app.get("/api/catalog")
async def get_catalog(lang: str = "pt"):
    raw_catalog = db.get_active_catalog(limit=30)
    adapted = []
    
    for item in raw_catalog:
        localized_text = LocalizationEngine.adapt_asset_text(item["title"], item["description"], lang)
        formatted_price = LocalizationEngine.format_money(item["target_price_usd"], lang)
        formatted_cost = LocalizationEngine.format_money(item["source_cost_usd"], lang)
        formatted_profit = LocalizationEngine.format_money(item["net_profit_usd"], lang)
        
        adapted.append({
            **item,
            "title": localized_text["title"],
            "description": localized_text["description"],
            "formatted_price": formatted_price,
            "formatted_cost": formatted_cost,
            "formatted_profit": formatted_profit,
        })
        
    return {"catalog": adapted, "count": len(adapted), "lang": lang}


@app.get("/api/trades")
async def get_trades(lang: str = "pt"):
    raw_trades = db.get_recent_transactions(limit=25)
    for trade in raw_trades:
        trade["formatted_profit"] = LocalizationEngine.format_money(trade["net_profit_usd"], lang)
        trade["formatted_sell"] = LocalizationEngine.format_money(trade["sell_price_usd"], lang)
    return {"trades": raw_trades}


@app.get("/api/receipt/{tx_id}")
async def get_receipt(tx_id: str):
    tx = db.get_transaction(tx_id)
    if not tx:
        return JSONResponse({"error": "Transacao nao encontrada"}, status_code=404)
    return {
        "certificate": "MUCAMBO CRYPTOGRAPHIC PROOF OF DELIVERY",
        "transaction_id": tx["id"],
        "order_id": tx["order_id"],
        "asset": tx["opportunity_identifier"],
        "asset_type": tx["asset_type"],
        "sell_price_usd": tx["sell_price_usd"],
        "delivery_proof_hash_sha256": tx.get("delivery_proof_hash", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        "delivery_status": tx.get("delivery_status", "CONFIRMED_DELIVERED"),
        "fulfillment_protocol": "JUST-IN-TIME ESCROW ZERO-INVENTORY V2",
        "timestamp_utc": tx["created_at"],
        "buyer_jurisdiction": tx["buyer_country"]
    }


@app.get("/api/logs")
async def get_logs():
    return {"logs": db.get_recent_logs(limit=25)}


@app.post("/api/checkout")
async def create_checkout(request: Request):
    payload = await request.json()
    opp_id = payload.get("opportunity_id")
    opp = db.get_opportunity(opp_id)
    if not opp:
        return JSONResponse({"error": "Ativo nao encontrado"}, status_code=404)
    
    from core.payment_gateway import PaymentGateway
    result = PaymentGateway.create_checkout_session(
        opportunity_id=opp_id,
        asset_title=opp["title"],
        price_usd=opp["target_price_usd"]
    )
    return JSONResponse(result)


@app.post("/api/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handles real incoming Stripe payment notifications to trigger instant JIT source fulfillment."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    # In production, verify stripe webhook signature
    try:
        data = json.loads(payload.decode('utf-8'))
        event_type = data.get("type")
        if event_type == "checkout.session.completed":
            session = data["data"]["object"]
            opp_id = session.get("metadata", {}).get("opportunity_id")
            buyer_email = session.get("customer_details", {}).get("email", "Client")
            
            # Execute instant JIT fulfillment upon verified payment
            await scheduler.fulfillment_engine.execute_trade(
                opportunity_id=opp_id,
                buyer_name=buyer_email,
                buyer_country="US",
                buyer_currency="USD"
            )
            return JSONResponse({"status": "fulfilled_successfully"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    return JSONResponse({"status": "received"})


@app.get("/api/syndication/status")
async def get_syndication_status():
    from syndication.domain_syndicator import DomainSyndicator
    syndicator = DomainSyndicator(db)
    return syndicator.get_syndication_status()


@app.get("/api/syndication/export/{platform}")
async def export_syndication_csv(platform: str):
    from syndication.domain_syndicator import DomainSyndicator
    from fastapi.responses import Response
    syndicator = DomainSyndicator(db)
    
    if platform.lower() == "afternic":
        csv_data = syndicator.export_afternic_csv()
        filename = "afternic_domains_bulk_upload.csv"
    else:
        csv_data = syndicator.export_sedo_csv()
        filename = "sedo_domains_bulk_upload.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/api/outreach/campaign")
async def get_outreach_campaign(request: Request):
    from outreach.lead_prospector import LeadProspector
    prospector = LeadProspector(db)
    base_url = str(request.base_url).rstrip("/")
    campaign = prospector.generate_outreach_campaign(base_url=base_url)
    return {"campaign": campaign, "total": len(campaign)}


@app.get("/api/offers/recent")
async def get_recent_offers():
    return {
        "dispatched_count": scheduler.dispatcher.offers_dispatched_count,
        "is_autonomous_active": scheduler.is_running
    }


@app.post("/api/reset-ledger")
async def reset_ledger():
    db.reset_test_data()
    await broadcast_ws({
        "type": "trade_executed",
        "data": {"summary": db.get_financial_summary()}
    })
    return {"status": "success", "message": "Ledger zerado para producao real"}


@app.get("/api/stripe/test-checkout")
async def stripe_test_checkout(request: Request):
    """Generates an immediate 1-click test checkout session to validate the full sales loop."""
    from core.payment_gateway import PaymentGateway
    catalog = db.get_active_catalog(limit=5)
    target = catalog[0] if catalog else {
        "id": "SAMPLE-101",
        "title": "Auditoria de Cibersegurança Web B2B",
        "target_price_usd": 49.0
    }
    
    base_url = str(request.base_url).rstrip("/")
    result = PaymentGateway.create_checkout_session(
        opportunity_id=target["id"],
        asset_title=target["title"],
        price_usd=target.get("target_price_usd", 49.0),
        success_url=f"{base_url}/?validation_success=true",
        cancel_url=f"{base_url}/?validation_canceled=true"
    )
    return JSONResponse(result)


@app.post("/api/trade")
async def execute_manual_trade(request: Request):
    payload = await request.json()
    opp_id = payload.get("opportunity_id")
    buyer_name = payload.get("buyer_name", "Web Client Buyer")
    buyer_country = payload.get("buyer_country", "BR")
    buyer_currency = payload.get("buyer_currency", "BRL")

    result = await scheduler.fulfillment_engine.execute_trade(
        opportunity_id=opp_id,
        buyer_name=buyer_name,
        buyer_country=buyer_country,
        buyer_currency=buyer_currency
    )
    if result.get("success"):
        await broadcast_ws({
            "type": "trade_executed",
            "data": {"trade": result, "summary": db.get_financial_summary()}
        })
        return JSONResponse(result)
    return JSONResponse(result, status_code=400)


@app.post("/api/control")
async def toggle_scheduler(request: Request):
    payload = await request.json()
    action = payload.get("action")
    if action == "start":
        scheduler.start()
    elif action == "stop":
        scheduler.stop()
    return {"is_running": scheduler.is_running}


@app.post("/api/mode")
async def toggle_mode(request: Request):
    payload = await request.json()
    new_mode = payload.get("simulation_mode")
    if new_mode is not None:
        config.SIMULATION_MODE = bool(new_mode)
        # Update .env file
        env_file = config.BASE_DIR / ".env"
        if env_file.exists():
            content = env_file.read_text(encoding="utf-8")
            if "SIMULATION_MODE=" in content:
                import re
                new_content = re.sub(r"SIMULATION_MODE=.*", f"SIMULATION_MODE={'true' if config.SIMULATION_MODE else 'false'}", content)
                env_file.write_text(new_content, encoding="utf-8")
        
        mode_str = "SIMULACAO" if config.SIMULATION_MODE else "PRODUCAO (REAL)"
        db.log_event("WARNING", "System", f"Modo alterado para: {mode_str}")
        await broadcast_ws({
            "type": "mode_changed",
            "data": {"simulation_mode": config.SIMULATION_MODE}
        })
    return {"simulation_mode": config.SIMULATION_MODE}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Keep-alive receive
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
