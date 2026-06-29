terraform {
  required_version = ">= 1.0.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  zone    = var.gcp_zone
}

# Reserva de IP Externo Estático (Gratuito enquanto associado a uma VM ligada)
resource "google_compute_address" "static_ip" {
  name = "tcc-server-static-ip"
}

# Regra de Firewall para permitir tráfego HTTP, HTTPS e SSH de qualquer lugar
resource "google_compute_firewall" "allow_web" {
  name    = "allow-tcc-web-traffic"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22", "80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["tcc-web-server"]
}

# Instância de VM E2-Micro (Qualificada para o Free Tier da GCP)
resource "google_compute_instance" "vm_instance" {
  name         = "tcc-central-server"
  machine_type = "e2-micro" # 100% elegível para o Free Tier
  zone         = var.gcp_zone

  tags = ["tcc-web-server"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts" # Ubuntu 22.04 LTS
      size  = 30                                # Limite máximo de 30GB gratuitos no Free Tier
      type  = "pd-standard"                     # Disco permanente padrão (standard)
    }
  }

  network_interface {
    network = "default"

    access_config {
      nat_ip = google_compute_address.static_ip.address # Associa o IP Estático Reservado
    }
  }

  metadata = {
    ssh-keys = "${var.ssh_username}:${var.ssh_public_key}"
  }

  # Script de inicialização automática da VM (Instala Docker, Docker Compose e ativa Swap de 4GB)
  metadata_startup_script = <<-EOT
    #!/bin/bash
    set -e

    # Ativar Swap de 4GB se não estiver ativa
    if [ ! -f /swapfile ]; then
      fallocate -l 4G /swapfile
      chmod 600 /swapfile
      mkswap /swapfile
      swapon /swapfile
      echo '/swapfile none swap sw 0 0' >> /etc/fstab
    fi

    # Atualizar repositórios e pacotes
    apt-get update
    apt-get upgrade -y

    # Instalar Docker e Docker Compose
    if ! command -v docker &> /dev/null; then
      apt-get install -y docker.io docker-compose
      systemctl start docker
      systemctl enable docker
    fi
  EOT
}
