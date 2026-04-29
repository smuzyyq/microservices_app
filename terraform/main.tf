terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_compute_instance" "foodrush_vm" {
  name         = "${var.project_name}-${var.environment}-vm"
  machine_type = var.machine_type
  zone         = var.zone
  tags         = [var.network_tag]

  boot_disk {
    initialize_params {
      image = var.boot_image
      size  = var.boot_disk_size_gb
      type  = "pd-balanced"
    }
  }

  network_interface {
    network = "default"

    access_config {
    }
  }

  metadata = {
    enable-oslogin = "FALSE"
  }
}

resource "google_compute_firewall" "foodrush_ingress" {
  name    = "${var.project_name}-${var.environment}-allow-ingress"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22", "80", "3000", "9090"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = [var.network_tag]
}
