# -*- coding: utf-8 -*-
"""
Copa do Mundo FIFA 2026 (EUA / Canadá / México)
Página com atualização online dos jogos da fase de grupos:
- Jogos separados por dia, com o(s) canal(is) que vão transmitir
- Resultados dos jogos já encerrados
- Classificação de todos os 12 grupos (calculada automaticamente)

Execute com:  streamlit run copa_mundo_2026.py
"""

import json
import urllib.request
import urllib.parse
import unicodedata
from datetime import datetime, date, timezone, timedelta

import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------------
# Configuração da página
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Copa do Mundo 2026 - Ao Vivo",
    page_icon="🏆",
    layout="wide",
)

# Fuso de Brasília (UTC-3)
BR_TZ = timezone(timedelta(hours=-3))

# ----------------------------------------------------------------------------
# Bandeiras (emoji)
# ----------------------------------------------------------------------------
FLAGS = {
    "México": "🇲🇽", "África do Sul": "🇿🇦", "Coreia do Sul": "🇰🇷", "Tchéquia": "🇨🇿",
    "Canadá": "🇨🇦", "Bósnia": "🇧🇦", "Catar": "🇶🇦", "Suíça": "🇨🇭",
    "Brasil": "🇧🇷", "Marrocos": "🇲🇦", "Haiti": "🇭🇹", "Escócia": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "EUA": "🇺🇸", "Paraguai": "🇵🇾", "Austrália": "🇦🇺", "Turquia": "🇹🇷",
    "Alemanha": "🇩🇪", "Curaçao": "🇨🇼", "Costa do Marfim": "🇨🇮", "Equador": "🇪🇨",
    "Holanda": "🇳🇱", "Japão": "🇯🇵", "Suécia": "🇸🇪", "Tunísia": "🇹🇳",
    "Bélgica": "🇧🇪", "Egito": "🇪🇬", "Irã": "🇮🇷", "Nova Zelândia": "🇳🇿",
    "Espanha": "🇪🇸", "Cabo Verde": "🇨🇻", "Arábia Saudita": "🇸🇦", "Uruguai": "🇺🇾",
    "França": "🇫🇷", "Senegal": "🇸🇳", "Iraque": "🇮🇶", "Noruega": "🇳🇴",
    "Argentina": "🇦🇷", "Argélia": "🇩🇿", "Áustria": "🇦🇹", "Jordânia": "🇯🇴",
    "Portugal": "🇵🇹", "RD Congo": "🇨🇩", "Uzbequistão": "🇺🇿", "Colômbia": "🇨🇴",
    "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Croácia": "🇭🇷", "Gana": "🇬🇭", "Panamá": "🇵🇦",
}


def flag(team: str) -> str:
    return FLAGS.get(team, "⚽")


# ----------------------------------------------------------------------------
# Grupos
# ----------------------------------------------------------------------------
GRUPOS = {
    "A": ["México", "África do Sul", "Coreia do Sul", "Tchéquia"],
    "B": ["Canadá", "Bósnia", "Catar", "Suíça"],
    "C": ["Brasil", "Marrocos", "Haiti", "Escócia"],
    "D": ["EUA", "Paraguai", "Austrália", "Turquia"],
    "E": ["Alemanha", "Curaçao", "Costa do Marfim", "Equador"],
    "F": ["Holanda", "Japão", "Suécia", "Tunísia"],
    "G": ["Bélgica", "Egito", "Irã", "Nova Zelândia"],
    "H": ["Espanha", "Cabo Verde", "Arábia Saudita", "Uruguai"],
    "I": ["França", "Senegal", "Iraque", "Noruega"],
    "J": ["Argentina", "Argélia", "Áustria", "Jordânia"],
    "K": ["Portugal", "RD Congo", "Uzbequistão", "Colômbia"],
    "L": ["Inglaterra", "Croácia", "Gana", "Panamá"],
}

