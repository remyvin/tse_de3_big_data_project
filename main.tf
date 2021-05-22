# Configure the AWS Provider
provider "aws" {
  region     = var.provider_region
  access_key = var.access_key
  secret_key = var.secret_key
  token      = var.token
}

resource "aws_instance" "web" {
  ami             = "ami-0d5eff06f840b45e9"
  instance_type   = "t2.micro"
  key_name        = aws_key_pair.rrt-key-pair.key_name
  security_groups = [aws_security_group.allow_ssh.name]
}

resource "aws_security_group" "allow_ssh" {
  name = "allow_ssh"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}


resource "aws_key_pair" "rrt-key-pair" {
  key_name   = "rrt-key-pair"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7LYjZkXqiogoq9ge8dLAvICihPHv97VHMN1u+9xDacMblHhQGLXUAhMaqeNXw7eMk1zyKRdWrTcdptB6oVRGGgySqttjBc23/F3oiU4sPZHhshDdoaDSubflt1mNNercEyzCfSlYFYRZ2fJqxr7CleQWDVqMHwuwx9qZAsVyDfWtYja8eLVg7OH+dEjp3+ddXnLH0F/WNBKUF3wypJNbLGf7EvPZG5yXIZ9GLAclfczI4ns01rqaBz6sLBSxaSvSP8q3NEtYSy8bqQEZyE+07guLN2AeLH2ZWl58PbyUUD+GMOHLtyUggOvtI69ZPS3gkxFX2glHVCMerqbZuskeJ thiba@DESKTOP-06IB7K5"
}

resource "aws_kms_key" "mykey" {
  description             = "This key is used to encrypt bucket objects"
  deletion_window_in_days = 10
}

resource "aws_s3_bucket" "mybucket" {
  bucket = "rrt-data-storage-1"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.mykey.arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
}


#resource "null_resource" "setup_bat" {
#    provisioner "local-exec" {
#    command = "echo set dns=${aws_instance.web.public_dns} > config_terraform_cloud.cmd"
#    } 
#}


resource "local_file" "ssh_config" {
    content     = "set dns=${aws_instance.web.public_dns}"
    filename = "config_terraform_cloud.cmd"
    depends_on =  [aws_instance.web]
}

resource "aws_s3_bucket_object" "file1" {
  bucket = aws_s3_bucket.mybucket.id
  key    = "label"
  source = "data_out/label.csv"
}

resource "aws_s3_bucket_object" "file2" {
  bucket = aws_s3_bucket.mybucket.id
  key    = "data"
  source = "data_out/data.json"
}

resource "aws_s3_bucket_object" "file3" {
  bucket = aws_s3_bucket.mybucket.id
  key    = "categories_string"
  source = "data_out/categories_string.csv"
}