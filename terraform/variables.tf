# Scope.Vantage Terraform Variables

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "scope-vantage"
}

variable "glue_database" {
  description = "AWS Glue database name"
  type        = string
  default     = "scope_vantage"
}

variable "bedrock_model_id" {
  description = "Amazon Bedrock Converse API model ID. Defaults to the Amazon Nova Lite cross-region inference profile (us-east-1). Anthropic Claude IDs are rejected: Claude on Bedrock is an AWS Marketplace product and is not covered by promo credits."
  type        = string
  default     = "us.amazon.nova-lite-v1:0"

  validation {
    condition     = !strcontains(lower(var.bedrock_model_id), "anthropic.")
    error_message = "Anthropic Claude models are not allowed. Claude on Amazon Bedrock is billed through AWS Marketplace and is IAM-denied on this account. Use an Amazon Nova model such as us.amazon.nova-lite-v1:0."
  }
}

variable "un_comtrade_key" {
  description = "UN Comtrade API subscription key"
  type        = string
  default     = ""
  sensitive   = true
}

variable "alpha_vantage_key" {
  description = "AlphaVantage API key"
  type        = string
  default     = ""
  sensitive   = true
}

variable "fred_api_key" {
  description = "FRED API key"
  type        = string
  default     = ""
  sensitive   = true
}