# ----------------------------------------------------------------------------
# Tabela de jogos da fase de grupos
# (data, grupo, mandante, visitante, cidade-sede)
# ----------------------------------------------------------------------------
JOGOS = [
    # ----- Rodada 1 -----
    ("2026-06-11", "A", "México", "África do Sul", "Cidade do México"),
    ("2026-06-11", "A", "Coreia do Sul", "Tchéquia", "Guadalajara"),
    ("2026-06-12", "B", "Canadá", "Bósnia", "Toronto"),
    ("2026-06-12", "D", "EUA", "Paraguai", "Los Angeles"),
    ("2026-06-13", "B", "Catar", "Suíça", "São Francisco"),
    ("2026-06-13", "C", "Brasil", "Marrocos", "Nova Jersey"),
    ("2026-06-13", "C", "Haiti", "Escócia", "Boston"),
    ("2026-06-13", "D", "Austrália", "Turquia", "Vancouver"),
    ("2026-06-14", "E", "Alemanha", "Curaçao", "Houston"),
    ("2026-06-14", "F", "Holanda", "Japão", "Dallas"),
    ("2026-06-14", "E", "Costa do Marfim", "Equador", "Filadélfia"),
    ("2026-06-14", "F", "Suécia", "Tunísia", "Monterrey"),
    ("2026-06-15", "H", "Espanha", "Cabo Verde", "Atlanta"),
    ("2026-06-15", "G", "Bélgica", "Egito", "Vancouver"),
    ("2026-06-15", "H", "Arábia Saudita", "Uruguai", "Miami"),
    ("2026-06-15", "G", "Irã", "Nova Zelândia", "Los Angeles"),
    ("2026-06-16", "I", "França", "Senegal", "Nova Jersey"),
    ("2026-06-16", "I", "Iraque", "Noruega", "Boston"),
    ("2026-06-16", "J", "Argentina", "Argélia", "Kansas City"),
    ("2026-06-16", "J", "Áustria", "Jordânia", "São Francisco"),
    ("2026-06-17", "K", "Portugal", "RD Congo", "Houston"),
    ("2026-06-17", "L", "Inglaterra", "Croácia", "Dallas"),
    ("2026-06-17", "L", "Gana", "Panamá", "Toronto"),
    ("2026-06-17", "K", "Uzbequistão", "Colômbia", "Cidade do México"),
    # ----- Rodada 2 -----
    ("2026-06-18", "A", "Tchéquia", "África do Sul", "Atlanta"),
    ("2026-06-18", "B", "Suíça", "Bósnia", "Los Angeles"),
    ("2026-06-18", "B", "Canadá", "Catar", "Vancouver"),
    ("2026-06-18", "A", "México", "Coreia do Sul", "Guadalajara"),
    ("2026-06-19", "C", "Escócia", "Marrocos", "Boston"),
    ("2026-06-19", "D", "EUA", "Austrália", "Seattle"),
    ("2026-06-19", "C", "Brasil", "Haiti", "Filadélfia"),
    ("2026-06-19", "D", "Turquia", "Paraguai", "São Francisco"),
    ("2026-06-20", "F", "Holanda", "Suécia", "Houston"),
    ("2026-06-20", "E", "Alemanha", "Costa do Marfim", "Toronto"),
    ("2026-06-20", "E", "Equador", "Curaçao", "Kansas City"),
    ("2026-06-20", "F", "Tunísia", "Japão", "Monterrey"),
    ("2026-06-21", "H", "Espanha", "Arábia Saudita", "Atlanta"),
    ("2026-06-21", "G", "Bélgica", "Irã", "Los Angeles"),
    ("2026-06-21", "H", "Uruguai", "Cabo Verde", "Miami"),
    ("2026-06-21", "G", "Nova Zelândia", "Egito", "Vancouver"),
    ("2026-06-22", "J", "Argentina", "Áustria", "Dallas"),
    ("2026-06-22", "I", "França", "Iraque", "Filadélfia"),
    ("2026-06-22", "I", "Noruega", "Senegal", "Nova Jersey"),
    ("2026-06-22", "J", "Jordânia", "Argélia", "São Francisco"),
    ("2026-06-23", "K", "Portugal", "Uzbequistão", "Houston"),
    ("2026-06-23", "L", "Inglaterra", "Gana", "Boston"),
    ("2026-06-23", "L", "Panamá", "Croácia", "Toronto"),
    ("2026-06-23", "K", "Colômbia", "RD Congo", "Guadalajara"),
    # ----- Rodada 3 -----
    ("2026-06-24", "B", "Suíça", "Canadá", "Vancouver"),
    ("2026-06-24", "B", "Bósnia", "Catar", "Seattle"),
    ("2026-06-24", "C", "Escócia", "Brasil", "Miami"),
    ("2026-06-24", "C", "Marrocos", "Haiti", "Atlanta"),
    ("2026-06-24", "A", "Tchéquia", "México", "Cidade do México"),
    ("2026-06-24", "A", "África do Sul", "Coreia do Sul", "Monterrey"),
    ("2026-06-25", "E", "Equador", "Alemanha", "Nova Jersey"),
    ("2026-06-25", "E", "Curaçao", "Costa do Marfim", "Filadélfia"),
    ("2026-06-25", "F", "Japão", "Suécia", "Dallas"),
    ("2026-06-25", "F", "Tunísia", "Holanda", "Kansas City"),
    ("2026-06-25", "D", "Turquia", "EUA", "Los Angeles"),
    ("2026-06-25", "D", "Paraguai", "Austrália", "São Francisco"),
    ("2026-06-26", "I", "Noruega", "França", "Boston"),
    ("2026-06-26", "I", "Senegal", "Iraque", "Toronto"),
    ("2026-06-26", "H", "Cabo Verde", "Arábia Saudita", "Houston"),
    ("2026-06-26", "H", "Uruguai", "Espanha", "Guadalajara"),
    ("2026-06-26", "G", "Egito", "Irã", "Seattle"),
    ("2026-06-26", "G", "Nova Zelândia", "Bélgica", "Vancouver"),
    ("2026-06-27", "L", "Panamá", "Inglaterra", "Nova Jersey"),
    ("2026-06-27", "L", "Croácia", "Gana", "Filadélfia"),
    ("2026-06-27", "K", "Colômbia", "Portugal", "Miami"),
    ("2026-06-27", "K", "RD Congo", "Uzbequistão", "Atlanta"),
    ("2026-06-27", "J", "Argélia", "Áustria", "Kansas City"),
    ("2026-06-27", "J", "Jordânia", "Argentina", "Dallas"),
]

# ----------------------------------------------------------------------------
# Resultados dos jogos já encerrados (mandante, visitante): (gols_mandante, gols_visitante)
# Atualize aqui conforme as partidas forem terminando.
# ----------------------------------------------------------------------------
RESULTADOS = {
    ("México", "África do Sul"): (2, 0),
    ("Coreia do Sul", "Tchéquia"): (2, 1),
    ("Canadá", "Bósnia"): (1, 1),
    ("EUA", "Paraguai"): (4, 1),
    ("Catar", "Suíça"): (1, 1),
    ("Brasil", "Marrocos"): (1, 1),
    ("Haiti", "Escócia"): (0, 1),
    ("Austrália", "Turquia"): (2, 0),
}

