import re
import unicodedata
import urllib.request
from datetime import datetime
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ------------------------
# Configuracao da pagina
# ------------------------
st.set_page_config(page_title="Notícias do Agro", page_icon="🌾", layout="wide")

# Feeds RSS/Atom de noticias do agronegocio (financeiro/mercado)
FEEDS_PADRAO = {
    "AgFeed": "https://agfeed.com.br/feed/",
    "Canal Rural": "https://www.canalrural.com.br/feed/",
    "Compre Rural": "https://www.comprerural.com/feed/",
    "BeefPoint": "https://www.beefpoint.com.br/feed/",
    # CNN nao tem feed so de agro; usamos o geral + filtro "apenas agro"
    "CNN Brasil": "https://www.cnnbrasil.com.br/feed/",
    "InfoMoney": "https://www.infomoney.com.br/feed/",
    "Money Times": "https://www.moneytimes.com.br/feed/",
    # Fontes regionais do Centro-Oeste (gerais; filtro de agro seleciona)
    "Só Notícias (MT)": "https://www.sonoticias.com.br/feed/",
    "Campo Grande News (MS)": "https://www.campograndenews.com.br/rss",
    # Fontes legislativas (politica do agro; filtro de agro seleciona)
    "Agência Câmara": "https://www.camara.leg.br/noticias/rss/ultimas-noticias",
    "Agência Senado": "https://www12.senado.leg.br/noticias/rss.xml",
}

INTERVALO_PADRAO = 120  # segundos
ATOM = "{http://www.w3.org/2005/Atom}"

# Vocabulario para filtrar conteudo relevante ao agronegocio.
# Casado com limite de palavra (\b) para evitar falsos positivos
# (ex.: "gado" em "advogado", "cana" em "canal").
TERMOS_AGRO = [
    "agro", "agroneg\\w*", "agricult\\w*", "agropecuari\\w*", "fazenda\\w*",
    "rural\\w*", "lavoura\\w*", "safra\\w*", "colheita\\w*", "plantio",
    "soja", "milho", "trigo", "algodao", "cafe", "cana-de\\w*", "canavi\\w*",
    "acucar\\w*", "etanol", "boi", "boiada", "bovino\\w*", "pecuari\\w*",
    "gado", "carne\\w*", "frigorif\\w*", "leite\\w*", "graos",
    "fertilizante\\w*", "defensivo\\w*", "commodit\\w*", "cepea", "esalq",
    "conab", "embrapa", "biocombustivel\\w*", "celulose", "frango\\w*",
    "suino\\w*", "produtor\\w* rural\\w*",
    # politica do agro (para nao filtrar noticias politicas do setor)
    "ruralist\\w*", "agrari\\w*", "incra", "florestal\\w*", "desmatament\\w*",
]
_RE_AGRO = re.compile(r"\b(?:" + "|".join(TERMOS_AGRO) + r")\b")

# Classificacao por categoria (badges e filtros). Um item pode ter varias.
TERMOS_POLITICO = [
    "politic\\w*", "ministr\\w*", "ministerio", "governo", "federal",
    "deputad\\w*", "senador\\w*", "congresso", "camara", "senado", "bancada",
    "ruralist\\w*", "frente parlamentar", "plano safra", "credito rural",
    "decreto", "medida provisoria", "votac\\w*", "votad\\w*", "stf",
    "supremo", "incra", "reforma agrari\\w*", "codigo florestal",
    "planalto", "tarif\\w*", "imposto\\w*", "tributari\\w*", "embargo\\w*",
    "mercosul", "acordo comercial", "lula", "presidente",
]
TERMOS_FINANCEIRO = [
    "preco\\w*", "cotac\\w*", "dolar", "mercado\\w*", "exportac\\w*",
    "importac\\w*", "bolsa", "commodit\\w*", "alta", "queda", "credito",
    "financ\\w*", "investiment\\w*", "receita", "lucro", "faturament\\w*",
    "pib", "bilhao", "bilhoes", "milhao", "milhoes", "juros", "inflac\\w*",
    "safra", "balanca comercial", "r\\$", "us\\$",
]
TERMOS_CENTRO_OESTE = [
    "mato grosso", "goias", "distrito federal", "brasilia", "cuiaba",
    "campo grande", "goiania", "sorriso", "rondonopolis", "sinop",
    "lucas do rio verde", "primavera do leste", "dourados", "varzea grande",
    "anapolis", "rio verde", "centro-oeste", "centro oeste", "tangara",
    "nova mutum", "sao gabriel do oeste", "chapadao",
]
_RE_POLITICO = re.compile(r"\b(?:" + "|".join(TERMOS_POLITICO) + r")\b")
_RE_FINANCEIRO = re.compile(r"\b(?:" + "|".join(TERMOS_FINANCEIRO) + r")\b")
_RE_CENTRO_OESTE = re.compile(r"\b(?:" + "|".join(TERMOS_CENTRO_OESTE) + r")\b")
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


