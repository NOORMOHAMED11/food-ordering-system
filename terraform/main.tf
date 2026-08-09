terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "ap-south-1" # Mumbai — closest region for India-based deployment
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = { Name = "tastygo-vpc" }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "tastygo-igw" }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block               = "10.0.1.0/24"
  map_public_ip_on_launch = true
  tags = { Name = "tastygo-public-subnet" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  tags = { Name = "tastygo-public-rt" }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "app" {
  name        = "tastygo-app-sg"
  description = "Allow HTTP and SSH"
  vpc_id      = aws_vpc.main.id

  ingress { from_port = 80,  to_port = 80,  protocol = "tcp", cidr_blocks = ["0.0.0.0/0"] }
  ingress { from_port = 22,  to_port = 22,  protocol = "tcp", cidr_blocks = ["0.0.0.0/0"] } # tighten this to your IP
  egress  { from_port = 0,   to_port = 0,   protocol = "-1",  cidr_blocks = ["0.0.0.0/0"] }

  tags = { Name = "tastygo-app-sg" }
}

resource "aws_instance" "app_server" {
  ami                    = "ami-0f5ee92e2d63afc18" # Amazon Linux 2023, ap-south-1 — verify before use
  instance_type           = "t3.micro"
  subnet_id                = aws_subnet.public.id
  vpc_security_group_ids  = [aws_security_group.app.id]
  key_name                = "YOUR_KEY_PAIR_NAME" # create with: aws ec2 create-key-pair --key-name tastygo-key

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y docker
              systemctl start docker
              systemctl enable docker
              EOF

  tags = { Name = "tastygo-app-server" }
}

output "app_server_public_ip" {
  value = aws_instance.app_server.public_ip
}
