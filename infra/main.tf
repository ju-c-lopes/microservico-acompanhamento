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

resource "aws_internet_gateway" "gw" {
    vpc_id = aws_vpc.main.id

    tags = {
        Name = "techchallenge-igw"
    }
}

resource "aws_subnet" "public" {
    vpc_id                  = aws_vpc.main.id
    cidr_block              = "10.0.1.0/24"
    availability_zone       = "us-east-1a"
    map_public_ip_on_launch = true

    tags = {
        Name = "techchallenge-public-subnet"
    }
}

resource "aws_route_table" "public" {
    vpc_id = aws_vpc.main.id

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.gw.id
    }

    tags = {
        Name = "techchallenge-public-rt"
    }
}

resource "aws_route_table_association" "public_assoc" {
    subnet_id      = aws_subnet.public.id
    route_table_id = aws_route_table.public.id
}

resource "aws_db_subnet_group" "rds" {
    name       = "rds-subnet-group"
    subnet_ids = [aws_subnet.public.id]

    tags = {
        Name = "techchallenge-rds-subnet-group"
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
    db_subnet_group_name   = aws_db_subnet_group.rds.name
    vpc_security_group_ids = [aws_security_group.rds_sg.id]
}
