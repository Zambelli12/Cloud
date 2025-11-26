#!/bin/bash

echo "--- 1. Iniciando Atualização de Estoque (IA) ---"
# Tenta rodar o monitor. Se falhar, continua para o site mesmo assim.
python stock_monitor.py || echo "⚠️ Erro no cálculo, mas iniciando o site..."

echo "--- 2. Iniciando Servidor Web ---"
# Inicia o site
python web_app.py