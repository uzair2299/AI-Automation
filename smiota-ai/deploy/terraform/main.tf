terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.30.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# GKE Cluster for Multi-Agent Smiota Workloads
resource "google_container_cluster" "smiota_cluster" {
  name     = "${var.environment}-smiota-gke"
  location = var.region

  remove_default_node_pool = true
  initial_node_count       = 1

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  network    = var.network_name
  subnetwork = var.subnet_name
}

# Node Pool for Agent API and MCP Workers
resource "google_container_node_pool" "agent_nodes" {
  name       = "agent-core-pool"
  location   = var.region
  cluster    = google_container_cluster.smiota_cluster.name
  node_count = var.min_nodes

  autoscaling {
    min_node_count = var.min_nodes
    max_node_count = var.max_nodes
  }

  node_config {
    preemptible  = false
    machine_type = "e2-standard-4"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      workload = "smiota-ai-agent"
    }
  }
}

# Cloud SQL PostgreSQL Instance with pgvector support
resource "google_sql_database_instance" "smiota_db_instance" {
  name             = "${var.environment}-smiota-postgres"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-custom-2-7680"
    database_flags {
      name  = "cloudsql.enable_pgvector"
      value = "on"
    }
  }
}

# Cloud SQL Database
resource "google_sql_database" "smiota_db" {
  name     = "smiota_ai"
  instance = google_sql_database_instance.smiota_db_instance.name
}

# Memorystore Redis for Session Cache and Agent State
resource "google_redis_instance" "smiota_redis" {
  name           = "${var.environment}-smiota-cache"
  tier           = "STANDARD_HA"
  memory_size_gb = 5
  region         = var.region
}
