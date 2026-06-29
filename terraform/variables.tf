variable "gcp_project_id" {
  type        = string
  description = "ID do projeto do Google Cloud onde a VM será implantada"
}

variable "gcp_region" {
  type        = string
  default     = "us-central1"
  description = "Região onde os recursos do GCP serão provisionados"
}

variable "gcp_zone" {
  type        = string
  default     = "us-central1-a"
  description = "Zona específica para a criação da VM no GCP"
}

variable "ssh_username" {
  type        = string
  description = "Nome de usuário do SSH na VM (ex: ubuntu ou seu usuário)"
}

variable "ssh_public_key" {
  type        = string
  description = "Chave SSH pública autorizada a acessar a VM para deploy"
}