# ------------------------
# Utilitarios de texto
# ------------------------
def normalizar(texto: str) -> str:
    """Minusculas e sem acentos, para comparacao de palavras-chave."""
    if not texto:
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ASCII", "ignore").decode("ASCII")
    return texto.lower()


def parse_data(texto: str) -> datetime | None:
    if not texto:
        return None
    # RSS: RFC 822 (ex.: Mon, 23 May 2026 10:00:00 -0300)
    try:
        return parsedate_to_datetime(texto).replace(tzinfo=None)
    except (TypeError, ValueError):
        pass
    # Atom: ISO 8601 (ex.: 2026-05-23T10:00:00Z)
    try:
        return datetime.fromisoformat(texto.replace("Z", "+00:00")).replace(
            tzinfo=None
        )
    except ValueError:
        return None


# ------------------------
# Leitura de feeds (RSS 2.0 e Atom)
# ------------------------
def _texto(elemento, *tags) -> str:
    for tag in tags:
        achado = elemento.find(tag)
        if achado is not None and achado.text:
            return achado.text.strip()
    return ""


def _link_atom(entrada) -> str:
    for link in entrada.findall(f"{ATOM}link"):
        rel = link.get("rel", "alternate")
        if rel == "alternate" and link.get("href"):
            return link.get("href")
    primeiro = entrada.find(f"{ATOM}link")
    return primeiro.get("href", "") if primeiro is not None else ""


def parse_feed(conteudo: bytes, fonte: str) -> list[dict]:
    registros = []
    try:
        raiz = ET.fromstring(conteudo)
    except ET.ParseError:
        return registros

    # RSS 2.0
    for item in raiz.iter("item"):
        titulo = _texto(item, "title") or "(sem título)"
        link = _texto(item, "link")
        resumo = _texto(item, "description")
        publicado = parse_data(_texto(item, "pubDate"))
        registros.append(
            {
                "id": link or titulo,
                "fonte": fonte,
                "titulo": titulo,
                "resumo": resumo,
                "link": link,
                "publicado": publicado,
            }
        )

    # Atom
    for entrada in raiz.iter(f"{ATOM}entry"):
        titulo = _texto(entrada, f"{ATOM}title") or "(sem título)"
        link = _link_atom(entrada)
        resumo = _texto(entrada, f"{ATOM}summary", f"{ATOM}content")
        publicado = parse_data(
            _texto(entrada, f"{ATOM}published", f"{ATOM}updated")
        )
        registros.append(
            {
                "id": link or titulo,
                "fonte": fonte,
                "titulo": titulo,
                "resumo": resumo,
                "link": link,
                "publicado": publicado,
            }
        )

    return registros


