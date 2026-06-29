output "vm_public_ip" {
  value       = google_compute_address.static_ip.address
  description = "IP Público Estático reservado e associado à máquina virtual"
}

output "ssh_command" {
  value       = "ssh ${var.ssh_username}@${google_compute_address.static_ip.address}"
  description = "Comando rápido para se conectar via SSH à VM"
}
