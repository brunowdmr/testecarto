# testecarto

Aplicativos Streamlit.

## Apps

- `testecartao.py` — dashboard de atingimento por carteira e consulta de cliente (MCI).
- `agro_news.py` — painel do agro com duas abas: **Notícias (RSS)**, com foco em
  agro financeiro, político e do Centro-Oeste (filtro por termo, por categoria,
  palavras-chave de alerta e notificação em tempo real via auto-refresh); e
  **YouTube**, com os vídeos recentes de canais de agro.

## Como rodar

```bash
pip install -r requirements.txt
streamlit run agro_news.py
```

### Notícias do Agro

- **Fontes:** feeds RSS públicos nacionais (AgFeed, Canal Rural, Compre Rural,
  BeefPoint, CNN Brasil, InfoMoney, Money Times), regionais do Centro-Oeste (Só
  Notícias/MT, Campo Grande News/MS) e legislativas (Agência Câmara, Agência
  Senado). As fontes
  gerais, regionais e legislativas não são só de agro, mas o filtro "apenas
  conteúdo do agro" mantém somente as matérias do setor — ou seja, é **agro do
  Centro-Oeste / agro político**, não notícia geral. É possível adicionar outro
  feed pela URL na barra lateral.
- **Apenas conteúdo do agro:** descarta o que não é do agronegócio (ligado por
  padrão); funciona como o portão de todas as fontes.
- **Categorias:** cada matéria é marcada como 💰 Financeiro, 🏛️ Político e/ou
  📍 Centro-Oeste, e dá para filtrar por elas (sempre dentro do agro).
- **Busca:** filtra as notícias por um termo.
- **Alertas:** ao surgir uma notícia nova que contenha alguma das palavras-chave
  configuradas, o app exibe um toast e marca o item com 🔔 / 🆕.
- **Tempo real:** com a atualização automática ligada, o app recarrega os feeds
  no intervalo escolhido e destaca as novidades.

### Aba YouTube

- **Canais:** feeds Atom oficiais do YouTube por `channel_id` (Canal Rural,
  Notícias Agrícolas, Scot Consultoria, Mais Soja, BeefPoint, Agro Resenha).
- **Período:** filtra os vídeos por últimas 24h / 3 / 7 / 30 dias.
- **Busca:** filtra os vídeos por termo no título.
- Os vídeos tocam direto na página (player do YouTube embutido).
