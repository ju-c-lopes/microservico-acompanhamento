# 🔑 Como Gerar e Configurar Chave SSH

## 1. Gerar Chave SSH Local

```bash
# Gere uma nova chave SSH
ssh-keygen -t rsa -b 4096 -f ~/.ssh/acompanhamento-key -N ""

# Isso criará:
# ~/.ssh/acompanhamento-key (chave PRIVADA)
# ~/.ssh/acompanhamento-key.pub (chave PÚBLICA)
```

## 2. Configurar no Terraform

No arquivo `infra-ec2/terraform.tfvars` (que você precisa criar):

```hcl
region           = "us-east-1"
key_name         = "acompanhamento-key"
public_key_path  = "~/.ssh/acompanhamento-key.pub"
my_ip           = "SEU_IP/32"  # Use: curl ifconfig.me
dockerhub_username = "SEU_USERNAME"
dockerhub_token    = "SEU_TOKEN"
db_user           = "admin"
db_password       = "senha123"
rds_host          = "localhost"
db_name           = "acompanhamento"
```

## 3. Configurar Secret no GitHub

-   **EC2_SSH_KEY**: Cole o conteúdo de `~/.ssh/acompanhamento-key` (chave PRIVADA)

## 4. Obter seu IP público

```bash
curl ifconfig.me
# Use o resultado + /32 no campo my_ip
```
