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

# Seleções com maior apelo (recebem transmissão na TV fechada além da CazéTV)
GRANDES = {
    "Brasil", "Argentina", "França", "Espanha", "Inglaterra", "Portugal",
    "Alemanha", "Holanda", "Bélgica", "Uruguai", "México", "EUA", "Croácia",
}


def canais_do_jogo(casa: str, fora: str):
    """Retorna a lista de canais/plataformas que transmitem o jogo.

    A CazéTV (YouTube, gratuito) exibe todos os 104 jogos. Globo (TV aberta) e
    SporTV (TV fechada) priorizam jogos do Brasil e das principais seleções.
    """
    canais = []
    if casa == "Brasil" or fora == "Brasil":
        canais = ["Globo", "SporTV", "CazéTV"]
    elif casa in GRANDES or fora in GRANDES:
        canais = ["SporTV", "CazéTV"]
    else:
        canais = ["CazéTV"]
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


@st.cache_data(ttl=30, show_spinner="Buscando placares ao vivo...")
def buscar_resultados_espn(_minuto):
    """Busca placares (inclusive jogos AO VIVO) no feed público da ESPN.

    Retorna {(casa, fora): (gols_casa, gols_fora, estado)}, estado em {'in', 'post'}.
    O parâmetro `_minuto` serve só para renovar o cache. Falhas de rede são
    ignoradas silenciosamente (a página então usa os resultados de RESULTADOS).
    """
    achados = {}
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
                if estado not in ("in", "post"):
                    continue
                cs = ev["competitions"][0]["competitors"]
                h = next(c for c in cs if c["homeAway"] == "home")
                a = next(c for c in cs if c["homeAway"] == "away")
                casa = EN_PARA_PT.get(_strip(h["team"]["displayName"]))
                fora = EN_PARA_PT.get(_strip(a["team"]["displayName"]))
                gc, gf = h.get("score"), a.get("score")
                if not (casa and fora) or gc in (None, "") or gf in (None, ""):
                    continue
                if (casa, fora) in CONFRONTOS:
                    achados[(casa, fora)] = (int(gc), int(gf), estado)
                elif (fora, casa) in CONFRONTOS:  # orientação invertida
                    achados[(fora, casa)] = (int(gf), int(gc), estado)
            except Exception:
                continue
    return achados


def obter_resultados(usar_espn: bool):
    """Combina resultados manuais (RESULTADOS) com os do feed ESPN (prioridade).

    Valor de cada confronto: (gols_casa, gols_fora, estado), estado em
    {'post' (encerrado), 'in' (ao vivo)}.
    """
    resultados = {k: (gc, gf, "post") for k, (gc, gf) in RESULTADOS.items()}
    if usar_espn:
        resultados.update(buscar_resultados_espn(datetime.now().strftime("%Y%m%d%H%M")))
    return resultados


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


def hora_jogo(casa: str, fora: str) -> str:
    """Horário de Brasília do jogo (string 'HHhMM')."""
    return HORARIOS.get((casa, fora), "--h--")


def _chave_horario(casa: str, fora: str) -> int:
    """Chave para ordenar jogos do dia em ordem cronológica (madrugada por último)."""
    h = hora_jogo(casa, fora)
    try:
        hh, mm = int(h[:2]), int(h[3:5])
    except ValueError:
        return 9999
    # Jogos de madrugada (00h-05h) acontecem depois dos da noite do mesmo dia
    return hh * 60 + mm + (24 * 60 if hh < 6 else 0)


def eh_madrugada(casa: str, fora: str) -> bool:
    h = hora_jogo(casa, fora)
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
# Cabeçalho
# ----------------------------------------------------------------------------
st.title("🏆 Copa do Mundo FIFA 2026")
st.caption("Estados Unidos 🇺🇸 · Canadá 🇨🇦 · México 🇲🇽  —  Fase de grupos (11 a 27 de junho)  "
           "·  🕒 Horários de Brasília (BRT) · 🌙 = madrugada")

