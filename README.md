# testecarto

Aplicações em Streamlit (cada arquivo é um app independente).

## Apps

### 🏆 Copa do Mundo 2026 (`copa_mundo_2026.py`)
App publicado em **https://copa2026jogos.streamlit.app/**

Página com atualização online dos jogos da Copa do Mundo FIFA 2026 (EUA/Canadá/México):

- **Jogos separados por dia**, com horário de Brasília e o(s) **canal(is)** que transmitem cada partida
- **Resultados** dos jogos (inclusive jogos **ao vivo**)
- **Classificação** automática dos 12 grupos (Pontos → Saldo de gols → Gols pró)
- **Placares ao vivo** via feed público da ESPN (os mesmos dados dos cards do Google), com atualização automática a cada 30s

Para rodar localmente:

```bash
pip install -r requirements.txt
streamlit run copa_mundo_2026.py
```

> Os placares são buscados automaticamente no feed da ESPN. Caso a rede falhe,
> a página usa os resultados cadastrados no dicionário `RESULTADOS`, no topo do
> arquivo, que também podem ser editados manualmente.

### 📊 Cartão / Atingimento (`testecartao.py`)
Consulta de atingimento por agência/carteira e informações de cliente (MCI).

```bash
streamlit run testecartao.py
```
