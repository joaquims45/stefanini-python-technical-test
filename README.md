# Painel de Integrações

Painel de saúde de integrações: consome duas APIs públicas sem autenticação,
normaliza os dados num modelo próprio, persiste o histórico de sincronizações
e expõe endpoints que respondem a quatro perguntas por integração:

- Está respondendo agora?
- Quando foi a última sincronização bem-sucedida?
- Quantos registros vieram?
- O que falhou, e quando?

Stack: **Django + Django REST Framework** (backend), **PostgreSQL**
(persistência), **django-q2** (agendamento/sincronização periódica) e
**Flutter Web** (única tela, somente leitura).

## Como rodar

### Com Docker (recomendado)

Pré-requisito: Docker e Docker Compose.

```bash
docker compose up --build
```

Isso sobe, nessa ordem:

1. `db` — Postgres 16, com healthcheck.
2. `migrate` — aplica as migrations uma única vez e encerra (ver "Decisões
   técnicas" abaixo sobre por que ele existe como serviço separado).
3. `backend` — na primeira subida, cria o agendamento do django-q2, roda uma
   sincronização inicial (para `/items` e `/health` já nascerem com dado) e
   sobe o servidor Django em `http://localhost:8000`.
4. `qcluster` — worker do django-q2 que executa a sincronização periódica
   (a cada 5 minutos, por padrão) em segundo plano.
5. `frontend` — build do Flutter Web servido por nginx em
   `http://localhost:8080`.

Endpoints para conferir:

```bash
curl http://localhost:8000/items
curl http://localhost:8000/items?source=open_brewery_db
curl http://localhost:8000/health
```

Para derrubar tudo (mantendo o volume do Postgres): `docker compose down`.
Para derrubar e apagar os dados também: `docker compose down -v`.

### Sem Docker (backend)

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt

# Banco: aponte as variáveis de ambiente POSTGRES_* para um Postgres local,
# ou suba só o serviço de banco do compose: docker compose up db
python manage.py migrate
python manage.py schedule_sync
python manage.py sync_sources     # sincronização manual, opcional
python manage.py runserver
```

Para o agendamento periódico funcionar sem Docker, é preciso rodar também
`python manage.py qcluster` em outro terminal.

### Testes (sem Docker, sem internet, sem banco externo)

```bash
cd backend
pytest
```

Roda contra SQLite em memória (ver `config/settings/test.py`), sem precisar
do Postgres de pé nem de acesso à internet — as chamadas HTTP externas são
mockadas. Não há necessidade de container para isso: containerizar os testes
não muda o resultado e adiciona complexidade que o enunciado pede para
evitar.

### Frontend sem Docker

Requer o SDK do Flutter instalado.

```bash
cd frontend
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

## Estrutura do repositório

```
backend/            Django + DRF + django-q2
  config/           settings (base/dev/test), urls, wsgi
  integrations/     models, clients das fontes externas, serviço de sync,
                     endpoints, management commands, testes
  Dockerfile
  entrypoint.sh
frontend/           Flutter Web (única tela)
  lib/
  Dockerfile
docker-compose.yml
README.md
USO-DE-IA.md
```

## Decisões técnicas

O enunciado deixa várias decisões em aberto de propósito. Esta seção
registra o que foi escolhido, e a alternativa descartada em cada ponto.

**Par de APIs.** BrasilAPI (feriados nacionais) + Open Brewery DB — o par
sugerido no enunciado. Formatos bem diferentes entre si (lista simples de
datas vs. lista de objetos com vários campos), que é justamente o ponto do
exercício. Não precisou trocar por indisponibilidade de nenhuma das duas.

**Banco de dados: PostgreSQL.** Rodando localmente via `docker-compose`
(serviço `db`). Alternativa descartada: SQLite para tudo — seria mais simples
de configurar, mas o Postgres já é o banco pedido para o projeto e o
`docker-compose` absorve todo o custo de setup dentro do orçamento de tempo.

**Testes em SQLite, não em Postgres.** `config/settings/test.py` troca o
banco para SQLite em memória só para os testes (`pytest.ini` fixa
`DJANGO_SETTINGS_MODULE=config.settings.test`). Alternativa descartada: usar
o próprio Postgres do compose nos testes — violaria a exigência de rodar
"sem depender de um banco de dados externo em execução".

**"Está respondendo agora?" reflete a última sincronização, não um ping ao
vivo.** `GET /health` responde com base no resultado do último `SyncRun` de
cada fonte, não fazendo uma chamada HTTP síncrona à API externa a cada
requisição. Alternativa descartada: checar a fonte ao vivo em toda chamada
de `/health` — isso reintroduziria, no próprio endpoint de saúde, a mesma
fragilidade (timeout, fonte fora do ar) que o painel existe para não
propagar ao usuário. Sync fica por conta do agendamento do django-q2.

**Falha de uma fonte não apaga dado bom.** Quando `sync_source` falha, ele
grava um `SyncRun` malsucedido com o erro, mas não mexe nos `Item`s já
persistidos daquela fonte. Dado antigo rotulado como antigo (via
`last_successful_sync` e `last_error`) é mais útil para quem olha o painel
do que simplesmente esvaziar `/items`.

**Agendamento com django-q2, broker ORM (não Redis).** `Q_CLUSTER` usa
`django_q.brokers.orm`, reaproveitando o próprio Postgres como fila.
Alternativa descartada: broker Redis — exigiria mais um serviço no
`docker-compose` só para rodar um cron simples de sincronização a cada 5
minutos; não se justificava para o volume do exercício.

**Serviço `migrate` separado no compose.** Na primeira versão, `backend` e
`qcluster` rodavam `migrate` cada um no seu próprio entrypoint. Isso causou
uma condição de corrida real (os dois tentando criar as mesmas tabelas ao
mesmo tempo num banco recém-criado, com erro de constraint duplicada — visto
e corrigido durante o desenvolvimento). A correção foi extrair `migrate`
como um serviço próprio que roda uma vez e encerra; `backend` e `qcluster`
esperam ele terminar (`condition: service_completed_successfully`) antes de
subir. O `entrypoint.sh` de cada um ainda roda `migrate` de novo por
segurança — é idempotente e não tem custo relevante.

**CORS liberado (`CORS_ALLOW_ALL_ORIGINS = True`).** Não há autenticação de
usuário no escopo do teste, então não existe uma superfície sensível para
restringir por origem. Alternativa descartada: lista de origens fixa
(`localhost:8080`) — funcionaria, mas é uma restrição sem efeito de
segurança real aqui, e complica testar a tela apontando para outra porta.

**`runserver` em vez de Gunicorn.** Simplicidade para o escopo do teste
(deploy em produção está explicitamente fora de escopo). Documentado como
corte deliberado, não esquecimento.

**Flutter Web, não mobile/desktop nativo.** Mais simples de rodar e de
comprovar (print de tela ou acesso direto ao navegador) sem emulador. A
tela foi construída via Docker (`ghcr.io/cirruslabs/flutter:stable` no
multi-stage build do `frontend/Dockerfile`), sem precisar instalar o SDK do
Flutter na máquina — reduz o risco coberto pela regra de parada do
enunciado. Neste projeto o setup subiu dentro do tempo esperado, então a
tela Flutter está completa; não foi necessário aplicar a regra de parada.

**`API_BASE_URL` do frontend aponta para `localhost`, não para o hostname
`backend`.** A tela roda no navegador de quem acessa a máquina host, fora da
rede interna do `docker-compose` — por isso o `ARG API_BASE_URL` do
`frontend/Dockerfile` usa `http://localhost:8000` (a porta publicada), e não
`http://backend:8000` (que só resolve dentro da rede do compose).

**Print de tela não incluído.** O enunciado só pede print "se a tela não
rodar facilmente na máquina de quem avalia". Como `docker compose up --build`
sobe a tela funcionando em `http://localhost:8080` de ponta a ponta (testado
durante o desenvolvimento), não foi anexado print — abrir a URL localmente
substitui a comprovação.

## O que foi deixado de fora (fora de escopo, por decisão)

Seguindo a lista de "fora de escopo" do enunciado: sem autenticação, sem
interface web além da tela Flutter, sem deploy em nuvem, sem meta de
cobertura de testes, sem filas/mensageria. Dos itens de "se sobrar tempo",
foi feito o `docker-compose` completo (pedido explicitamente pelo
solicitante do teste); paginação em `/items`, CI e log estruturado não
foram implementados por não terem sobrado como prioridade dentro do
orçamento de tempo.