# ----------------------------------------------------------------------------
# Horário de cada jogo (horário de Brasília — BRT, UTC-3)
# Jogos entre 00h e 04h são de madrugada (dia seguinte ao da rodada).
# ----------------------------------------------------------------------------
HORARIOS = {
    # ----- Rodada 1 -----
    ("México", "África do Sul"): "18h00",
    ("Coreia do Sul", "Tchéquia"): "01h00",
    ("Canadá", "Bósnia"): "18h00",
    ("EUA", "Paraguai"): "00h00",
    ("Catar", "Suíça"): "18h00",
    ("Brasil", "Marrocos"): "19h00",
    ("Haiti", "Escócia"): "22h00",
    ("Austrália", "Turquia"): "03h00",
    ("Alemanha", "Curaçao"): "16h00",
    ("Holanda", "Japão"): "19h00",
    ("Costa do Marfim", "Equador"): "20h00",
    ("Suécia", "Tunísia"): "23h00",
    ("Espanha", "Cabo Verde"): "15h00",
    ("Bélgica", "Egito"): "18h00",
    ("Arábia Saudita", "Uruguai"): "21h00",
    ("Irã", "Nova Zelândia"): "22h00",
    ("França", "Senegal"): "18h00",
    ("Iraque", "Noruega"): "21h00",
    ("Argentina", "Argélia"): "00h00",
    ("Áustria", "Jordânia"): "03h00",
    ("Portugal", "RD Congo"): "16h00",
    ("Inglaterra", "Croácia"): "19h00",
    ("Gana", "Panamá"): "22h00",
    ("Uzbequistão", "Colômbia"): "23h00",
    # ----- Rodada 2 -----
    ("Tchéquia", "África do Sul"): "15h00",
    ("Suíça", "Bósnia"): "18h00",
    ("Canadá", "Catar"): "21h00",
    ("México", "Coreia do Sul"): "00h00",
    ("Escócia", "Marrocos"): "21h00",
    ("EUA", "Austrália"): "18h00",
    ("Brasil", "Haiti"): "23h30",
    ("Turquia", "Paraguai"): "02h00",
    ("Holanda", "Suécia"): "16h00",
    ("Alemanha", "Costa do Marfim"): "19h00",
    ("Equador", "Curaçao"): "23h00",
    ("Tunísia", "Japão"): "03h00",
    ("Espanha", "Arábia Saudita"): "15h00",
    ("Bélgica", "Irã"): "18h00",
    ("Uruguai", "Cabo Verde"): "21h00",
    ("Nova Zelândia", "Egito"): "22h00",
    ("Argentina", "Áustria"): "16h00",
    ("França", "Iraque"): "20h00",
    ("Noruega", "Senegal"): "23h00",
    ("Jordânia", "Argélia"): "02h00",
    ("Portugal", "Uzbequistão"): "16h00",
    ("Inglaterra", "Gana"): "19h00",
    ("Panamá", "Croácia"): "22h00",
    ("Colômbia", "RD Congo"): "23h00",
    # ----- Rodada 3 -----
    ("Suíça", "Canadá"): "18h00",
    ("Bósnia", "Catar"): "18h00",
    ("Escócia", "Brasil"): "21h00",
    ("Marrocos", "Haiti"): "21h00",
    ("Tchéquia", "México"): "22h00",
    ("África do Sul", "Coreia do Sul"): "22h00",
    ("Equador", "Alemanha"): "19h00",
    ("Curaçao", "Costa do Marfim"): "19h00",
    ("Japão", "Suécia"): "22h00",
    ("Tunísia", "Holanda"): "22h00",
    ("Turquia", "EUA"): "23h00",
    ("Paraguai", "Austrália"): "23h00",
    ("Noruega", "França"): "18h00",
    ("Senegal", "Iraque"): "18h00",
    ("Cabo Verde", "Arábia Saudita"): "23h00",
    ("Uruguai", "Espanha"): "23h00",
    ("Egito", "Irã"): "02h00",
    ("Nova Zelândia", "Bélgica"): "02h00",
    ("Panamá", "Inglaterra"): "20h00",
    ("Croácia", "Gana"): "20h00",
    ("Colômbia", "Portugal"): "22h30",
    ("RD Congo", "Uzbequistão"): "22h30",
    ("Argélia", "Áustria"): "23h00",
    ("Jordânia", "Argentina"): "23h00",
}

# Sedes por país (para indicar bandeira do país-sede)
SEDE_PAIS = {
    "Cidade do México": "🇲🇽 México", "Guadalajara": "🇲🇽 México", "Monterrey": "🇲🇽 México",
    "Toronto": "🇨🇦 Canadá", "Vancouver": "🇨🇦 Canadá",
    "Los Angeles": "🇺🇸 EUA", "São Francisco": "🇺🇸 EUA", "Nova Jersey": "🇺🇸 EUA",
    "Boston": "🇺🇸 EUA", "Houston": "🇺🇸 EUA", "Dallas": "🇺🇸 EUA",
    "Filadélfia": "🇺🇸 EUA", "Atlanta": "🇺🇸 EUA", "Miami": "🇺🇸 EUA",
    "Kansas City": "🇺🇸 EUA", "Seattle": "🇺🇸 EUA",
}

# Seleções com maior apelo (usadas para escolher o "jogo do dia" da Globo)
GRANDES = {
    "Brasil", "Argentina", "França", "Espanha", "Inglaterra", "Portugal",
    "Alemanha", "Holanda", "Bélgica", "Uruguai", "México", "EUA", "Croácia",
}

# Ordem de prestígio para escolher o jogo principal de cada dia (TV aberta)
_PRESTIGIO_ORDEM = [
    "Brasil", "Argentina", "França", "Espanha", "Inglaterra", "Portugal",
    "Alemanha", "Holanda", "Bélgica", "Uruguai", "Croácia", "Colômbia",
    "México", "EUA", "Marrocos", "Japão", "Senegal", "Suíça", "Equador",
    "Coreia do Sul", "Catar", "Austrália", "Noruega", "Egito", "Costa do Marfim",
]
_PRESTIGIO = {t: len(_PRESTIGIO_ORDEM) - i for i, t in enumerate(_PRESTIGIO_ORDEM)}


