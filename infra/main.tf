data "aws_vpc" "default" {
    default = true
}

data "aws_subnets" "default" {
    filter {
        name   = "vpc-id"
        values = [data.aws_vpc.default.id]
    }
}

resource "aws_db_subnet_group" "default" {
    name       = "rds-subnet-group"
    subnet_ids = data.aws_subnets.default.ids

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