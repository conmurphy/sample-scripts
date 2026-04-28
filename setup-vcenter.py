# This is used in my lab to help configure some of the base vcenter infrastructure for a shared environment 
# - vm folders, users and RBAC, DVS, port groups (each team receives their own DVS and pre-allocated VLANs/subnets which are configured as port groups on the DVS

from pyvim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
from urllib.parse import quote

# === VCENTER CONNECTION ===
VCENTER_SERVER = '172.16.194.10'
VCENTER_USER = 'administrator@vsphere.local'
VCENTER_PASSWORD = ''
DATACENTER_NAME = 'EMEA'
CLUSTER_NAME = 'Prod'
VCENTER_DOMAIN = "some-domain.com"


THEATRES = {
    'INFRASTRUCTURE': {
        'vlans': [194],
        'subnets': ['172.16.194.0/25'],
    },
    'TEAM-01': {
        'vlans': list(range(1100, 1116)),
        'subnets': [
            '172.16.200.0/26', '172.16.200.64/26', '172.16.200.128/26', '172.16.200.192/26',
            '172.16.201.0/26', '172.16.201.64/26', '172.16.201.128/26', '172.16.201.192/26',
            '172.16.202.0/26', '172.16.202.64/26', '172.16.202.128/26', '172.16.202.192/26',
            '172.16.203.0/26', '172.16.203.64/26', '172.16.203.128/26', '172.16.203.192/26',
        ]
    },
    'TEAM-02': {
        'vlans': list(range(1200, 1232)),
        'subnets': [
            '172.16.208.0/24', # '172.16.208.64/26', '172.16.208.128/26', '172.16.208.192/26',
            '172.16.209.0/26', '172.16.209.64/26', '172.16.209.128/26', '172.16.209.192/26',
            '172.16.210.0/26', '172.16.210.64/26', '172.16.210.128/26', '172.16.210.192/26',
            '172.16.211.0/26', '172.16.211.64/26', '172.16.211.128/26', '172.16.211.192/26',
            '172.16.212.0/26', '172.16.212.64/26', '172.16.212.128/26', '172.16.212.192/26',
            '172.16.213.0/26', '172.16.213.64/26', '172.16.213.128/26', '172.16.213.192/26',
            '172.16.214.0/26', '172.16.214.64/26', '172.16.214.128/26', '172.16.214.192/26',
            '172.16.215.0/26', '172.16.215.64/26', '172.16.215.128/26', '172.16.215.192/26',
        ]
    },
    'TEAM-03': {
        'vlans': list(range(1300, 1332)),
        'subnets': [
            '172.16.216.0/24', #'172.16.216.64/26', '172.16.216.128/26', '172.16.216.192/26',
            '172.16.217.0/26', '172.16.217.64/26', '172.16.217.128/26', '172.16.217.192/26',
            '172.16.218.0/26', '172.16.218.64/26', '172.16.218.128/26', '172.16.218.192/26',
            '172.16.219.0/26', '172.16.219.64/26', '172.16.219.128/26', '172.16.219.192/26',
            '172.16.220.0/26', '172.16.220.64/26', '172.16.220.128/26', '172.16.220.192/26',
            '172.16.221.0/26', '172.16.221.64/26', '172.16.221.128/26', '172.16.221.192/26',
            '172.16.222.0/26', '172.16.222.64/26', '172.16.222.128/26', '172.16.222.192/26',
            '172.16.223.0/26', '172.16.223.64/26', '172.16.223.128/26', '172.16.223.192/26',
        ]
    },
    'TEAM-04': {
        'vlans': list(range(1400, 1432)),
        'subnets': [
            '172.16.224.0/24', #'172.16.224.64/26', '172.16.224.128/26', '172.16.224.192/26',
            '172.16.225.0/26', '172.16.225.64/26', '172.16.225.128/26', '172.16.225.192/26',
            '172.16.226.0/26', '172.16.226.64/26', '172.16.226.128/26', '172.16.226.192/26',
            '172.16.227.0/26', '172.16.227.64/26', '172.16.227.128/26', '172.16.227.192/26',
            '172.16.228.0/26', '172.16.228.64/26', '172.16.228.128/26', '172.16.228.192/26',
            '172.16.229.0/26', '172.16.229.64/26', '172.16.229.128/26', '172.16.229.192/26',
            '172.16.230.0/26', '172.16.230.64/26', '172.16.230.128/26', '172.16.230.192/26',
            '172.16.231.0/26', '172.16.231.64/26', '172.16.231.128/26', '172.16.231.192/26',
        ]
    },
    'TEAM-05': {
        'vlans': list(range(1500, 1532)),
        'subnets': [
            '172.16.232.0/24', #'172.16.232.64/26', '172.16.232.128/26', '172.16.232.192/26',
            '172.16.233.0/26', '172.16.233.64/26', '172.16.233.128/26', '172.16.233.192/26',
            '172.16.234.0/26', '172.16.234.64/26', '172.16.234.128/26', '172.16.234.192/26',
            '172.16.235.0/26', '172.16.235.64/26', '172.16.235.128/26', '172.16.235.192/26',
            '172.16.236.0/26', '172.16.236.64/26', '172.16.236.128/26', '172.16.236.192/26',
            '172.16.237.0/26', '172.16.237.64/26', '172.16.237.128/26', '172.16.237.192/26',
            '172.16.238.0/26', '172.16.238.64/26', '172.16.238.128/26', '172.16.238.192/26',
            '172.16.239.0/26', '172.16.239.64/26', '172.16.239.128/26', '172.16.239.192/26',
        ]
    },
    'TEAM-06': {
        'vlans': list(range(1600, 1632)),
        'subnets': [
            '172.16.240.0/24', #'172.16.240.64/26', '172.16.240.128/26', '172.16.240.192/26',
            '172.16.241.0/26', '172.16.241.64/26', '172.16.241.128/26', '172.16.241.192/26',
            '172.16.242.0/26', '172.16.242.64/26', '172.16.242.128/26', '172.16.242.192/26',
            '172.16.243.0/26', '172.16.243.64/26', '172.16.243.128/26', '172.16.243.192/26',
            '172.16.244.0/26', '172.16.244.64/26', '172.16.244.128/26', '172.16.244.192/26',
            '172.16.245.0/26', '172.16.245.64/26', '172.16.245.128/26', '172.16.245.192/26',
            '172.16.246.0/26', '172.16.246.64/26', '172.16.246.128/26', '172.16.246.192/26',
            '172.16.247.0/26', '172.16.247.64/26', '172.16.247.128/26', '172.16.247.192/26',
        ]
    },
    'TEAM-07': {
        'vlans': list(range(1700, 1732)),
        'subnets': [
            '172.16.248.0/24', #'172.16.248.64/26', '172.16.248.128/26', '172.16.248.192/26',
            '172.16.249.0/26', '172.16.249.64/26', '172.16.249.128/26', '172.16.249.192/26',
            '172.16.250.0/26', '172.16.250.64/26', '172.16.250.128/26', '172.16.250.192/26',
            '172.16.251.0/26', '172.16.251.64/26', '172.16.251.128/26', '172.16.251.192/26',
            '172.16.252.0/26', '172.16.252.64/26', '172.16.252.128/26', '172.16.252.192/26',
            '172.16.253.0/26', '172.16.253.64/26', '172.16.253.128/26', '172.16.253.192/26',
            '172.16.254.0/26', '172.16.254.64/26', '172.16.254.128/26', '172.16.254.192/26',
            '172.16.255.0/26', '172.16.255.64/26', '172.16.255.128/26', '172.16.255.192/26',
        ]
    },
}