def _prestigio_jogo(casa, fora):
    return _PRESTIGIO.get(casa, 0) + _PRESTIGIO.get(fora, 0)


# Jogos que vão à Globo (TV aberta): a Seleção + o jogo principal de cada dia
def _calcular_jogos_globo():
    globo = set()
    por_dia = {}
    for d, g, c, f, ci in JOGOS:
        por_dia.setdefault(d, []).append((c, f))
        if "Brasil" in (c, f):
            globo.add((c, f))
    for d, confrontos in por_dia.items():
        globo.add(max(confrontos, key=lambda cf: _prestigio_jogo(*cf)))
    return globo


GLOBO_GAMES = _calcular_jogos_globo()


def canais_do_jogo(casa: str, fora: str):
    """Retorna os canais/plataformas que transmitem o jogo, em ordem de TV.

    - CazéTV (YouTube, grátis): todos os 104 jogos
    - SporTV (TV fechada): todos os jogos
    - Globo (TV aberta): jogos da Seleção + o jogo principal de cada dia
    """
    canais = []
    if (casa, fora) in GLOBO_GAMES:
        canais.append("Globo")
    canais.append("SporTV")
    canais.append("CazéTV")
    return canais


# ----------------------------------------------------------------------------
# Funções auxiliares
# ----------------------------------------------------------------------------
def _strip(txt: str) -> str:
    """Normaliza string para comparação (sem acento, minúscula)."""
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    return txt.lower().strip()


# Mapeia nomes em inglês (usados por APIs) -> nomes em português desta página
EN_PARA_PT = {
    "mexico": "México", "south africa": "África do Sul", "south korea": "Coreia do Sul",
    "korea republic": "Coreia do Sul", "czechia": "Tchéquia", "czech republic": "Tchéquia",
    "canada": "Canadá", "bosnia and herzegovina": "Bósnia", "bosnia": "Bósnia",
    "qatar": "Catar", "switzerland": "Suíça", "brazil": "Brasil", "morocco": "Marrocos",
    "haiti": "Haiti", "scotland": "Escócia", "united states": "EUA", "usa": "EUA",
    "paraguay": "Paraguai", "australia": "Austrália", "turkey": "Turquia", "turkiye": "Turquia",
    "germany": "Alemanha", "curacao": "Curaçao", "ivory coast": "Costa do Marfim",
    "cote d'ivoire": "Costa do Marfim", "ecuador": "Equador", "netherlands": "Holanda",
    "bosnia-herzegovina": "Bósnia",
    "japan": "Japão", "sweden": "Suécia", "tunisia": "Tunísia", "belgium": "Bélgica",
    "egypt": "Egito", "iran": "Irã", "new zealand": "Nova Zelândia", "spain": "Espanha",
    "cape verde": "Cabo Verde", "cabo verde": "Cabo Verde", "saudi arabia": "Arábia Saudita",
    "uruguay": "Uruguai", "france": "França", "senegal": "Senegal", "iraq": "Iraque",
    "norway": "Noruega", "argentina": "Argentina", "algeria": "Argélia", "austria": "Áustria",
    "jordan": "Jordânia", "portugal": "Portugal", "dr congo": "RD Congo",
    "congo dr": "RD Congo", "uzbekistan": "Uzbequistão", "colombia": "Colômbia",
    "england": "Inglaterra", "croatia": "Croácia", "ghana": "Gana", "panama": "Panamá",
}


# Endereço do feed público de placares da ESPN (mesmos dados dos cards do Google).
ESPN_URL = ("https://site.api.espn.com/apis/site/v2/sports/soccer/"
            "fifa.world/scoreboard?dates={data}")

# Conjunto de confrontos na orientação oficial (mandante, visitante)
CONFRONTOS = {(c, f) for _, _, c, f, _ in JOGOS}


@st.cache_data(ttl=30, show_spinner="Buscando dados ao vivo...")
def buscar_espn(_minuto):
    """Busca placares E horários oficiais no feed público da ESPN.

    Retorna (resultados, horarios):
      - resultados: {(casa, fora): (gols_casa, gols_fora, estado)} para jogos 'in'/'post'
      - horarios:   {(casa, fora): 'HHhMM'} horário de Brasília (do timestamp oficial)
    O parâmetro `_minuto` serve só para renovar o cache. Falhas de rede são
    ignoradas silenciosamente (a página usa RESULTADOS/HORARIOS como reserva).
    """
    resultados, horarios, detalhes = {}, {}, {}
    for d in sorted({x[0] for x in JOGOS}):
        url = ESPN_URL.format(data=d.replace("-", ""))
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                dados = json.loads(resp.read().decode("utf-8"))
        except Exception:
            continue
        for ev in dados.get("events", []):
            try:
                estado = ev["status"]["type"]["state"]  # pre, in, post
                cs = ev["competitions"][0]["competitors"]
                h = next(c for c in cs if c["homeAway"] == "home")
                a = next(c for c in cs if c["homeAway"] == "away")
                casa = EN_PARA_PT.get(_strip(h["team"]["displayName"]))
                fora = EN_PARA_PT.get(_strip(a["team"]["displayName"]))
                if not (casa and fora):
                    continue
                if (casa, fora) in CONFRONTOS:
                    chave, invertido = (casa, fora), False
                elif (fora, casa) in CONFRONTOS:  # orientação invertida
                    chave, invertido = (fora, casa), True
                else:
                    continue
                # Horário oficial (UTC) convertido para Brasília
                dt = datetime.fromisoformat(ev["date"].replace("Z", "+00:00")).astimezone(BR_TZ)
                horarios[chave] = f"{dt:%Hh%M}"
                # Minuto do jogo ao vivo (ex.: "30'", "Intervalo")
                if estado == "in":
                    detalhes[chave] = (ev["status"].get("displayClock") or "AO VIVO").strip()
                # Placar (apenas jogos em andamento ou encerrados)
                if estado in ("in", "post"):
                    gc, gf = h.get("score"), a.get("score")
                    if gc not in (None, "") and gf not in (None, ""):
                        gc, gf = int(gc), int(gf)
                        resultados[chave] = (gf, gc, estado) if invertido else (gc, gf, estado)
            except Exception:
                continue
    return resultados, horarios, detalhes


