# Provedor AWS
provider "aws" {
  region  = var.region
}

# AMI Ubuntu mais recente

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# Chave SSH
resource "aws_key_pair" "default" {
  key_name   = var.key_name
  public_key = file(var.public_key_path)
}

# VPC e Subnets padrão

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security Group para EC2
resource "aws_security_group" "ec2_sg" {
  name   = "ec2-sg"
  vpc_id = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Instância EC2
resource "aws_instance" "acompanhamento" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = data.aws_subnets.default.ids[0]
  key_name               = aws_key_pair.default.key_name
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]

  user_data = templatefile("${path.module}/setup.sh.tpl", {
    DOCKERHUB_USERNAME = var.dockerhub_username,
    DOCKERHUB_TOKEN    = var.dockerhub_token,
    DB_USER           = var.db_user,
    DB_PASSWORD       = var.db_password,
    RDS_HOST          = var.rds_host,
    DB_NAME           = var.db_name
  })

  tags = {
    Name = "acompanhamento-ec2"
  }
}

output "ec2_public_ip" {
  value = aws_instance.acompanhamento.public_ip
}

output "security_group_id" {
  value = aws_security_group.ec2_sg.id
}
