resource "aws_vpc" "vpc" {
    cidr_block = "10.0.0.0/16"
    enable_dns_hostnames = true
    enable_dns_support   = true
}

resource "aws_subnet" "private_subnet" {
    vpc_id = aws_vpc.vpc.id
    count = 1
    cidr_block = "10.0.1.0/24"
    availability_zone = "${var.aws_region}a"
    map_public_ip_on_launch = false
}

resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.vpc.id
}

resource "aws_vpc_endpoint" "endpoint_s3" {
    vpc_id            = aws_vpc.vpc.id
    vpc_endpoint_type = "Gateway"
    service_name      = "com.amazonaws.${var.aws_region}.s3"
    route_table_ids   = [aws_route_table.private_rt.id]
    policy = jsonencode(
        {
            "Version": "2012-10-17",
            "Statement": [
              {
                "Sid": "Allow-access-to-specific-bucket",
                "Effect": "Allow",
                "Principal": "*",
                "Action": [
                   "s3:ListBucket",
                   "s3:GetObject",
                   "s3:PutObject"
                ],
                "Resource": [
                  "arn:aws:s3:::tfm-educ-app-gold",
                  "arn:aws:s3:::tfm-educ-app-gold/*"
                ]
                "Condition": {
                    "ArnEquals": {
                      "aws:PrincipalArn": "arn:aws:iam::${var.account_number}:role/core_app_lambda "
                    }
                }
              }
            ]
        }   
    ) 
}

resource "aws_vpc_endpoint" "endpoint_dynamodb" {
    vpc_id            = aws_vpc.vpc.id
    vpc_endpoint_type = "Gateway"
    service_name      = "com.amazonaws.${var.aws_region}.dynamodb"
    route_table_ids   = [aws_route_table.private_rt.id]
}

resource "aws_security_group" "sg_lambda_core" {
    name        = "${var.project_name}-sg-lambda-core"
    description = "Security group for Lambda core functions"
    vpc_id      = aws_vpc.vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "allow_tls_ipv4" {
  security_group_id = aws_security_group.sg_lambda_core.id
  cidr_ipv4         = aws_vpc.vpc.cidr_block
  ip_protocol       = "-1"
}

resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv4" {
    security_group_id = aws_security_group.sg_lambda_core.id
    cidr_ipv4 = "0.0.0.0/0"
    ip_protocol = "TCP"
    from_port = 443
    to_port = 443
}