def obter_dados(usar_espn: bool):
    """Retorna (resultados, horarios) combinando dados manuais e do feed ESPN.

    - resultados: {(casa, fora): (gols_casa, gols_fora, estado)} (estado: 'post'/'in')
    - horarios:   {(casa, fora): 'HHhMM'} em horário de Brasília
    O feed ESPN tem prioridade sobre os valores cadastrados manualmente.
    """
    resultados = {k: (gc, gf, "post") for k, (gc, gf) in RESULTADOS.items()}
    horarios = dict(HORARIOS)
    detalhes = {}
    if usar_espn:
        r, h, dt = buscar_espn(datetime.now().strftime("%Y%m%d%H%M"))
        resultados.update(r)
        horarios.update(h)
        detalhes.update(dt)
    return resultados, horarios, detalhes


def calcular_classificacao(grupo: str, resultados: dict) -> pd.DataFrame:
    """Calcula a classificação do grupo (somente jogos ENCERRADOS contam pontos)."""
    tab = {t: dict(P=0, J=0, V=0, E=0, D=0, GP=0, GC=0) for t in GRUPOS[grupo]}
    for data, g, casa, fora, cidade in JOGOS:
        res = resultados.get((casa, fora))
        if g != grupo or res is None or res[2] != "post":
            continue
        gc, gf, _ = res
        for t, marcou, sofreu in ((casa, gc, gf), (fora, gf, gc)):
            tab[t]["J"] += 1
            tab[t]["GP"] += marcou
            tab[t]["GC"] += sofreu
        if gc > gf:
            tab[casa]["V"] += 1; tab[casa]["P"] += 3; tab[fora]["D"] += 1
        elif gc < gf:
            tab[fora]["V"] += 1; tab[fora]["P"] += 3; tab[casa]["D"] += 1
        else:
            tab[casa]["E"] += 1; tab[fora]["E"] += 1
            tab[casa]["P"] += 1; tab[fora]["P"] += 1

    linhas = []
    for t, s in tab.items():
        linhas.append({
            "Seleção": f"{flag(t)} {t}",
            "P": s["P"], "J": s["J"], "V": s["V"], "E": s["E"], "D": s["D"],
            "GP": s["GP"], "GC": s["GC"], "SG": s["GP"] - s["GC"],
        })
    df = pd.DataFrame(linhas)
    df = df.sort_values(by=["P", "SG", "GP"], ascending=False).reset_index(drop=True)
    df.index = df.index + 1
    df.index.name = "Pos"
    return df


def hora_jogo(casa: str, fora: str, horarios: dict = HORARIOS) -> str:
    """Horário de Brasília do jogo (string 'HHhMM')."""
    return horarios.get((casa, fora), "--h--")


def _chave_horario(casa: str, fora: str, horarios: dict = HORARIOS) -> int:
    """Chave para ordenar jogos do dia em ordem cronológica (madrugada por último)."""
    h = hora_jogo(casa, fora, horarios)
    try:
        hh, mm = int(h[:2]), int(h[3:5])
    except ValueError:
        return 9999
    # Jogos de madrugada (00h-05h) acontecem depois dos da noite do mesmo dia
    return hh * 60 + mm + (24 * 60 if hh < 6 else 0)


def eh_madrugada(casa: str, fora: str, horarios: dict = HORARIOS) -> bool:
    h = hora_jogo(casa, fora, horarios)
    return h[:2].isdigit() and int(h[:2]) < 6


def status_jogo(data_str: str, estado, hoje: date):
    d = datetime.strptime(data_str, "%Y-%m-%d").date()
    if estado == "in":
        return "🔴 AO VIVO"
    if estado == "post":
        return "✅ Encerrado"
    if d < hoje:
        return "⏳ Aguardando"
    if d == hoje:
        return "🟡 Hoje"
    return "🗓️ Agendado"


DIAS_SEMANA = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
MESES = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def data_formatada(data_str: str) -> str:
    d = datetime.strptime(data_str, "%Y-%m-%d").date()
    return f"{DIAS_SEMANA[d.weekday()]}, {d.day:02d} de {MESES[d.month]}"


# ----------------------------------------------------------------------------
# Barra lateral
# ----------------------------------------------------------------------------
st.sidebar.title("⚙️ Opções")
auto = st.sidebar.toggle("Atualização automática (30s)", value=True)
usar_espn = st.sidebar.toggle("Placares ao vivo (feed ESPN)", value=True,
                              help="Busca placares e jogos ao vivo no feed público da ESPN "
                                   "(os mesmos dados exibidos pelo Google). Se a rede falhar, "
                                   "a página usa os resultados cadastrados manualmente.")
if st.sidebar.button("🔄 Atualizar agora", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**📺 Onde assistir (Brasil)**\n\n"
    "- **CazéTV** (YouTube) — todos os 104 jogos, de graça\n"
    "- **Globo** (TV aberta) — principais jogos e a Seleção\n"
    "- **SporTV** (TV fechada) e **Globoplay** (streaming)\n"
    "- **SBT** e **ge tv** — jogos selecionados"
)

