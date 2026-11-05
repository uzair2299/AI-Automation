output "gke_cluster_name" {
  description = "GKE Cluster identifier"
  value       = google_container_cluster.smiota_cluster.name
}

output "cloudsql_connection_name" {
  description = "Cloud SQL instance connection string"
  value       = google_sql_database_instance.smiota_db_instance.connection_name
}

output "redis_host" {
  description = "Memorystore Redis primary host"
  value       = google_redis_instance.smiota_redis.host
}
