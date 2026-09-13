@echo off
title MUCAMBO NEXUS - Autonomous Arbitrage Engine 24/7
echo ==============================================================================
echo    INICIANDO MUCAMBO NEXUS - SISTEMA AUTONOMO DE ARBITRAGEM 24/7
echo ==============================================================================
echo [!] Verificando ambiente Python...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado via 'py'. Por favor instale o Python.
    pause
    exit /b 1
)

echo [!] Abrindo o Painel no Navegador em http://localhost:8000 ...
start http://localhost:8000

echo [!] Executando Motor Autonomo...
py main.py

pause