def get_obj(content, vimtype, name, folder=None):
    obj = None
    if folder:
        container = folder
    else:
        container = content.rootFolder
    view = content.viewManager.CreateContainerView(container, [vimtype], True)
    for c in view.view:
        if c.name == name:
            obj = c
            break
    view.Destroy()
    return obj

def get_or_create_network_folder(datacenter, folder_name):
    for child in datacenter.networkFolder.childEntity:
        if isinstance(child, vim.Folder) and child.name == folder_name:
            print(f"Network folder '{folder_name}' already exists.")
            return child
    print(f"Creating network folder: {folder_name}")
    return datacenter.networkFolder.CreateFolder(folder_name)

def create_vm_folder(datacenter, folder_name):
    for child in datacenter.vmFolder.childEntity:
        if isinstance(child, vim.Folder) and child.name == folder_name:
            print(f"VM folder '{folder_name}' already exists.")
            return
    print(f"Creating VM folder: {folder_name}")
    datacenter.vmFolder.CreateFolder(folder_name)

def create_storage_folder(datacenter, folder_name):
    for child in datacenter.datastoreFolder.childEntity:
        if isinstance(child, vim.Folder) and child.name == folder_name:
            print(f"Storage folder '{folder_name}' already exists.")
            return
    print(f"Creating storage folder: {folder_name}")
    datacenter.datastoreFolder.CreateFolder(folder_name)

def get_or_create_subfolder(parent_folder, subfolder_name):
    for child in parent_folder.childEntity:
        if isinstance(child, vim.Folder) and child.name == subfolder_name:
            print(f"Subfolder '{subfolder_name}' already exists under '{parent_folder.name}'.")
            return child
    print(f"Creating subfolder '{subfolder_name}' under '{parent_folder.name}'.")
    return parent_folder.CreateFolder(subfolder_name)