# ----------------------------------------------------------------------------
# Visual "Copa Tech" (CSS)
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Rajdhani:wght@500;600;700&display=swap');
:root{
  --bg:#070b16; --panel:#0f1626; --panel2:#131c30;
  --line:rgba(120,160,255,.14); --txt:#e8eefc; --muted:#8a98b8;
  --cyan:#22d3ee; --green:#22e07a; --red:#ff3b5c; --amber:#ffb020; --violet:#7c5cff;
}
.stApp{
  background:
    radial-gradient(1200px 600px at 12% -12%, rgba(124,92,255,.20), transparent 60%),
    radial-gradient(1000px 520px at 112% -2%, rgba(34,211,238,.16), transparent 55%),
    var(--bg);
}
.block-container{padding-top:1.1rem; max-width:1220px;}
/* Hero */
.hero{position:relative; border-radius:24px; padding:28px 30px; margin:2px 0 16px;
  background:linear-gradient(120deg, rgba(124,92,255,.30), rgba(34,211,238,.14) 55%, rgba(34,224,122,.12));
  border:1px solid var(--line); overflow:hidden;}
.hero:before{content:""; position:absolute; inset:0;
  background:repeating-linear-gradient(90deg, rgba(255,255,255,.045) 0 2px, transparent 2px 24px); opacity:.6;}
