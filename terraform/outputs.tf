output "project_id" {
  description = "Google Cloud project ID."
  value       = var.project_id
}

output "instance_name" {
  description = "Compute Engine instance name."
  value       = google_compute_instance.foodrush_vm.name
}

output "instance_zone" {
  description = "Compute Engine instance zone."
  value       = google_compute_instance.foodrush_vm.zone
}

output "public_ip" {
  description = "Public IP address of the Compute Engine instance."
  value       = google_compute_instance.foodrush_vm.network_interface[0].access_config[0].nat_ip
}
