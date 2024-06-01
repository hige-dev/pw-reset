terraform {
    backend "s3" {
    # terraform init -backend-config="bucket=backend.bucket"
    #    bucket = "tfstate-${var.account_id}"
       key    = "terraform.tfstate"
       region = "ap-northeast-1"
    }

    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "5.47.0"
        }
    }
}

provider "aws" {
    region  = "ap-northeast-1"
}
