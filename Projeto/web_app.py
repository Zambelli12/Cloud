from flask import Flask, render_template_string
from sqlalchemy import create_engine, text
import os
from urllib.parse import quote_plus

app = Flask(__name__)

# --- Configuração de Conexão ---
MYSQL_HOST="inventario-a.mysql.database.azure.com"
MYSQL_USER="FeLA123"
MYSQL_PASSWORD="@Senha123"
MYSQL_DATABASE="inventario"

# Corrige a senha com @ e configura SSL (Caminho relativo)
encoded_user = quote_plus(MYSQL_USER)
encoded_password = quote_plus(MYSQL_PASSWORD)
ssl_args = {"ssl": {"ca": "certs/MysqlflexGlobalRootCA.crt.pem"}}

CONNECTION_STRING = f"mysql+pymysql://{encoded_user}:{encoded_password}@{MYSQL_HOST}:3306/{MYSQL_DATABASE}"
ENGINE = create_engine(CONNECTION_STRING, connect_args=ssl_args)

# HTML do Site (Interface Visual)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitoramento de Estoque</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body { font-family: sans-serif; background-color: #f4f7f6; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { background-color: #007bff; color: white; padding: 12px; text-align: left; }
        td { padding: 12px; border-bottom: 1px solid #ddd; }
        .alert { color: #d9534f; font-weight: bold; background: #f9d6d5; padding: 5px 10px; border-radius: 4px; }
        .ok { color: #28a745; font-weight: bold; background: #d4edda; padding: 5px 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📦 Painel de Controle de Estoque</h1>
        <table>
            <thead>
                <tr>
                    <th>Produto</th>
                    <th>Estoque Atual</th>
                    <th>Mínimo Calculado (IA)</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for item in dados %}
                <tr>
                    <td>{{ item.nome }}</td>
                    <td>{{ item.estoque }}</td>
                    <td>{{ item.minimo }}</td>
                    <td>
                        {% if item.estoque <= item.minimo %}
                            <span class="alert">⚠️ REPOR ESTOQUE</span>
                        {% else %}
                            <span class="ok">✔ NORMAL</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% if not dados %}
            <p style="text-align:center; color:gray;">Nenhum alerta calculado ainda. Aguarde o processamento.</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    try:
        # Cruza a tabela de Produtos (estoque real) com Limites (IA)
        query = text("""
            SELECT 
                p.nome, 
                p.estoque, 
                lm.LimiteMinimo 
            FROM produtos p
            JOIN limites_minimos lm ON p.id = lm.ProductID
            ORDER BY (p.estoque - lm.LimiteMinimo) ASC
        """)
        
        with ENGINE.connect() as conn:
            result = conn.execute(query).fetchall()
        
        dados = []
        for row in result:
            dados.append({
                "nome": row[0],
                "estoque": int(row[1]),
                "minimo": float(row[2])
            })
            
        return render_template_string(HTML_TEMPLATE, dados=dados)
    except Exception as e:
        return f"<h3 style='color:red'>Erro de Conexão com Banco: {e}</h3>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)