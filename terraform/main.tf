# Define required providers
terraform {
  # Ensure the use of a compatible Terraform version
  required_version = ">= 0.14.0"
  required_providers {
    # Define OpenStack terraform provider
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 3.0.0"# (1)!
    }
  }
}

# Configure the OpenStack Provider
provider "openstack" {
  auth_url    = "https://api.pub1.infomaniak.cloud/identity"
  region      = "dc3-a"
  user_name   = openshift_user
  tenant_name = openshift_project
  password    = openshift_pwd
}
