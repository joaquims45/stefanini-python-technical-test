# Uso de IA

## 1. Quais ferramentas usei

Claude Code (Sonnet), em modo de pair-programming interativo, com acesso a
shell, Docker e ao daemon Docker local.

## 2. Onde usei, onde não usei

**Usei para:** todo o código — modelos, clientes das APIs externas,
serviço de sincronização, endpoints DRF, management commands do django-q2,
`Dockerfile`s, `docker-compose.yml` e a tela Flutter. Também usei para
gerar o scaffold do Django (`django-admin startapp`) e do Flutter
(`flutter create`) via comandos reais das próprias ferramentas, em vez de
escrever esses arquivos de boilerplate à mão.

**Não usei para:** as decisões de modelagem e arquitetura em si (o que
vira campo de `Item`, como representar "está respondendo agora", por que
`migrate` virou um serviço separado no compose) — essas decisões foram
minhas, e a IA implementou o que foi decidido. Também não usei para gerar
dado de teste ou fixture "bonito demais"; os testes usam cenários mínimos
que exercitam exatamente os três cenários obrigatórios (timeout, 500,
formato inesperado).

## 3. Como verifiquei o que foi gerado

- Rodei a suíte de testes (`pytest`) depois de cada trecho de backend
  gerado, não só ao final — 23 testes passando, cobrindo os três cenários
  obrigatórios por fonte.
- Rodei o `docker compose up --build` de ponta a ponta pelo menos duas
  vezes: a primeira revelou uma condição de corrida real entre `backend` e
  `qcluster` rodando `migrate` ao mesmo tempo (erro de constraint
  duplicada no Postgres). Diagnostiquei a causa pelo log do container,
  corrigi extraindo um serviço `migrate` dedicado, e confirmei rodando de
  novo do zero.
- Verifiquei `/items` e `/health` com `curl` contra dados reais das duas
  APIs públicas (não só contra mocks), conferindo contagem de registros e
  o formato da resposta.
- Rodei `flutter analyze`, `flutter test` e `flutter build web` dentro do
  container oficial antes de escrever o `Dockerfile` do frontend, e depois
  validei a imagem final subindo o container e conferindo HTTP 200 na
  página servida.
- Li o código gerado antes de aceitar cada etapa — em particular, revisei
  a lógica de `sync_source`/`sync_all_sources` para confirmar que uma
  falha numa fonte não apaga itens já persistidos da mesma fonte, que é o
  requisito central de robustez do enunciado.
