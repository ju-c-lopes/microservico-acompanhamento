#!/bin/bash
set -e

# Instala Docker via script oficial
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# (Opcional) Instala Docker Compose
# sudo apt-get install -y docker-compose

# Adiciona o usuário ubuntu ao grupo docker
sudo usermod -aG docker ubuntu

# Faz login no Docker Hub (substitua USER e TOKEN pelas secrets ou use ENV)
echo "${DOCKERHUB_TOKEN}" | sudo docker login -u "${DOCKERHUB_USERNAME}" --password-stdin

# Puxa e roda o container (ajuste as variáveis conforme necessário)
sudo docker pull ${DOCKERHUB_USERNAME}/acompanhamento:latest
sudo docker stop acompanhamento || true
sudo docker rm acompanhamento || true
sudo docker run -d --name acompanhamento \
  -e DATABASE_URL="mysql+aiomysql://${DB_USER}:${DB_PASSWORD}@${RDS_HOST}:3306/${DB_NAME}" \
  -p 8000:8000 \
  ${DOCKERHUB_USERNAME}/acompanhamento:latest