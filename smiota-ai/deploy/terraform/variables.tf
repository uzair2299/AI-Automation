variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "smiota-cloud-prod"
}

variable "region" {
  description = "GCP primary region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "network_name" {
  description = "VPC Network name"
  type        = string
  default     = "default"
}

variable "subnet_name" {
  description = "VPC Subnet name"
  type        = string
  default     = "default"
}

variable "min_nodes" {
  description = "Minimum node count for GKE node pool"
  type        = number
  default     = 3
}

variable "max_nodes" {
  description = "Maximum node count for GKE node pool"
  type        = number
  default     = 15
}
