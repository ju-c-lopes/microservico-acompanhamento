variable "region" {
  description = "Região AWS para provisionar a EC2"
  type        = string
}

variable "key_name" {
  description = "Nome da chave SSH para acesso EC2"
  type        = string
}

variable "public_key_path" {
  description = "Caminho para o arquivo da chave pública SSH"
  type        = string
  sensitive = true
}

variable "my_ip" {
  description = "IP autorizado para acesso SSH (formato CIDR, ex: 1.2.3.4/32)"
  type        = string
}

variable "instance_type" {
  description = "Tipo da instância EC2"
  type        = string
  default     = "t2.micro"
}

variable "dockerhub_username" {
  description = "Nome de usuário do Docker Hub"
  type        = string
}

variable "dockerhub_token" {
  description = "Token de acesso do Docker Hub"
  type        = string
  sensitive   = true
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

variable "rds_host" {
  description = "Host do RDS"
  type        = string
}

variable "db_name" {
  description = "Nome do banco de dados"
  type        = string
}
