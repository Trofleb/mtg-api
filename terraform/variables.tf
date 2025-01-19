variable "openshift_pwd" {
  description = "Password for OpenShift authentication"
  type        = string
  sensitive   = true
}

variable "openshift_project" {
  description = "Project for OpenShift authentication"
  type        = string
  sensitive   = true
}

variable "openshift_user" {
  description = "User for OpenShift authentication"
  type        = string
  sensitive   = true
}