resultados = obter_resultados(usar_espn)
agora = datetime.now(BR_TZ)
hoje = agora.date()

n_encerrados = sum(1 for v in resultados.values() if v[2] == "post")
n_ao_vivo = sum(1 for v in resultados.values() if v[2] == "in")

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("Jogos", len(JOGOS))
col_b.metric("Encerrados", n_encerrados)
col_c.metric("🔴 Ao vivo", n_ao_vivo)
col_d.metric("Atualizado às", agora.strftime("%H:%M:%S"))

if usar_espn:
    st.info("🟢 Fonte: feed público de placares da ESPN (mesmos dados dos cards do Google). "
            "A página atualiza sozinha a cada 30s.")

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

        jogos_dia.sort(key=lambda x: _chave_horario(x[1], x[2]))
        marcador = " 🔴 HOJE" if datetime.strptime(d, "%Y-%m-%d").date() == hoje else ""
        st.subheader(f"📆 {data_formatada(d)}{marcador}")

        for g, casa, fora, cidade in jogos_dia:
            res = resultados.get((casa, fora))
            estado = res[2] if res else None
            status = status_jogo(d, estado, hoje)

            if res:
                gc, gf, _ = res
                cor = "#e10600" if estado == "in" else "#0b8043"
                placar = (f"<div style='text-align:center;font-size:2rem;font-weight:800;"
                          f"line-height:1;color:{cor}'>{gc}<span style='color:#999'> x </span>{gf}</div>")
            else:
                placar = ("<div style='text-align:center;font-size:1.5rem;font-weight:700;"
                          "color:#bbb;line-height:1'>x</div>")

            canais = " · ".join(f"`{c}`" for c in canais_do_jogo(casa, fora))
            sede = SEDE_PAIS.get(cidade, "")
            hora = hora_jogo(casa, fora)
            hora_txt = f"🕒 **{hora}**" + (" 🌙" if eh_madrugada(casa, fora) else "")

            c_hora, l1, l2, l3, l4 = st.columns([1.3, 3, 1.4, 3, 2.4])
            c_hora.markdown(f"<div style='padding-top:8px'>{hora_txt}</div>",
                            unsafe_allow_html=True)
            l1.markdown(f"<div style='text-align:right;font-size:1.1rem;padding-top:8px'>"
                        f"{flag(casa)} <b>{casa}</b></div>", unsafe_allow_html=True)
            l2.markdown(placar, unsafe_allow_html=True)
            l3.markdown(f"<div style='font-size:1.1rem;padding-top:8px'>"
                        f"{flag(fora)} <b>{fora}</b></div>", unsafe_allow_html=True)
            l4.markdown(f"<div style='padding-top:8px'><code>Grupo {g}</code><br>{status}</div>",
                        unsafe_allow_html=True)
            st.caption(f"📍 {cidade} ({sede}) &nbsp;|&nbsp; 📺 {canais}")
            st.divider()

# ----------------------------------------------------------------------------
# Aba 2 — Classificação dos grupos
# ----------------------------------------------------------------------------
with tab_grupos:
    st.caption("Os dois primeiros de cada grupo avançam, além dos 8 melhores terceiros colocados. "
               "Critérios: Pontos → Saldo de gols → Gols pró.")
    grupos_lista = list(GRUPOS.keys())
    for i in range(0, len(grupos_lista), 2):
        cols = st.columns(2)
        for col, g in zip(cols, grupos_lista[i:i + 2]):
            with col:
                st.markdown(f"### Grupo {g}")
                df = calcular_classificacao(g, resultados)
                st.dataframe(df, use_container_width=True)

# ----------------------------------------------------------------------------
# Atualização automática
# ----------------------------------------------------------------------------
if auto:
    import time
    time.sleep(30)
    st.rerun()

