"""
EP.03.01 - Evidencia de Producto
Conversión de practica12.py a un dashboard en Streamlit
ELIZABETH RESENDIZ RAMOS IDIA 223"""

from pathlib import Path
import json

import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  
import streamlit as st

st.set_page_config(page_title="Práctica 12 - GitHub API",  layout="wide")

st.title(" Dashboard - Repositorios de Python en GitHub")



# FASE 3: LECTURA, SEGURIDAD Y LIMPIEZA

def obtener_token():
    """1. El token vive fuera del código (igual que en la práctica original)."""
    # Primero, los Secrets de Streamlit Cloud (al desplegar)
    try:
        token = st.secrets.get("GITHUB_TOKEN")
        if token:
            return str(token).strip()
    except Exception:
        pass
    # En local, el archivo Token.txt / token.txt junto a app.py
    for nombre in ("Token.txt", "token.txt"):
        token_path = Path(__file__).with_name(nombre)
        if token_path.exists():
            token = token_path.read_text(encoding="utf-8").strip()
            if token:
                return token
    return None


@st.cache_data(ttl=3600, show_spinner="Cargando datos...")
def cargar_raw_data():
    """4. La respuesta se guarda/lee de un archivo para no gastar peticiones."""
    json_file = Path(__file__).with_name("respuesta.json")

    if json_file.exists():
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f), "archivo local 'respuesta.json'"

    token = obtener_token()
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        st.warning(
            "No se encontró token (ni en Secrets ni en Token.txt/token.txt). "
            "Se consultará la API sin autenticación, con un límite menor de peticiones."
        )

    all_items = []
    # Consultamos la página 1 y la página 2 para acumular 200 registros
    for page in [1, 2]:
        url = f"https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc&per_page=100&page={page}"
        response = requests.get(url, headers=headers, timeout=30)

        # 2. Se revisa el código de estado antes de seguir
        if response.status_code == 401:
            raise SystemExit("Error 401: Token inválido o no autorizado.")
        elif response.status_code == 400:
            raise SystemExit("Error 400: Solicitud incorrecta.")
        elif response.status_code == 429:
            raise SystemExit("Error 429: Límite de peticiones excedido en GitHub.")
        elif response.status_code != 200:
            raise SystemExit(f"Error inesperado: Código de estado {response.status_code}")

        # 3. Se revisa que la respuesta sea JSON
        if "json" not in (response.headers.get("Content-Type") or ""):
            raise SystemExit("Error: La respuesta del servidor no es un JSON válido.")

        data = response.json()
        all_items.extend(data.get("items", []))

    return {"items": all_items}, "API de GitHub (páginas 1 y 2)"


try:
    raw_data, fuente = cargar_raw_data()
except SystemExit as e:
    st.error(str(e))
    st.stop()

st.success(f"Datos obtenidos desde: **{fuente}**")

# 5. Carga a Pandas y limpieza documentada
items = raw_data.get("items", [])
df = pd.DataFrame(items)

columnas = ["stargazers_count", "forks_count", "open_issues_count", "created_at"]

with st.expander("Fase 3 - Tipos de datos, valores faltantes y limpieza"):
    st.write("**Tipos de datos iniciales**")
    st.write(df[columnas].dtypes.astype(str))
    st.write("**Valores faltantes por columna**")
    st.write(df[columnas].isnull().sum())

# Limpieza y conversiones (idénticas a la práctica original)
df['created_at'] = pd.to_datetime(df['created_at'])
df['stargazers_count'] = pd.to_numeric(df['stargazers_count'], errors='coerce')
df['forks_count'] = pd.to_numeric(df['forks_count'], errors='coerce')

# Eliminar nulos si los hubiera
df = df.dropna(subset=['stargazers_count', 'forks_count', 'created_at'])

st.metric("Registros totales utilizables después de limpiar", len(df))

with st.expander("Ver los datos limpios"):
    st.dataframe(
        df[["name", "full_name", "stargazers_count", "forks_count",
            "open_issues_count", "created_at"]],
        use_container_width=True,
    )


# FASE 4: LAS CUATRO GRÁFICAS

# Paleta de colores
GRAY = '#B9C3D1'
BLUE = '#1C4C9A'
COLORS = ['#E69F00', '#56B4E9', '#009E73', '#0072B2']

# 1. Distribución
st.header("1. Gráfica de Distribución")
st.write(
    "**Pregunta que responde:** ¿Cómo se reparten los valores? "
    "¿Dónde se concentran? ¿Hay casos extremos?"
)
fig1 = plt.figure(figsize=(8, 5))
plt.hist(df['stargazers_count'], bins=15, color=BLUE, edgecolor='white')
plt.title('La mayoría de los repositorios se concentran en pocas estrellas y pocos destacan con masividad')
plt.xlabel('Número de Estrellas (Stargazers)')
plt.ylabel('Cantidad de Repositorios')
plt.tight_layout()
st.pyplot(fig1)
plt.close(fig1)


# 2. Relación
st.header("2. Gráfica de Relación")
st.write("**Pregunta que responde:** ¿Estas dos variables se mueven juntas?")
fig2 = plt.figure(figsize=(8, 5))
plt.scatter(df['stargazers_count'], df['forks_count'], color=BLUE, alpha=0.7)
plt.title('Existe una relación directa: los repositorios con más estrellas también acumulan más forks')
plt.xlabel('Número de Estrellas (Stargazers)')
plt.ylabel('Número de Forks')
plt.tight_layout()
st.pyplot(fig2)
plt.close(fig2)


# 3. Evolución
st.header("3. Gráfica de Evolución")
st.write("**Pregunta que responde:** ¿Cómo cambió esto con el tiempo?")
df['year'] = df['created_at'].dt.year
yearly_counts = df['year'].value_counts().sort_index()

fig3 = plt.figure(figsize=(8, 5))
plt.plot(yearly_counts.index, yearly_counts.values, marker='o', color=BLUE, linewidth=2)
plt.title('El volumen de creación de repositorios populares ha fluctuado a lo largo de los años')
plt.xlabel('Año de Creación')
plt.ylabel('Cantidad de Repositorios')
plt.tight_layout()
st.pyplot(fig3)
plt.close(fig3)

# 4. Comparación
st.header("4. Gráfica de Comparación")
st.write(
    "**Pregunta que responde:** ¿Qué grupo tiene más? ¿Cuál se comporta distinto?"
)
top_repos = df.head(8)
fig4 = plt.figure(figsize=(10, 5))
plt.bar(top_repos['name'], top_repos['open_issues_count'], color=COLORS[0])
plt.title('Los repositorios principales presentan diferencias marcadas en su cantidad de open issues')
plt.xlabel('Nombre del Repositorio')
plt.ylabel('Número de Open Issues')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
st.pyplot(fig4)
plt.close(fig4)


st.caption(
    "EP.03.01 - Evidencia de Producto · Conversión de practica12.py a Streamlit · "
    "Fuente: GitHub REST API - https://docs.github.com/en/rest"
)
