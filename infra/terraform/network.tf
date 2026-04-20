data "vkcs_networking_network" "external" {
  sdn      = "sprut"
  external = true
}

resource "vkcs_networking_network" "service_desk_network" {
  name = "service-desk-net"
  sdn  = "sprut"
}

resource "vkcs_networking_subnet" "service_desk_subnet" {
  name       = "service-desk-subnet"
  network_id = vkcs_networking_network.service_desk_network.id
  cidr       = "192.168.199.0/24"
}

resource "vkcs_networking_router" "service_desk_router" {
  name                = "service-desk-router"
  sdn                 = "sprut"
  external_network_id = data.vkcs_networking_network.external.id
}

resource "vkcs_networking_router_interface" "service_desk_router_interface" {
  router_id = vkcs_networking_router.service_desk_router.id
  subnet_id = vkcs_networking_subnet.service_desk_subnet.id
}