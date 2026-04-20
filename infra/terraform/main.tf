data "vkcs_compute_flavor" "compute" {
  name = var.compute_flavor
}

data "vkcs_images_image" "compute" {
  visibility = "public"
  default    = true

  properties = {
    mcs_os_distro  = "ubuntu"
    mcs_os_version = "24.04"
  }
}

data "vkcs_networking_network" "extnet" {
  name = "internet"
}

resource "vkcs_compute_instance" "service_desk_vm" {
  name              = "service-desk-vm"
  flavor_id         = data.vkcs_compute_flavor.compute.id
  key_pair          = var.key_pair_name
  security_groups   = [
    "default",
    "ssh",
    vkcs_networking_secgroup.service_desk_secgroup.name,
  ]
  availability_zone = var.availability_zone_name

  block_device {
    uuid                  = data.vkcs_images_image.compute.id
    source_type           = "image"
    destination_type      = "volume"
    volume_type           = "ceph-ssd"
    volume_size           = 20
    boot_index            = 0
    delete_on_termination = true
  }

  network {
    uuid = vkcs_networking_network.service_desk_network.id
  }

  depends_on = [
    vkcs_networking_network.service_desk_network,
    vkcs_networking_subnet.service_desk_subnet
  ]
}

resource "vkcs_networking_floatingip" "fip" {
  pool = data.vkcs_networking_network.extnet.name
}

resource "vkcs_compute_floatingip_associate" "fip" {
  floating_ip = vkcs_networking_floatingip.fip.address
  instance_id = vkcs_compute_instance.service_desk_vm.id
}

output "instance_fip" {
  value = vkcs_networking_floatingip.fip.address
}