import bpy

def resXChanged(self, context):
    camera = context.object
    context.scene.render.resolution_x = camera.resX
    
def resYChanged(self, context):
    camera = context.object
    context.scene.render.resolution_y = camera.resY

bpy.types.Object.resX = bpy.props.IntProperty(name="Resolution X", default=bpy.data.scenes[0].render.resolution_x, update=resXChanged)
bpy.types.Object.resY = bpy.props.IntProperty(name="Resolution Y", default=bpy.data.scenes[0].render.resolution_y, update=resYChanged)
bpy.types.Object.active = bpy.props.BoolProperty(name="Render Cam", default=False)



class CameraSettings(bpy.types.Panel):
    """Creates Custom Settings for Cameras"""
    bl_category = "Cameras"
    bl_label = "Camera Custom Settings"
    bl_idname = "OBJECT_PT_camera_settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    
    @classmethod
    def poll(cls, context):
        return context.camera
            
    def draw(self, context):
        camera = context.object
        layout = self.layout
        col = layout.column(align=True)
        col.prop(camera, "resX", text="Resolution X")
        col.prop(camera, "resY", text="Resolution Y")
        col.prop(camera, "active", text="Render Cam")
    
    
    
class CameraLister(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_category = "Cameras"
    bl_label = "Cameras"
    bl_idname = "CAMERA_PT_camera_lister"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
                
    def draw(self, context):
        cams = bpy.data.objects

        layout = self.layout
        
        for cam in cams:
            if cam.users==0 or cam.type != 'CAMERA':
                break
                
            box = layout.box()
            row = box.row()
            
            op = row.operator('camera.camera_properties',  text="", icon="RESTRICT_SELECT_OFF")
            op.camera_name = cam.name
            op.operation = 'select'
            
            op = row.operator('camera.camera_properties',  text="", icon="RESTRICT_VIEW_OFF")
            op.camera_name=cam.name
            op.operation = 'view'
            
            op = row.operator('camera.camera_properties',  text="", icon="SETTINGS")
            op.camera_name = cam.name
            op.operation = 'settings'
            
            row.prop(cam, "active", text="")
            
            row.prop(cam, "name", text="")
        
        row = layout.row()
        op = row.operator('camera.camera_properties', text="Render")
        op.camera_name = cam.name
        op.operation = 'render'
        
                                            
                                            
class CameraProperties(bpy.types.Operator):
    """Managing Camera Properties via Cameras Section in Output"""
    bl_idname = "camera.camera_properties"
    bl_label = "Camera Managing"
    
    
    camera_name = bpy.props.StringProperty(name="cam name")
    operation = bpy.props.StringProperty(name="operation")
    
    
    def view_from(self, context, camera):
        context.scene.render.resolution_x = camera.resX
        context.scene.render.resolution_y = camera.resY
        bpy.context.scene.objects.active = camera
        bpy.ops.view3d.object_as_camera()
        
    def select_camera(self, context, camera):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = camera
        camera.select = True        
    
    def execute(self, context):
        operation = self.operation
        
        if self.camera_name is not "cam name":
            camera = bpy.data.objects[self.camera_name]
            bpy.context.scene.objects.active = camera
        
        if operation == "select":
            self.select_camera(context, camera)
            
        if operation == "view":
            self.view_from(context, camera)
            
        if operation == "settings":
            bpy.ops.wm.call_menu(name='OBJECT_MT_camera_more_menu')
            
        if operation == "render":
            path = bpy.context.scene.render.filepath
            format = bpy.context.scene.render.image_settings.file_format.lower()
            cams = bpy.data.objects
            
            for cam in cams:
                if cam.users>0 and cam.type == 'CAMERA':
                    if cam.active:
                        output = path+"\\"+cam.name+"."+format
                        bpy.context.scene.render.filepath = output
                        self.view_from(context, cam)
                        bpy.ops.render.render(write_still=True)
                        print(output)
                        print(cam.name+" rendered")
            
            bpy.context.scene.render.filepath = path

        return {'FINISHED'}



class CameraMoreProperties(bpy.types.Menu):
    bl_label = "Custom Menu"
    bl_idname = "OBJECT_MT_camera_more_menu"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.object, "resX", text="Resolution X")
        row.prop(context.object, "resY", text="Resolution Y")


def draw_item(self, context):
    layout = self.layout
    layout.menu(CameraMoreProperties.bl_idname)
    
        
def register():
    bpy.utils.register_class(CameraLister)
    bpy.utils.register_class(CameraSettings)
    bpy.utils.register_class(CameraProperties)
    bpy.utils.register_class(CameraMoreProperties)
    bpy.types.INFO_HT_header.append(draw_item)


def unregister():
    bpy.utils.unregister_class(CameraLister)
    bpy.utils.unregister_class(CameraSettings)    
    bpy.utils.unregister_class(CameraProperties)
    bpy.utils.unregister_class(CameraMoreProperties)
    bpy.types.INFO_HT_header.remove(draw_item)


if __name__ == "__main__":
    register()    