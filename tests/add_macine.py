


from juju.model import Model
import asyncio
from juju import loop
async def add_machine():
	os_series = "xenial"
	memory = 512
	cpu = 1
	disc_size = 5
	ssh_key_private = "/home/arouk/.ssh/id_juju"
	ssh_key_puplic = "/home/arouk/.ssh/id_juju.pub"
	SSH_USER = "ubuntu"
	SSH_PASSWORD = "linux"
	cmd_list_kvm = ["uvt-kvm", "list"]
	machine_ip = "192.168.122.77"
	model = Model()
	await model.connect_current()
	await asyncio.sleep(10)
	juju_cmd = "".join(["ssh:", SSH_USER, "@", machine_ip, ":", ssh_key_private])
	juju_machine = await model.add_machine()
	
	await model.disconnect()

print("START")
loop.run(add_machine())
print("EXIST")
