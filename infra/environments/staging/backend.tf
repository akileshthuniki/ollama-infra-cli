# ==========================================
# S3 Bucket for State File Storage
# ==========================================
# Backend Configuration
terraform {
  backend "s3" {
    bucket = "ollama-state-files"
    key    = "terraform/state/staging.tfstate"
    region = "us-east-1"
    use_lockfile = true
  }
}
