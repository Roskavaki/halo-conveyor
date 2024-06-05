import bpy
from mathutils import Matrix
from bpy.types import (Panel, Operator,AddonPreferences,PropertyGroup)

from bpy.props import (StringProperty, BoolProperty,
                       IntProperty, FloatProperty,
                       EnumProperty, PointerProperty, )

bl_info = {
    "name": "halo-conveyors",
    "author": "Roskavaki",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Side tab called Conveyor",
    "support": "COMMUNITY",
    "category": "3D View",
}

''' Duplicate object x with linked data '''
def duplicateNamedObject(x='noob',prefix=""):    
    object_to_duplicate = bpy.data.objects[x]
    
    # Select the object.
    bpy.context.view_layer.objects.active = object_to_duplicate
    object_to_duplicate.select_set(True)

    # Duplicate the object.
    bpy.ops.object.duplicate(linked=True)

    # The duplicated object is now the active one.
    duplicated_object = bpy.context.active_object
    
    duplicated_object.select_set(False)
    object_to_duplicate.select_set(False)
    
    return duplicated_object


''' Bone spacing '''
def set_bone_offsets(mult=1, armature_name="Armature"):    
    offset_multiplier = mult
    i=0
    arma = bpy.data.objects[armature_name]
    mybones = arma.pose.bones
    
    for b in mybones:
        bone_constraints = b.constraints
        if len(b.constraints)<1:
            continue
        i+=1
        b.constraints["Follow Path"].offset  = i*offset_multiplier
        #bpy.data.armatures[armature_name].bones[b.name].use_relative_parent = True


''' parent object to bone '''
def parent_duplicate(object_name='step', bone_name='Bone', armature_name="Armature"):
    #print( f"obj {object_name} , {bone_name}" )
    objects = bpy.data.objects
    a = objects[armature_name]
    b = objects[object_name]
    b.parent = a
    b.parent_bone = bone_name
    b.parent_type = 'BONE'


def createNewBone( bone_name='Bone', armature='Armature'):    
    armatur = bpy.data.objects[armature]
    view_layer = bpy.context.view_layer
    armatur.select_set(True)
    view_layer.objects.active = armatur

    bpy.ops.object.mode_set(mode='EDIT')

    # Create a new bone
    bones = armatur.data.edit_bones
    new_bone = bones.new(bone_name)
    new_bone.head = (0, 0, 0)
    new_bone.tail = (0, 0, 1)
    
    #new_bone.parent = bpy.data.armatures[ARMATURE].bones["root"]
    new_bone.parent = bones["root"]
    return new_bone


def deleteBone(bone_name="Bone", armature="Armature"):
    #print(f'delete {bone_name} on {armature}')
    armobj = bpy.data.objects[armature]
    armobj.select_set(True)
    view_layer = bpy.context.view_layer
    view_layer.objects.active = armobj
    
    arm = armobj.data
    bones = arm.bones
    to_delete = [bone_name]
    
    bpy.ops.object.mode_set(mode='EDIT')
    for name in to_delete:        
        if arm.edit_bones[name]:
            arm.edit_bones.remove(arm.edit_bones[name])
    
    bpy.ops.object.mode_set(mode='OBJECT')
    

''' Adds a Follow Path constraint to a bone '''
def addConstrainToBone(bone_name="Bone", offset=1, armature_name="Armature", bezier_name="BezierCircle", follow=False, forward='FORWARD_X', up='UP_Z'):
    #print(f"add constraint to {bone_name}")
    
    # Select armature and bone to add constraint to
    armature = bpy.data.objects[armature_name]
    armature.select_set(True)
    
    # Ensure you're in Pose Mode
    bpy.ops.object.posemode_toggle()
    
    bone = armature.pose.bones[bone_name]

    # Add a new constraint to the bone
    constraint = bone.constraints.new(type="FOLLOW_PATH")

    # Set the target of the constraint (if applicable)
    constraint.target = bpy.data.objects[bezier_name]
    constraint.offset=offset
    constraint.influence = 1.0  # Full influence
    constraint.use_curve_follow = follow
    constraint.forward_axis = forward   
    constraint.up_axis=up


''' Delete bones not named root'''
def delbones(armaturename="Armature", rootbone_name="root"):
    mybones = bpy.data.objects[armaturename].pose.bones    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')    
    for b in mybones:
        if b.name == rootbone_name:
            continue
        deleteBone(b.name, armaturename)


