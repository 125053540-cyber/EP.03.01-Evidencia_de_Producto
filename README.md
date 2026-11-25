# 📊 EP.03.01 — Dashboard en Streamlit (conversión de practica12.py)

Conversión a **Streamlit** de la práctica con la **GitHub REST API**.
Se conserva la lógica original:

- **Fase 3:** el token vive fuera del código (`Token.txt` / `token.txt`),
  la respuesta se lee de `respuesta.json` para no gastar peticiones,
  se revisan los códigos de estado (401, 400, 429) y se documenta la limpieza.
- **Fase 4:** las mismas cuatro gráficas de matplotlib, con los mismos
  títulos, colores y parámetros. Solo cambia la salida:
  `plt.show()` / `plt.savefig()` → `st.pyplot(fig)`.

## Datos

- **Endpoint:** `GET https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc&per_page=100&page=1` y `page=2`
- **Registros:** 200 limpios y utilizables
- **Columnas:** `stargazers_count`, `forks_count`, `open_issues_count`, `created_at`
- `respuesta.json` se incluye en el repositorio (igual que en la práctica
  original), por lo que el dashboard desplegado lee de ahí y no depende
  de peticiones en vivo.

## Ejecutar en local (Linux)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Token

- **Local:** deja tu `Token.txt` junto a `app.py`. Está en `.gitignore`:
  **nunca lo subas a GitHub**.
- **Streamlit Cloud:** Settings → Secrets:

```toml
GITHUB_TOKEN = "tu_token_aqui"
```

Solo se usa si no existe `respuesta.json` y hay que consultar la API en vivo.

## Despliegue

1. Sube a un repositorio **público** de GitHub: `app.py`, `requirements.txt`,
   `README.md`, `.gitignore` y `respuesta.json` (sin `Token.txt`).
2. En https://share.streamlit.io → **Create app** → repo, rama `main`, `app.py`.
3. **Deploy**. El link `https://....streamlit.app` es la evidencia,
   junto con el URL del repositorio.
