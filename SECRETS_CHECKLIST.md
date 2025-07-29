# 🔐 Checklist de Secrets para GitHub Actions

## Secrets Obrigatórias no GitHub

Vá em: **Settings → Secrets and variables → Actions → New repository secret**

### AWS Credentials

-   [ ] `AWS_ACCESS_KEY_ID` - Chave de acesso AWS
-   [ ] `AWS_SECRET_ACCESS_KEY` - Chave secreta AWS

### Docker Hub

-   [ ] `DOCKERHUB_USERNAME` - Seu username no Docker Hub
-   [ ] `DOCKERHUB_TOKEN` - Token de acesso do Docker Hub

### SSH EC2

-   [ ] `EC2_USER` - Usuário SSH (use: `ubuntu`)
-   [ ] `EC2_SSH_KEY` - Chave SSH privada (conteúdo do arquivo .pem)

### Configuração de Rede

-   [ ] `MY_IP` - Seu IP público (sem /32, ex: `187.180.172.78`)

## ✅ Você NÃO precisa do arquivo terraform.tfvars

O workflow agora usa **apenas Secrets do GitHub**. O arquivo `terraform.tfvars.example` serve apenas como referência.

## ⚠️ Importante: Configurar Terraform Variables

Você também precisará de um arquivo `terraform.tfvars` na pasta `infra-ec2/`:

```hcl
region           = "us-east-1"
key_name         = "acompanhamento-key"
public_key_path  = "~/.ssh/id_rsa.pub"
my_ip           = "SEU_IP/32"  # Use: curl ifconfig.me
dockerhub_username = "SEU_USERNAME"
dockerhub_token    = "SEU_TOKEN"
db_user           = "admin"
db_password       = "senha123"
rds_host          = "localhost"  # Para SQLite local
db_name           = "acompanhamento"
```

## 🧪 Comandos para Teste Local (antes do GitHub)

```bash
# 1. Validar Terraform
cd infra-ec2
terraform init
terraform plan

# 2. Validar Docker Build
docker build -t acompanhamento:test .
docker run --rm -p 8000:8000 acompanhamento:test

# 3. Rodar testes da aplicação
python run_tests.py all
```