''' Numbered duplicates of object which have .001 .002 etc in their name'''
def deleteCopies(name="name"):
    xx = filter(lambda x: x.name.startswith(name+'.'), bpy.data.objects)
    for i in xx:
        #print(f"Deleting {i.name}")
        object_to_delete = bpy.data.objects[i.name]
        bpy.data.objects.remove(object_to_delete, do_unlink=True)


''' Create bones with constraints as children of root '''
def create_n_bones(n=1,spacing=2,armature_name="Armature", path="BezierCircle", mesh_name="step", phys_name="step_phys", col_name="step_col", follow=False, forward='FORWARD_X', up='UP_Z', relative_par=True):
    # Return to Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')
        
    armature = bpy.data.objects[armature_name]
    bpy.ops.object.posemode_toggle()
    
    #add root bone if needed
    if "root" not in armature.pose.bones:
        print("creating bone named root")
        createNewBone('root' , armature_name)
    
    # Create bones
    bonesCreated = []
    for i in range(0,n):
        new_bone = createNewBone('Bone' , armature_name)
        new_bone.use_relative_parent = relative_par
        bonesCreated.append(new_bone.name)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add constraints to bones
    x=0
    for i in bonesCreated:
        addConstrainToBone(i , x*spacing, armature_name, path, follow, forward, up)
        x+=1
    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
      
    dups = []
    phys_dups = []
    col_dups = []
    
    # Create meshes
    for i in bonesCreated:
        dup = duplicateNamedObject(mesh_name)
        dup.location.x=0
        dup.location.y=0
        dup.location.z=0
        dups.append(dup.name)
    
    for i in bonesCreated:
        dup = duplicateNamedObject(phys_name,"$")
        dup.location.x=0
        dup.location.y=0
        dup.location.z=0
        phys_dups.append(dup.name)
    
    for i in bonesCreated:
        dup = duplicateNamedObject(col_name,"@")
        dup.location.x=0
        dup.location.y=0
        dup.location.z=0
        col_dups.append(dup.name)
    
    bpy.ops.object.select_all(action='DESELECT')
        
    #parent meshes to bones
    for i in range(0,n):
        parent_duplicate(dups[i] , bonesCreated[i])

    print( phys_dups)
    for i in range(0,n):
        parent_duplicate(phys_dups[i] , bonesCreated[i])
        bpy.data.objects[phys_dups[i]].name="$"+phys_dups[i]
        
    for i in range(0,n):
        parent_duplicate(col_dups[i] , bonesCreated[i])
        bpy.data.objects[col_dups[i]].name="@"+col_dups[i]


'''The main function '''
def spawnSteps(armature_name="Armature", path="BezierCircle", mesh_name="step", physmesh="step_phys", colmesh="step_col", steps=1, spacing=4, follow=False, forward='FORWARD_X', up='UP_Z', relativeParent=True):    
    if steps<1:
        print("must have at least 1 step")
        return
    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    arm = bpy.data.objects[armature_name]
    arm.select_set(True)
    
    view_layer = bpy.context.view_layer
    view_layer.objects.active = arm

    #delete previous duplicated meshes
    deleteCopies(mesh_name)
    deleteCopies("$"+physmesh)
    deleteCopies("@"+colmesh)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    #delete all except root bone
    delbones(armature_name,"root")
    
    create_n_bones(steps,spacing, armature_name, path, mesh_name, physmesh, colmesh, follow, forward, up, relativeParent)

'''Execute'''
class AddStepsBtn(Operator):
    bl_idname="object.addsteps"
    bl_label="add steps"
    bl_region_type = 'UI'
    
    def execute(self,context):        
        cs = context.scene        
        spawnSteps(cs.armatureName, cs.bezierName, cs.renderMeshName, cs.physMeshName, cs.colMeshName, cs.numSteps, cs.spacing, cs.followPath, cs.fwd, cs.up, cs.relativeParent)
        return {'FINISHED'}

'''Update spacing between the steps'''
class UpdateSpacingBtn(Operator):
    bl_idname="object.updatespaccing"
    bl_label="update spacing"
    bl_region_type = 'UI'
    
    def execute(self,context):
        print("update spacing")
        cs = context.scene
        set_bone_offsets(cs.spacing, cs.armatureName)
        return {'FINISHED'}
    

class HelloWorldPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Conveyor Maker"
    bl_idname = 'PT_TestPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Conveyor"
    bl_context = "objectmode"
    
    def draw(self, context):
        layout = self.layout
                
        row = layout.row()
        row.label(text="1 Create a Bezier Circle")
        
        row = layout.row()
        row.label(text="2 Create an Armature with a bone called root")
        row = layout.row()
        row.label(text="Position the armature center at the exact same spot as the bezier circle pivot")
        
        row = layout.row()
        row.label(text="3 Create mesh objects")
        
        row = layout.row()
        row.label(text="4 Execute")
        
        row = layout.row()
        row.label(text="5 Select the armature. In pose mode, click 'Animate Path' on any of bone constraints. Only needed once.")
                        
        row = layout.row()
        row.prop(context.scene, "bezierName", text="BezierCircle")
        
        row = layout.row()
        row.prop(context.scene, "armatureName", text="armature")
        
        row = layout.row()
        row.prop(context.scene, "renderMeshName", text="render mesh")
                
        row = layout.row()
        row.prop(context.scene, "physMeshName", text="phys mesh")

        row = layout.row()
        row.prop(context.scene, "colMeshName", text="collision mesh")
        
        row = layout.row()
        row.prop(context.scene, "numSteps", text="Steps")
        
        row = layout.row()
        row.prop(context.scene, "spacing", text="Spacing")
        
        row = layout.row()
        row.prop(context.scene, "followPath", text="Follow Path")

        row = layout.row()
        row.prop(context.scene, "relativeParent", text="Relative Parent")

        row = layout.row()
        row.prop(context.scene, "fwd", text="Forward")

        row = layout.row()
        row.prop(context.scene, "up", text="Up")
                    
        row = layout.row()
        row.operator(AddStepsBtn.bl_idname, text="Execute", icon="CONSOLE")
        
        row = layout.row()
        row.operator(UpdateSpacingBtn.bl_idname, text="Update spacing only", icon="CONSOLE")
        

classes = (
    AddStepsBtn,
    UpdateSpacingBtn,
    HelloWorldPanel,
)

def register():    
    bpy.types.Scene.fwd = bpy.props.EnumProperty(
        name="Fwd",
        default = 'FORWARD_X',
        items=(
            ('FORWARD_X', "X", ""),
            ('FORWARD_Y', "Y", ""),
            ('FORWARD_Z', "Z", ""),
            ('TRACK_NEGATIVE_X', "-X", ""),
            ('TRACK_NEGATIVE_Y', "-Y", ""),
            ('TRACK_NEGATIVE_Z', "-Z", ""),
            ),
        )
        
    bpy.types.Scene.up = bpy.props.EnumProperty(
        name="Up",
        default = 'UP_Z',
        items=(
            ('UP_X', "X", ""),
            ('UP_Y', "Y", ""),
            ('UP_Z', "Z", ""),
            ),
        )
    #https://docs.blender.org/api/current/bpy.ops.constraint.html#bpy.ops.constraint.followpath_path_animate
    
    bpy.types.Scene.relativeParent = bpy.props.BoolProperty(
        name="RelativeParent",
        description="Fixes rotations.",
        default = True)
            
    bpy.types.Scene.followPath = bpy.props.BoolProperty(
        name="FollowPath",
        description="Make elements follow the direction of the path.",
        default = False)
 
    bpy.types.Scene.numSteps = bpy.props.IntProperty(
        name="num steps",
        description="Number of elements in the conveyor",
        default = 1)
        
    bpy.types.Scene.spacing = bpy.props.FloatProperty(
        name="spacing",
        description="Space between steps. Offset property of bone constraints",
        default = 2)
           
    bpy.types.Scene.armatureName = bpy.props.StringProperty(
        name="armature",
        description="Name of armature",
        default = "Armature")
        
    bpy.types.Scene.bezierName = bpy.props.StringProperty(
        name="bezier",
        description="Name of path",
        default = "BezierCircle")
        
    bpy.types.Scene.renderMeshName = bpy.props.StringProperty(
        name="render mesh",
        description="Render mesh",
        default = "step")

    bpy.types.Scene.physMeshName = bpy.props.StringProperty(
        name="physics mesh",
        description="",
        default = "step_phys")
        
    bpy.types.Scene.colMeshName = bpy.props.StringProperty(
        name="collision mesh",
        description="",
        default = "step_col")
        
    for cls in classes:
        bpy.utils.register_class(cls)
    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
