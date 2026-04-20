variable "compute_flavor" {
  type    = string
  default = "Basic-1-2-20"
}

variable "key_pair_name" {
  type = string
  default = "service-desk-vm"
}
variable "availability_zone_name" {
  type = string
  default = "MS1"
}