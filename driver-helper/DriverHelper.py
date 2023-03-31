import bpy
from bpy.types import (Panel, Operator)
from bpy.props import (StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty, PointerProperty)

# A simple panel to display a pose bone's custom properties, whether or not that bone is currently selected. 
# This is useful for creating/editing drivers, as well as animating custom properties.

class SwitchToPose(Operator):
    """Enter Pose Mode for the selected rig"""
    bl_idname = "object.switch_to_pose"
    bl_label = "Switch to pose mode"   

    def execute(self, context):
        try:
            objectToSelect = context.scene.objects[context.scene.armature_name]
            bpy.context.active_object.select_set(False)
            objectToSelect.select_set(True)    
            bpy.context.view_layer.objects.active = objectToSelect
            bpy.ops.object.mode_set(mode='POSE')
            print(context.scene.armature_name)
            
        except KeyError:
            print(context.scene.armature_name + " is not a valid rig")
        
        return {'FINISHED'}
    
    
class PinActiveBone(Operator):
    """Pin the current Active Bone to the panel and access its custom properties."""
    bl_idname = "object.pin_bone"
    bl_label = "Pin active bone to panel"
        
    def execute(self, context):
        if (bpy.context.active_pose_bone):
            obj = context.object
            obj.bone_name = bpy.context.active_pose_bone.name
        
        return {'FINISHED'}
    
class DriverHelperBase:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Driver Helper"
    
class DriverHelperPanel(DriverHelperBase, bpy.types.Panel):
    
    bl_idname = 'VIEW3D_PT_driverHelper_panel'
    bl_label = 'Driver Helper'
       
    def draw(self, context):
        
        bPoseMode = (context.mode == 'POSE')
        
        layout = self.layout
        row = layout.row()
        row.prop_search(context.scene, "armature_name", bpy.data, "armatures", text="Rig")
        
        row = layout.row()
        row.operator(SwitchToPose.bl_idname, text="Enter Pose Mode")
        row.enabled = not bPoseMode

class PinnedBonePanel(DriverHelperBase, bpy.types.Panel):
    
    bl_idname = 'VIEW3D_PT_pinnedBone_panel'
    bl_label = 'Pinned Bone'
    bl_parent_id = 'VIEW3D_PT_driverHelper_panel'
    
    def draw(self, context):
        
        layout = self.layout
        
        # Draw a string parameter to select the bone and a button to use the currently active bone as selection
        split = layout.split(factor=0.7)        
        col = split.column()
        try:
            col.prop(context.object, "bone_name", text="Bone", expand=True)
            col = split.column()
            col.operator(PinActiveBone.bl_idname, text="Pin Active")
            
        except TypeError:
            col.label(text="Enter Pose Mode to select a bone")
            
        # Draw custom properties for selected bone, if valid
        try:
            bone = bpy.data.objects["Armature"].pose.bones[context.object.bone_name]
            
            row = layout.row()
            row.label(text=context.object.bone_name + " Properties")
        
            for i in bone.keys():
                row = layout.row()
                row.prop(bone, '["' + i + '"]')
                
        except KeyError:
            row = layout.row()
            row.label(text="'" + context.object.bone_name + "'" + " is not a bone!")
            layout.separator() 
        
CLASSES = [
    DriverHelperPanel, PinnedBonePanel, SwitchToPose, PinActiveBone
]

def register():
    for item in CLASSES:
        bpy.utils.register_class(item)
        
    bpy.types.Object.bone_name = bpy.props.StringProperty(
        default='Enter bone name'
    )
    bpy.types.Scene.armature_name = bpy.props.StringProperty(
        default='Armature'
    )

def unregister():
    for item in CLASSES:
        bpy.utils.unregister_class(item)
        
    del bpy.types.Object.bone_name
    del bpy.types.Scene.armature_name

if __name__ == '__main__':
    register()