def create_user_folder(vm_folder, user):
    for child in vm_folder.childEntity:
        if isinstance(child, vim.Folder) and child.name == user:
            print(f"User folder '{user}' already exists under '{vm_folder.name}'.")
            return child
    print(f"Creating user folder '{user}' under '{vm_folder.name}'.")
    return vm_folder.CreateFolder(user)

def create_dvs(content, network_folder, dvs_name):
    dvs = get_obj(content, vim.DistributedVirtualSwitch, dvs_name, folder=network_folder)
    if not dvs:
        print(f"Creating DVS: {dvs_name} in network folder: {network_folder.name}")
        dvs_spec = vim.DistributedVirtualSwitch.CreateSpec()
        dvs_spec.configSpec = vim.DistributedVirtualSwitch.ConfigSpec()
        dvs_spec.configSpec.name = dvs_name
        task = network_folder.CreateDVS_Task(spec=dvs_spec)
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            continue
    else:
        print(f"DVS '{dvs_name}' already exists in folder '{network_folder.name}'.")

def portgroup_exists_on_dvs(dvs, pg_name):
    encoded_pg_name = quote(pg_name, safe='')
    encoded_pg_name_upper = encoded_pg_name.upper()
    for pg in dvs.portgroup:
        if (
            pg.name == pg_name or
            pg.name == encoded_pg_name or
            pg.name == encoded_pg_name_upper or
            pg.name.lower() == encoded_pg_name.lower()
        ):
            return True
    return False

def create_portgroup(dvs, pg_name, vlan_id):
    if portgroup_exists_on_dvs(dvs, pg_name):
        print(f"Port group '{pg_name}' already exists on DVS '{dvs.name}'.")
        return

    print(f"Creating port group: {pg_name} on DVS: {dvs.name} with VLAN {vlan_id}")
    spec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec()
    spec.name = pg_name
    spec.type = vim.dvs.DistributedVirtualPortgroup.PortgroupType.earlyBinding

    vlan_spec = vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec()
    vlan_spec.vlanId = vlan_id
    vlan_spec.inherited = False

    port_config = vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy()
    port_config.vlan = vlan_spec
    spec.defaultPortConfig = port_config

    try:
        task = dvs.AddDVPortgroup_Task([spec])
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            continue
        if task.info.state == vim.TaskInfo.State.success:
            print(f"Port group '{pg_name}' created with VLAN {vlan_id}")
        else:
            msg = getattr(task.info.error, 'msg', str(task.info.error))
            print(f"Failed to create port group '{pg_name}': {msg}")
    except Exception as e:
        print(f"Failed to create port group '{pg_name}': {str(e)}")

def create_custom_role(content, role_name, privileges):
    auth_manager = content.authorizationManager
    for role in auth_manager.roleList:
        if role.name == role_name:
            print(f"Role '{role_name}' already exists.")
            return role.roleId
    try:
        role_id = auth_manager.AddAuthorizationRole(name=role_name, privIds=privileges)
        print(f"Created role '{role_name}' with privileges: {privileges}")
        return role_id
    except Exception as e:
        print(f"Failed to create role '{role_name}': {e}")
        return None

def assign_permission_to_entity(entity, role_id, group, domain, content, role_name, folder_type, propagate=True):
    principal = f"{domain}\\{group}"
    for perm in entity.permission:
        if perm.principal.lower() == principal.lower() and perm.roleId == role_id:
            print(f"Permission for group '{principal}' with role '{role_name}' already set on {folder_type} '{entity.name}'.")
            return
    perm = vim.AuthorizationManager.Permission()
    perm.principal = principal
    perm.group = True
    perm.propagate = propagate
    perm.roleId = role_id
    try:
        content.authorizationManager.SetEntityPermissions(entity=entity, permission=[perm])
        print(f"Assigned group '{principal}' with role '{role_name}' to {folder_type} '{entity.name}'.")
    except Exception as e:
        print(f"Failed to assign group '{principal}' with role '{role_name}' to {folder_type} '{entity.name}': {e}")

