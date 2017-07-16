from __future__ import print_function
import mmapi
from mmRemote import *
import subprocess
import time

app_path = '/Applications/Meshmixer.app/Contents/MacOS/meshmixer'

asset_dir = '/Users/bbeckman/Documents/Ops-robotics-rsimcon/content/raw/mesh' \
            '/64907_Fanuc_430_Robot/'

asset_file_name_prefix = 'armature_rigging_groups_submesh'


# TODO import from mm
def vectori_to_list(vi):
    """convert a SWIG vectori object to a Python list"""
    sz = vi.size()
    lst = []
    for i in xrange(0, sz):
        lst.append ( vi[i] )
    return lst

# TODO: log instead of print

def append_mesh_file(remote, dyr, nym, typ):
    cmd = mmapi.StoredCommands()
    input_file_name = dyr +  nym + '.' + typ
    key = cmd.AppendSceneCommand_AppendMeshFile(input_file_name)
    remote.runCommand(cmd)
    objs_veci = mmapi.vectori()
    cmd.GetSceneCommandResult_AppendMeshFile(key, objs_veci)
    objs = vectori_to_list(objs_veci)
    print({'result_key_from_append_mesh': key,
           'asset_dir': dyr,
           'input_mesh_file_name': input_file_name,
           'input_mesh_file_type': typ,
           'first_obj': objs[0] if objs else None,
           'last_obj': objs[-1] if objs else None,
           'number_of_objs': len(objs)})

def show_all (remote):
    cmd = mmapi.StoredCommands()
    key = cmd.AppendSceneCommand_ShowAll()
    remote.runCommand(cmd)
    print ({'result_from_show_all':
                cmd.GetSceneCommandResult_IsOK(key)})
    cmd = mmapi.StoredCommands()
    cmd.ViewControl_SetShowWireframe(True) # void; no result to check
    remote.runCommand(cmd)
    cmd = mmapi.StoredCommands()
    cmd.ViewControl_SetShowBoundaries(True) # void; no result to check
    remote.runCommand(cmd)

def close_cracks (remote):
    cmd = mmapi.StoredCommands()
    cmd.AppendBeginToolCommand("closeCracks") # void; no result to check
    cmd.AppendCompleteToolCommand("accept") # void: no result to check
    remote.runCommand(cmd)

def repair_defects (remote):
    cmd = mmapi.StoredCommands()
    cmd.AppendBeginToolCommand("inspector") # void: no result to check
    cmd.AppendToolUtilityCommand("repairAll") # void: no result to check
    cmd.AppendCompleteToolCommand("accept") # void: no result to check
    remote.runCommand(cmd)

def export_selection (remote, dyr, nym, typ):
    cmd = mmapi.StoredCommands()
    output_file_name = dyr + nym + '_repaired' + '.' + typ
    key = cmd.AppendSceneCommand_ExportMeshFile_CurrentSelection(
        output_file_name)
    remote.runCommand(cmd)
    print({'result_key_from_export_selection': key,
           'result_from_export_selection': cmd.GetSceneCommandResult_IsOK(key),
           'asset_dir': dyr,
           'output_mesh_file_name': output_file_name,
           'output_mesh_file_type': typ})

def clear_scene (remote):
    cmd = mmapi.StoredCommands()
    cmd.AppendSceneCommand_Clear() # void; no result to check
    remote.runCommand(cmd)

def fix_mesh (dyr, nym, remote, in_typ ='off', out_typ = 'obj'):
    clear_scene(remote)
    append_mesh_file(remote, dyr, nym, in_typ)
    show_all(remote)
    close_cracks(remote)
    repair_defects(remote)
    export_selection(remote, dyr, nym, out_typ)

def erect_fixture():
    '''Returns tuple of app subprocess and remote connection.'''
    mm = subprocess.Popen([app_path])
    # TODO: VERY BAD, but I have not yet found a reliable way to synchronize
    # the app. This function hangs if the app has been started but is not
    # yet ready to accept commands.
    time.sleep(5.0)
    remote = mmRemote()
    remote.connect()
    return mm, remote

def tear_down_fixture(remote, mm):
    clear_scene(remote)
    remote.shutdown()
    mm.terminate()

def fix_meshes (dyr, nym_prefix, rg, in_typ ='off', out_typ ='obj'):
    mm, remote = erect_fixture()
    meshes = [('%s_%03d' % (nym_prefix, (i+1))) for i in range(rg)]
    results = [(fix_mesh(dyr, m, remote, in_typ, out_typ)) for m in meshes]
    tear_down_fixture(remote, mm)

fix_meshes(asset_dir, asset_file_name_prefix, 21)