@st.cache_data(ttl=60, show_spinner=False)
def carregar_feeds(feeds: tuple[tuple[str, str], ...]) -> pd.DataFrame:
    """Busca e consolida as entradas dos feeds selecionados."""
    registros = []
    erros = []
    for nome, url in feeds:
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/rss+xml, application/xml, text/xml, */*",
                },
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                conteudo = resp.read()
            registros.extend(parse_feed(conteudo, nome))
        except Exception as exc:  # rede, timeout, etc.
            erros.append(f"{nome}: {exc}")

    df = pd.DataFrame(registros)
    if not df.empty:
        df = df.drop_duplicates(subset="id")
        df = df.sort_values("publicado", ascending=False, na_position="last")
        df = df.reset_index(drop=True)
    return df, erros


def filtrar(df: pd.DataFrame, termo: str) -> pd.DataFrame:
    if df.empty or not termo.strip():
        return df
    alvo = normalizar(termo)
    mask = df.apply(
        lambda r: alvo in normalizar(f"{r['titulo']} {r['resumo']}"), axis=1
    )
    return df[mask]


def casa_alerta(linha, palavras: list[str]) -> bool:
    if not palavras:
        return False
    conteudo = normalizar(f"{linha['titulo']} {linha['resumo']}")
    return any(p in conteudo for p in palavras)


def eh_do_agro(linha) -> bool:
    conteudo = normalizar(f"{linha['titulo']} {linha['resumo']}")
    return bool(_RE_AGRO.search(conteudo))


def eh_politico(linha) -> bool:
    conteudo = normalizar(f"{linha['titulo']} {linha['resumo']}")
    return bool(_RE_POLITICO.search(conteudo))


def eh_financeiro(linha) -> bool:
    conteudo = normalizar(f"{linha['titulo']} {linha['resumo']}")
    return bool(_RE_FINANCEIRO.search(conteudo))


def eh_centro_oeste(linha) -> bool:
    conteudo = normalizar(f"{linha['titulo']} {linha['resumo']}")
    return bool(_RE_CENTRO_OESTE.search(conteudo))


def categorias(linha) -> list[str]:
    cats = []
    if eh_financeiro(linha):
        cats.append("💰 Financeiro")
    if eh_politico(linha):
        cats.append("🏛️ Político")
    if eh_centro_oeste(linha):
        cats.append("📍 Centro-Oeste")
    return cats


def filtrar_agro(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    return df[df.apply(eh_do_agro, axis=1)].reset_index(drop=True)


# ------------------------
# Estado da sessao
# ------------------------
if "ids_vistos" not in st.session_state:
    st.session_state.ids_vistos = set()

# ------------------------
# Barra lateral
# ------------------------
st.sidebar.header("⚙️ Configurações")

fontes_selecionadas = st.sidebar.multiselect(
    "Fontes (feeds RSS):",
    options=list(FEEDS_PADRAO.keys()),
    default=list(FEEDS_PADRAO.keys()),
)

feed_extra = st.sidebar.text_input("Adicionar feed RSS (URL):", "")

termo_busca = st.sidebar.text_input("🔎 Buscar por termo:", "")

apenas_agro = st.sidebar.checkbox(
    "🌱 Apenas conteúdo do agro",
    value=True,
    help="Mantém só matérias sobre o agro, inclusive nas fontes regionais e "
    "gerais. Notícia geral (não-agro) do Centro-Oeste é descartada.",
)

cats_selecionadas = st.sidebar.multiselect(
    "🏷️ Filtrar por categoria do agro:",
    options=["💰 Financeiro", "🏛️ Político", "📍 Centro-Oeste"],
    default=[],
    help="Vazio = todas. As categorias sempre se aplicam dentro do agro.",
)

alertas_texto = st.sidebar.text_input(
    "🔔 Palavras-chave de alerta (separadas por vírgula):",
    "soja, milho, mato grosso, plano safra, bancada ruralista",
)
palavras_alerta = [normalizar(p) for p in alertas_texto.split(",") if p.strip()]

auto_atualizar = st.sidebar.checkbox("Atualização automática", value=True)
intervalo = st.sidebar.slider(
    "Intervalo (segundos):", 30, 600, INTERVALO_PADRAO, step=30
)

if st.sidebar.button("🔄 Atualizar agora"):
    carregar_feeds.clear()
    st.rerun()

# ------------------------
# Auto-refresh
# ------------------------
if auto_atualizar:
    st_autorefresh(interval=intervalo * 1000, key="auto_refresh_agro")

# ------------------------
# Carregamento dos dados
# ------------------------
feeds = {nome: FEEDS_PADRAO[nome] for nome in fontes_selecionadas}
if feed_extra.strip():
    feeds[feed_extra.strip()] = feed_extra.strip()

st.title("🌾 Notícias do Agro")
st.caption("Foco em agro financeiro, político e do Centro-Oeste.")
st.caption(
    f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} • "
    f"{'auto-refresh a cada ' + str(intervalo) + 's' if auto_atualizar else 'manual'}"
)

if not feeds:
    st.info("Selecione pelo menos uma fonte na barra lateral.")
    st.stop()

df, erros = carregar_feeds(tuple(feeds.items()))

if erros:
    st.warning("Algumas fontes falharam:\n\n" + "\n".join(f"- {e}" for e in erros))

if df.empty:
    st.error("Nenhuma notícia carregada. Verifique a conexão ou as fontes.")
    st.stop()

if apenas_agro:
    df = filtrar_agro(df)
    if df.empty:
        st.info("Nenhuma notícia do agro nas fontes selecionadas no momento.")
        st.stop()

if cats_selecionadas and not df.empty:
    df = df[
        df.apply(
            lambda r: bool(set(categorias(r)) & set(cats_selecionadas)), axis=1
        )
    ].reset_index(drop=True)
    if df.empty:
        st.info("Nenhuma notícia do agro nas categorias selecionadas.")
        st.stop()

# ------------------------
# Deteccao de novidades para notificacao
# ------------------------
ids_atuais = set(df["id"])
primeira_carga = len(st.session_state.ids_vistos) == 0
novos_ids = ids_atuais - st.session_state.ids_vistos

novos_relevantes = df[
    df["id"].isin(novos_ids)
    & df.apply(lambda r: casa_alerta(r, palavras_alerta), axis=1)
]

if not primeira_carga and not novos_relevantes.empty:
    for _, linha in novos_relevantes.iterrows():
        st.toast(f"🔔 {linha['fonte']}: {linha['titulo']}", icon="🌾")
    st.success(
        f"{len(novos_relevantes)} nova(s) notícia(s) relevante(s) detectada(s)!"
    )

st.session_state.ids_vistos = ids_atuais

# ------------------------
# Aplica filtro de busca e metricas
# ------------------------
df_exibir = filtrar(df, termo_busca)

col_a, col_b, col_c = st.columns(3)
col_a.metric("Notícias carregadas", len(df))
col_b.metric("Após filtro", len(df_exibir))
col_c.metric("Alertas ativos", len(palavras_alerta))

st.divider()

if df_exibir.empty:
    st.info("Nenhuma notícia corresponde ao termo buscado.")
    st.stop()

# ------------------------
# Listagem das noticias
# ------------------------
for _, linha in df_exibir.iterrows():
    destaque = casa_alerta(linha, palavras_alerta)
    eh_novo = linha["id"] in novos_ids and not primeira_carga

    marcador = ""
    if eh_novo:
        marcador += " 🆕"
    if destaque:
        marcador += " 🔔"

    publicado = linha["publicado"]
    quando = (
        publicado.strftime("%d/%m/%Y %H:%M") if pd.notna(publicado) else "—"
    )

    cats = categorias(linha)
    selo_cats = "  ".join(f"`{c}`" for c in cats)

    with st.container(border=True):
        st.markdown(f"### {linha['titulo']}{marcador}")
        legenda = f"**{linha['fonte']}** • {quando}"
        if selo_cats:
            legenda += f" • {selo_cats}"
        st.caption(legenda)
        if linha["resumo"]:
            st.write(linha["resumo"], unsafe_allow_html=True)
        if linha["link"]:
            st.markdown(f"[Ler matéria completa →]({linha['link']})")