.hero-badge{position:relative; display:inline-block; font:700 12px/1 'Rajdhani',sans-serif; letter-spacing:3px;
  color:#06101f; background:linear-gradient(90deg,var(--cyan),var(--green)); padding:7px 13px; border-radius:999px;}
.hero h1{position:relative; font:800 46px/1 'Orbitron',sans-serif; margin:16px 0 8px; letter-spacing:2px;
  background:linear-gradient(90deg,#ffffff,#bcd3ff); -webkit-background-clip:text; background-clip:text; color:transparent;}
.hero h1 span{color:var(--cyan); -webkit-text-fill-color:var(--cyan);}
.hero-sub{position:relative; color:#c8d4f0; font:500 15px/1.4 'Rajdhani',sans-serif; letter-spacing:.4px;}
/* Stats */
.stats{display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:2px 0 8px;}
.stat{background:linear-gradient(180deg,var(--panel2),var(--panel)); border:1px solid var(--line);
  border-radius:16px; padding:14px 16px;}
.stat .v{font:800 26px/1 'Orbitron',sans-serif; color:var(--txt);}
.stat .l{color:var(--muted); font:600 11px/1 'Rajdhani',sans-serif; letter-spacing:1.5px; text-transform:uppercase; margin-top:7px;}
.stat.live{border-color:rgba(255,59,92,.45);} .stat.live .v{color:var(--red);}
/* Day header */
.dayhead{display:flex; align-items:center; gap:11px; margin:24px 0 13px;}
.dayhead .dot{width:10px; height:10px; border-radius:50%; background:var(--cyan); box-shadow:0 0 13px var(--cyan);}
.dayhead .d{font:700 18px/1 'Rajdhani',sans-serif; letter-spacing:1.5px; color:var(--txt); text-transform:uppercase;}
.dayhead .today{font:700 11px/1 'Rajdhani',sans-serif; letter-spacing:1px; color:#06101f; background:var(--amber); padding:5px 9px; border-radius:999px;}
.day-grid{display:grid; grid-template-columns:repeat(auto-fill, minmax(330px,1fr)); gap:14px;}
/* Live bar */
.livebar{display:flex; align-items:center; gap:11px; margin:4px 0 12px;
  font:800 16px/1 'Rajdhani',sans-serif; letter-spacing:2px; color:#fff; text-transform:uppercase;}
.livebar:before{content:""; width:11px; height:11px; border-radius:50%; background:var(--red);
  box-shadow:0 0 14px var(--red); animation:pulse 1.2s infinite;}
/* Match card */
.match-link{text-decoration:none; color:inherit; display:block; cursor:pointer;}
.match-link:hover{text-decoration:none;}
.match{background:linear-gradient(180deg,var(--panel2),var(--panel)); border:1px solid var(--line);
  border-radius:18px; padding:14px 16px; transition:.16s; position:relative; overflow:hidden;}
.match:hover{transform:translateY(-3px); border-color:rgba(34,211,238,.45); box-shadow:0 12px 30px rgba(0,0,0,.45);}
.match.live{border-color:rgba(255,59,92,.55); box-shadow:0 0 0 1px rgba(255,59,92,.25), 0 8px 26px rgba(255,59,92,.14);}
.match.live:before{content:""; position:absolute; left:0; top:0; bottom:0; width:3px; background:var(--red);}
.m-head{display:flex; justify-content:space-between; align-items:center; font:600 12px/1 'Rajdhani',sans-serif; color:var(--muted); letter-spacing:.5px;}
.m-status{font-weight:700; padding:4px 9px; border-radius:999px; font-size:11px; letter-spacing:.5px;}
.s-live{color:#fff; background:var(--red); animation:pulse 1.2s infinite;}
.s-post{color:var(--green); background:rgba(34,224,122,.14);}
.s-today{color:var(--amber); background:rgba(255,176,32,.14);}
.s-pre{color:var(--muted); background:rgba(138,152,184,.12);}
@keyframes pulse{0%,100%{opacity:1} 50%{opacity:.4}}
.m-body{display:grid; grid-template-columns:1fr auto 1fr; align-items:center; gap:8px; margin:13px 0;}
.m-team{display:flex; flex-direction:column; align-items:center; gap:7px;}
.m-flag{font-size:30px; line-height:1;}
.m-name{font:700 14px/1.15 'Rajdhani',sans-serif; text-align:center; color:var(--txt); letter-spacing:.3px;}
.m-score{font:800 30px/1 'Orbitron',sans-serif; color:var(--txt); min-width:84px; text-align:center;}
.m-score.live{color:var(--red);}
.m-score .sep{color:var(--muted); margin:0 5px;}
.m-score .vs{font:700 15px/1 'Rajdhani',sans-serif; color:var(--muted); letter-spacing:2px;}
.m-foot{display:flex; justify-content:space-between; align-items:center; gap:8px; border-top:1px solid var(--line); padding-top:10px; flex-wrap:wrap;}
.m-venue{font:500 11px/1.3 'Rajdhani',sans-serif; color:var(--muted); letter-spacing:.3px;}
.chip{font:700 10px/1 'Rajdhani',sans-serif; letter-spacing:.5px; padding:5px 9px; border-radius:999px; margin-left:5px; display:inline-block;}
.chip-globo{background:rgba(34,211,238,.16); color:var(--cyan);}
.chip-sportv{background:rgba(124,92,255,.20); color:#bca9ff;}
.chip-caze{background:rgba(34,224,122,.16); color:var(--green);}
/* Standings */
.group-grid{display:grid; grid-template-columns:repeat(auto-fill, minmax(345px,1fr)); gap:16px;}
.grp{background:linear-gradient(180deg,var(--panel2),var(--panel)); border:1px solid var(--line); border-radius:18px; overflow:hidden;}
.grp-head{font:700 15px/1 'Rajdhani',sans-serif; letter-spacing:2px; padding:12px 16px; color:#06101f;
  background:linear-gradient(90deg,var(--cyan),var(--green)); text-transform:uppercase;}
.tbl{width:100%; border-collapse:collapse; font:600 13px/1 'Rajdhani',sans-serif;}
.tbl th{color:var(--muted); font-weight:600; text-align:center; padding:9px 4px; font-size:11px; letter-spacing:.5px; border-bottom:1px solid var(--line);}
.tbl th.l, .tbl td.l{text-align:left; padding-left:12px;}
.tbl td{text-align:center; padding:10px 4px; border-bottom:1px solid rgba(255,255,255,.04); color:var(--txt);}
.tbl tr:last-child td{border-bottom:none;}
.tbl .pos{font-weight:800; width:30px;}
.tbl tr.q{background:linear-gradient(90deg, rgba(34,224,122,.09), transparent);}
.tbl tr.q td:first-child{box-shadow:inset 3px 0 var(--green);}
.tbl tr.q .pos{color:var(--green);}
.tbl tr.p td:first-child{box-shadow:inset 3px 0 var(--amber);}
.tbl tr.p .pos{color:var(--amber);}
.tbl .pts{font-weight:800; color:var(--cyan);}
.legend{color:var(--muted); font:500 12px/1.5 'Rajdhani',sans-serif; margin:4px 0 12px; letter-spacing:.3px;}
.legend b{color:var(--green);} .legend i{color:var(--amber); font-style:normal;}
/* Tabs */
.stTabs [data-baseweb="tab-list"]{gap:8px;}
.stTabs [data-baseweb="tab"]{background:var(--panel); border:1px solid var(--line); border-radius:11px; padding:6px 14px;}
.stTabs [aria-selected="true"]{background:linear-gradient(90deg, rgba(34,211,238,.22), rgba(34,224,122,.15)); border-color:rgba(34,211,238,.5);}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

CHIP_CLS = {"Globo": "chip-globo", "SporTV": "chip-sportv", "CazéTV": "chip-caze"}


def card_jogo_html(d, g, casa, fora, cidade, res, hoje, horarios, detalhe=None):
    dt = datetime.strptime(d, "%Y-%m-%d").date()
    estado = res[2] if res else None
    if estado == "in":
        stxt, scls = (f"🔴 {detalhe}" if detalhe else "🔴 AO VIVO"), "s-live"
    elif estado == "post":
        stxt, scls = "ENCERRADO", "s-post"
    elif dt == hoje:
        stxt, scls = "HOJE", "s-today"
    elif dt < hoje:
        stxt, scls = "AGUARDANDO", "s-pre"
    else:
        stxt, scls = "AGENDADO", "s-pre"

    live = "live" if estado == "in" else ""
    if res:
        gc, gf, _ = res
        score = f'<div class="m-score {live}">{gc}<span class="sep">:</span>{gf}</div>'
    else:
        score = '<div class="m-score"><span class="vs">VS</span></div>'

    moon = " 🌙" if eh_madrugada(casa, fora, horarios) else ""
    chips = "".join(f'<span class="chip {CHIP_CLS.get(c, "chip")}">{c}</span>'
                    for c in canais_do_jogo(casa, fora))
    sede = SEDE_PAIS.get(cidade, "")
    url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(
        f"{casa} x {fora} copa do mundo 2026 ao vivo")
    return (
        f'<a class="match-link" href="{url}" target="_blank" rel="noopener">'
        f'<div class="match {live}">'
        f'<div class="m-head"><span>🕒 {hora_jogo(casa, fora, horarios)}{moon}</span>'
        f'<span>GRUPO {g}</span><span class="m-status {scls}">{stxt}</span></div>'
        f'<div class="m-body">'
        f'<div class="m-team"><span class="m-flag">{flag(casa)}</span><span class="m-name">{casa}</span></div>'
        f'{score}'
        f'<div class="m-team"><span class="m-flag">{flag(fora)}</span><span class="m-name">{fora}</span></div>'
        f'</div>'
        f'<div class="m-foot"><span class="m-venue">📍 {cidade} · {sede}</span>'
        f'<span>{chips}</span></div></div></a>'
    )


def grupo_tabela_html(g, resultados):
    df = calcular_classificacao(g, resultados)
    rows = ""
    for pos, row in df.iterrows():
        cls = "q" if pos <= 2 else ("p" if pos == 3 else "")
        rows += (
            f'<tr class="{cls}"><td class="pos">{pos}</td>'
            f'<td class="l">{row["Seleção"]}</td>'
            f'<td class="pts">{row["P"]}</td><td>{row["J"]}</td>'
            f'<td>{row["V"]}</td><td>{row["E"]}</td><td>{row["D"]}</td>'
            f'<td>{row["SG"]:+d}</td></tr>'
        )
    return (
        f'<div class="grp"><div class="grp-head">Grupo {g}</div>'
        f'<table class="tbl"><thead><tr><th class="pos">#</th><th class="l">Seleção</th>'
        f'<th>P</th><th>J</th><th>V</th><th>E</th><th>D</th><th>SG</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>'
    )


# ----------------------------------------------------------------------------
# Cabeçalho
# ----------------------------------------------------------------------------
resultados, horarios, detalhes = obter_dados(usar_espn)
agora = datetime.now(BR_TZ)
hoje = agora.date()
n_encerrados = sum(1 for v in resultados.values() if v[2] == "post")
n_ao_vivo = sum(1 for v in resultados.values() if v[2] == "in")

st.markdown(
    '<div class="hero"><span class="hero-badge">FIFA WORLD CUP · COPA TECH</span>'
    '<h1>COPA DO MUNDO <span>2026</span></h1>'
    '<div class="hero-sub">🇺🇸 EUA · 🇨🇦 Canadá · 🇲🇽 México — Fase de grupos · '
    '🕒 horário de Brasília · 🌙 madrugada</div></div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="stats">'
    f'<div class="stat"><div class="v">{len(JOGOS)}</div><div class="l">Jogos</div></div>'
    f'<div class="stat"><div class="v">{n_encerrados}</div><div class="l">Encerrados</div></div>'
    f'<div class="stat live"><div class="v">{n_ao_vivo}</div><div class="l">Ao vivo</div></div>'
    f'<div class="stat"><div class="v">{agora:%H:%M}</div><div class="l">Atualizado</div></div>'
    f'</div>',
    unsafe_allow_html=True,
)

if usar_espn:
    st.caption("🟢 Placares ao vivo via feed público da ESPN (mesmos dados dos cards do Google) · "
               "atualização automática a cada 30s · 👆 toque num jogo para abrir os detalhes")

# Seção "AO VIVO AGORA" — destaque para jogos em andamento
jogos_ao_vivo = [(d, g, c, f, ci) for d, g, c, f, ci in JOGOS
                 if (r := resultados.get((c, f))) and r[2] == "in"]
if jogos_ao_vivo:
    st.markdown('<div class="livebar">Ao vivo agora</div>', unsafe_allow_html=True)
    cards_live = "".join(
        card_jogo_html(d, g, c, f, ci, resultados.get((c, f)), hoje, horarios, detalhes.get((c, f)))
        for d, g, c, f, ci in jogos_ao_vivo
    )
    st.markdown(f'<div class="day-grid">{cards_live}</div>', unsafe_allow_html=True)

tab_jogos, tab_grupos = st.tabs(["📅 Jogos por dia", "📊 Classificação dos grupos"])

# ----------------------------------------------------------------------------
# Aba 1 — Jogos por dia
# ----------------------------------------------------------------------------
with tab_jogos:
    c1, c2 = st.columns([2, 1])
    grupos_opt = ["Todos"] + [f"Grupo {g}" for g in GRUPOS]
    grupo_sel = c1.selectbox("Filtrar por grupo:", grupos_opt)
    so_brasil = c2.toggle("Apenas jogos do Brasil 🇧🇷", value=False)

    datas = sorted({d for d, *_ in JOGOS})
    for d in datas:
        jogos_dia = []
        for data, g, casa, fora, cidade in JOGOS:
            if data != d:
                continue
            if grupo_sel != "Todos" and f"Grupo {g}" != grupo_sel:
                continue
            if so_brasil and "Brasil" not in (casa, fora):
                continue
            jogos_dia.append((g, casa, fora, cidade))
        if not jogos_dia:
            continue

        jogos_dia.sort(key=lambda x: _chave_horario(x[1], x[2], horarios))
        eh_hoje = datetime.strptime(d, "%Y-%m-%d").date() == hoje
        badge = '<span class="today">🔴 HOJE</span>' if eh_hoje else ""
        st.markdown(
            f'<div class="dayhead"><span class="dot"></span>'
            f'<span class="d">{data_formatada(d)}</span>{badge}</div>',
            unsafe_allow_html=True,
        )
        cards = "".join(
            card_jogo_html(d, g, casa, fora, cidade, resultados.get((casa, fora)),
                           hoje, horarios, detalhes.get((casa, fora)))
            for g, casa, fora, cidade in jogos_dia
        )
        st.markdown(f'<div class="day-grid">{cards}</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Aba 2 — Classificação dos grupos
# ----------------------------------------------------------------------------
with tab_grupos:
    st.markdown(
        '<div class="legend">Classificam-se os <b>2 primeiros</b> de cada grupo + os '
        '<i>8 melhores 3º colocados</i>. &nbsp;Critérios: Pontos → Saldo (SG) → Gols pró.</div>',
        unsafe_allow_html=True,
    )
    tabelas = "".join(grupo_tabela_html(g, resultados) for g in GRUPOS)
    st.markdown(f'<div class="group-grid">{tabelas}</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Atualização automática
# ----------------------------------------------------------------------------
if auto:
    import time
    time.sleep(30)
    st.rerun()

