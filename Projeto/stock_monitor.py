import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sqlalchemy import create_engine, text
import os
import warnings
import math
from urllib.parse import quote_plus

warnings.filterwarnings("ignore")

print("\n--- INICIANDO ROBÔ DE PREVISÃO (INTEIROS + CALIBRADO) ---")

# ===============================
# Variáveis de ambiente do Azure
# ===============================
MYSQL_HOST = os.getenv("MYSQL_HOST", "")
MYSQL_USER = os.getenv("MYSQL_USER", "")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "")

# Encode para URLs (garante que nunca seja None)
encoded_user = quote_plus(MYSQL_USER or "")
encoded_password = quote_plus(MYSQL_PASSWORD or "")

# Configuração SSL (certificado precisa estar dentro da imagem Docker)
ssl_args = {"ssl": {"ca": "certs/MysqlflexGlobalRootCA.crt.pem"}}

# ===============================
# Conexão com o banco de dados
# ===============================
CONNECTION_STRING = f"mysql+pymysql://{encoded_user}:{encoded_password}@{MYSQL_HOST}:3306/{MYSQL_DATABASE}"

try:
    ENGINE = create_engine(CONNECTION_STRING, connect_args=ssl_args)
    print(f"✔ Conectado ao Azure MySQL: {MYSQL_HOST}")
except Exception as e:
    print(f"❌ Erro Fatal de Conexão: {e}")
    exit(1)

# ===============================
# Funções
# ===============================
def get_sales_history(product_id):
    query = text("""
        SELECT DataVenda, UnidadesVendidas 
        FROM historicovendas 
        WHERE ProductID = :pid
        ORDER BY DataVenda
    """)
    try:
        with ENGINE.connect() as conn:
            df = pd.read_sql(query, conn, params={"pid": product_id}, parse_dates=['DataVenda'])

        if df.empty:
            return None

        # Agrupa por dia
        ts = df.groupby('DataVenda')['UnidadesVendidas'].sum().asfreq('D').fillna(0)
        return ts

    except Exception as e:
        print(f"Erro ao ler dados ID {product_id}: {e}")
        return None

def calculate_safe_stock(ts):
    DIAS_DE_COBERTURA = 7
    MARGEM_SEGURANCA = 0.10

    media_diaria = ts.mean()

    try:
        if len(ts) > 30:
            model = SARIMAX(ts, order=(1,1,1), seasonal_order=(0,0,0,0),
                            enforce_stationarity=False, enforce_invertibility=False)
            fit = model.fit(disp=False)
            forecast = fit.forecast(steps=DIAS_DE_COBERTURA)
            forecast[forecast < 0] = 0
            demanda_prevista = forecast.sum()
        else:
            demanda_prevista = media_diaria * DIAS_DE_COBERTURA

        limite = demanda_prevista * (1 + MARGEM_SEGURANCA)
        limite_teto = (media_diaria * DIAS_DE_COBERTURA) * 2.5
        if limite > limite_teto:
            limite = limite_teto

        return int(math.ceil(limite))

    except Exception:
        val = (media_diaria * DIAS_DE_COBERTURA) * (1 + MARGEM_SEGURANCA)
        return int(math.ceil(val))

def save_limit(pid, limit):
    try:
        with ENGINE.connect() as conn:
            conn.execute(text("DELETE FROM limites_minimos WHERE ProductID = :p"), {"p": pid})
            conn.execute(text("""
                INSERT INTO limites_minimos (ProductID, LimiteMinimo, DataCalculo)
                VALUES (:p, :l, NOW())
            """), {"p": pid, "l": limit})
            conn.commit()
        print(f"   -> Produto {pid} | Mínimo Definido: {limit}")
    except Exception as e:
        print(f"   -> Erro ao salvar: {e}")

def run_pipeline():
    print("--- Buscando produtos... ---")
    try:
        with ENGINE.connect() as conn:
            pids = [row[0] for row in conn.execute(text("SELECT id FROM produtos")).fetchall()]
    except Exception as e:
        print(f"Erro ao buscar lista de produtos: {e}")
        return

    print(f"Processando {len(pids)} produtos (Limites ajustados para 7 dias - INTEIROS).\n")
    
    for pid in pids:
        ts = get_sales_history(pid)
        if ts is not None and len(ts) > 0:
            limit = calculate_safe_stock(ts)
            save_limit(pid, limit)
        else:
            print(f"   -> Produto {pid}: Sem histórico. Definindo 0.")
            save_limit(pid, 0)

    print("\n--- CÁLCULO CONCLUÍDO ---")

# ===============================
# Execução
# ===============================
if __name__ == "__main__":
    run_pipeline()
