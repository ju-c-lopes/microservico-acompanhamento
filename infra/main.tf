data "aws_vpc" "default" {
    default = true
}

resource "aws_vpc" "main" {
    cidr_block           = "10.0.0.0/16"
    enable_dns_support   = true
    enable_dns_hostnames = true

    tags = {
        Name = "techchallenge-vpc"
    }
}

resource "aws_subnet" "private_a" {
    vpc_id            = aws_vpc.main.id
    cidr_block        = "10.0.1.0/24"
    availability_zone = "us-east-1a"

    tags = {
        Name = "techchallenge-private-a"
    }
}

resource "aws_subnet" "private_b" {
    vpc_id            = aws_vpc.main.id
    cidr_block        = "10.0.2.0/24"
    availability_zone = "us-east-1b"

    tags = {
        Name = "techchallenge-private-b"
    }
}

resource "aws_db_subnet_group" "default" {
    name       = "rds-subnet-group"
    subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]

    tags = {
        Name = "TechChallengeSUB"
    }
}

resource "aws_security_group" "rds_sg" {
    name   = "rds_sg"
    description = "SG para o RDS MySQL"
    vpc_id = data.aws_vpc.default.id

    ingress {
        from_port   = 3306
        to_port     = 3306
        protocol    = "tcp"
        cidr_blocks = var.allowed_ips
    }

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = {
        Name = "techchallenge_rds"
    }
}

resource "aws_db_instance" "mysql" {
    identifier             = "rds-techchallenge"
    instance_class         = "db.t3.micro"
    allocated_storage      = 5
    engine                 = "mysql"
    engine_version         = "8.0"
    db_name                = var.db_name
    username               = var.db_user
    password               = var.db_password
    parameter_group_name   = "default.mysql8.0"
    skip_final_snapshot    = true
    publicly_accessible    = true
    db_subnet_group_name   = aws_db_subnet_group.default.name
    vpc_security_group_ids = [aws_security_group.rds_sg.id]
}