def main():
    context = ssl._create_unverified_context()
    service_instance = SmartConnect(host=VCENTER_SERVER, user=VCENTER_USER, pwd=VCENTER_PASSWORD, sslContext=context)
    content = service_instance.RetrieveContent()
    datacenter = get_obj(content, vim.Datacenter, DATACENTER_NAME)
    cluster = get_obj(content, vim.ClusterComputeResource, CLUSTER_NAME)
    root_folder = content.rootFolder  

    # Get the prod-storage-filer-02-iso datastore (root object, not under a theatre)
    iso_datastore = get_obj(content, vim.Datastore, "prod-storage-filer-02-iso")
    if not iso_datastore:
        print("Warning: 'prod-storage-filer-02-iso' datastore not found!")

    needed_roles = [
        "Lab User - Network Administrator",
        "Lab User - Storage Administrator",
        "Lab User - VM Administrator",
        "Lab User - Server Administrator",
        "Lab User - vCenter User",
        "Lab User - Storage Consumer"
    ]
    role_ids = {}
    for role_name in needed_roles:
        privs = CUSTOM_ROLES[role_name]
        role_id = create_custom_role(content, role_name, privs)
        if role_id:
            role_ids[role_name] = role_id

    NO_ACCESS_ROLE_ID = -1

    for theatre in THEATRES:
        print(f"\n--- Processing {theatre} ---")
        group = theatre

        network_folder = get_or_create_network_folder(datacenter, theatre)
        dvs_name = f"{theatre}"
        create_dvs(content, network_folder, dvs_name)
        dvs = get_obj(content, vim.DistributedVirtualSwitch, dvs_name, folder=network_folder)

        for vlan, subnet in zip(THEATRES[theatre]['vlans'], THEATRES[theatre]['subnets']):
            pg_name = f"{vlan}_{subnet}"
            create_portgroup(dvs, pg_name, vlan)

    #     create_vm_folder(datacenter, theatre)
    #     create_storage_folder(datacenter, theatre)

    #     vm_folder = get_obj(content, vim.Folder, theatre, folder=datacenter.vmFolder)
    #     storage_folder = get_obj(content, vim.Folder, theatre, folder=datacenter.datastoreFolder)
    #     net_folder = network_folder

    #     # Storage folder: Storage admin, vCenter user, server admin
    #     if storage_folder and "Lab User - Storage Administrator" in role_ids:
    #         assign_permission_to_entity(storage_folder, role_ids["Lab User - Storage Administrator"], group, VCENTER_DOMAIN, content, "Lab User - Storage Administrator", "Storage folder")

    #     # Network folder: Network admin, vCenter user, server admin
    #     if net_folder and "Lab User - Network Administrator" in role_ids:
    #         assign_permission_to_entity(net_folder, role_ids["Lab User - Network Administrator"], group, VCENTER_DOMAIN, content, "Lab User - Network Administrator", "Network folder")

    #     # Cluster: Server admin only
    #     if cluster and "Lab User - Server Administrator" in role_ids:
    #         assign_permission_to_entity(cluster, role_ids["Lab User - Server Administrator"], group, VCENTER_DOMAIN, content, "Lab User - Server Administrator", "Cluster")

    #     if vm_folder:
    #         users_folder = get_or_create_subfolder(vm_folder, "Users")
    #         # Assign built-in No Access to the theatre group at the Users folder, propagate=True
    #         # assign_permission_to_entity(
    #         #     users_folder,
    #         #     -1,  # built-in No Access roleId
    #         #     group,
    #         #     VCENTER_DOMAIN,
    #         #     content,
    #         #     "No Access",
    #         #     f"Users folder in {theatre}"
    #         # )
    #         for user, user_theatre in USER_THEATRE_MAP.items():
    #             if user_theatre != theatre:
    #                 continue
    #             user_folder = create_user_folder(users_folder, user)
    #             # Assign VM Admin to the user at their own folder
    #             assign_permission_to_entity(
    #                 user_folder,
    #                 role_ids["Lab User - VM Administrator"],
    #                 user,
    #                 VCENTER_DOMAIN,
    #                 content,
    #                 "Lab User - VM Administrator",
    #                 f"User folder ({user})"
    #             )

    # # Assign Storage Consumer to ISO datastore for all groups
    # if iso_datastore and "Lab User - Storage Consumer" in role_ids:
    #     for group in GROUPS:
    #         assign_permission_to_entity(
    #             iso_datastore,
    #             role_ids["Lab User - Storage Consumer"],
    #             group,
    #             VCENTER_DOMAIN,
    #             content,
    #             "Lab User - Storage Consumer",
    #             "ISO Datastore"
    #         )

    # # vCenter (Root folder): vCenter user for all groups
    # for group in GROUPS:
    #     if "Lab User - vCenter User" in role_ids:
    #         assign_permission_to_entity(
    #             root_folder,
    #             role_ids["Lab User - vCenter User"],
    #             group,
    #             VCENTER_DOMAIN,
    #             content,
    #             "Lab User - vCenter User",
    #             "vCenter Root",
    #             propagate=False
    #         )

    Disconnect(service_instance)

if __name__ == "__main__":
    main()
