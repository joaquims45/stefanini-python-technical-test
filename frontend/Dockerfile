# Build: compila o Flutter Web dentro do próprio container, sem exigir o SDK
# instalado na máquina de quem roda o projeto.
FROM ghcr.io/cirruslabs/flutter:stable AS build

WORKDIR /app

COPY pubspec.yaml ./
RUN flutter pub get

COPY . .

# A tela roda no navegador de quem acessa, não dentro da rede do
# docker-compose — por isso o valor padrão aponta para a porta do backend
# publicada no host (localhost), não para o hostname interno "backend".
ARG API_BASE_URL=http://localhost:8000
RUN flutter build web --release --dart-define=API_BASE_URL=${API_BASE_URL}

# Runtime: nginx só serve os arquivos estáticos gerados no build acima.
FROM nginx:alpine

COPY --from=build /app/build/web /usr/share/nginx/html

EXPOSE 80
