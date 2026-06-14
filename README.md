# testecarto

Aplicativo **multipágina** em Streamlit. A página principal é o `testecartao.py`
e as demais ficam na pasta `pages/`, aparecendo automaticamente no menu lateral.

Para rodar tudo (mesma URL, com navegação entre as páginas):

```bash
pip install -r requirements.txt
streamlit run testecartao.py
```

## Páginas

### 📊 Cartão / Atingimento (`testecartao.py`) — página inicial
Consulta de atingimento por agência/carteira e informações de cliente (MCI).

### 🏆 Copa do Mundo 2026 (`pages/1_🏆_Copa_do_Mundo_2026.py`)
Página com atualização online dos jogos da Copa do Mundo FIFA 2026 (EUA/Canadá/México):

- **Jogos separados por dia**, com horário de Brasília e o(s) **canal(is)** que transmitem cada partida
- **Resultados** dos jogos (inclusive jogos **ao vivo**)
- **Classificação** automática dos 12 grupos (Pontos → Saldo de gols → Gols pró)
- **Placares ao vivo** via feed público da ESPN (os mesmos dados dos cards do Google), com atualização automática a cada 30s

> Os placares são buscados automaticamente no feed da ESPN. Caso a rede falhe,
> a página usa os resultados cadastrados no dicionário `RESULTADOS`, no topo do
> arquivo, que também podem ser editados manualmente.

> **Deploy:** como é multipágina, o app já publicado (com `testecartao.py` como
> arquivo principal) ganha a página da Copa automaticamente — não é preciso criar
> um novo deploy.
