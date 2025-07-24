variable "region" {
    default     = "us-east-1"
    description = "Região AWS onde o RDS será criado"
}

variable "aws_role_to_assume" {
    description = "ARN da Role IAM com acesso à AWS via OIDC"
    type        = string
    sensitive   = true
}

variable "db_name" {
    description = "Nome do banco de dados"
    type        = string
}

variable "db_user" {
    description = "Usuário do banco de dados"
    type        = string
}

variable "db_password" {
    description = "Senha do banco de dados"
    type        = string
    sensitive   = true
}

variable "allowed_ips" {
    description = "IP público da máquina que irá acessar o banco de dados"
    type        = list(string)
    default     = []
    sensitive = true
}