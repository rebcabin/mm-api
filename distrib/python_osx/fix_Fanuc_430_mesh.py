import mmapi
from mmRemote import *
import subprocess

app_path = '/Applications/Meshmixer.app/Contents/MacOS/meshmixer'

asset_dir = '/Users/bbeckman/Documents/Ops-robotics-rsimcon/content/raw/mesh' \
            '/64907_Fanuc_430_Robot/'

asset_file = "test_submesh_001"

def append_mesh_file(remote, dyr, nym, typ):
    cmd = mmapi.StoredCommands()
    cmd.AppendSceneCommand_AppendMeshFile(dyr +  nym + '.' + typ)
    remote.runCommand(cmd)

def show_all (remote):
    cmd = mmapi.StoredCommands()
    cmd.AppendSceneCommand_ShowAll()
    cmd.ViewControl_SetShowWireframe(True)
    cmd.ViewControl_SetShowBoundaries(True)
    remote.runCommand(cmd)

def close_cracks (remote):
    cmd = mmapi.StoredCommands()
    cmd.AppendBeginToolCommand("closeCracks")
    cmd.AppendCompleteToolCommand("accept")
    remote.runCommand(cmd)

def repair_defects (remote):
    cmd = mmapi.StoredCommands()
    cmd.AppendBeginToolCommand("inspector")
    cmd.AppendToolUtilityCommand("repairAll")
    cmd.AppendCompleteToolCommand("accept")
    remote.runCommand(cmd)

def export_selection (remote, dyr, nym, typ):
    cmd = mmapi.StoredCommands()
    cmd.AppendSceneCommand_ExportMeshFile_CurrentSelection(
        dyr + nym + '_repaired' + '.' + typ)
    remote.runCommand(cmd)

def fix_a_mesh (dyr, nym, typ):
    mm = subprocess.Popen([app_path])

    remote = mmRemote()
    remote.connect()

    append_mesh_file(remote, dyr, nym, typ)
    show_all(remote)
    close_cracks(remote)
    repair_defects(remote)
    export_selection(remote, dyr, nym, "obj")

    remote.shutdown()

    mm.kill()
    pass

meshes = [('test_submesh_%0.3d' % (i+1)) for i in range(21)]
map(lambda mesh:fix_a_mesh(asset_dir, mesh, "off"), meshes)

# mm = subprocess.Popen([app_path])
#
# remote = mmRemote()
# remote.connect()
#
# append_mesh_file(remote, asset_dir, asset_file, "off")
# show_all(remote)
# close_cracks(remote)
# repair_defects(remote)
# export_selection(remote, asset_dir, asset_file, "obj")
#
# remote.shutdown()
#
# mm.kill()