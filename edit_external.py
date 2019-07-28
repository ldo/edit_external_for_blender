#+
# This script lets the user edit the contents of a Blender text object
# using Emacs, invoked via the emacsclient command. Note that Blender
# execution is blocked while waiting for the edit to complete.
#
# Copyright 2012, 2019 by Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
# Licensed under CC-BY-SA <http://creativecommons.org/licenses/by-sa/4.0/>.
#-

import os
import subprocess
import tempfile
import bpy

bl_info = \
    {
        "name" : "Edit in Emacs",
        "author" : "Lawrence D'Oliveiro <ldo@geek-central.gen.nz>",
        "version" : (1, 0, 3),
        "blender" : (2, 80, 0),
        "location" : "Text Editor > Text > Edit in Emacs",
        "description" : "Edit the current text externally in Emacs (ALT+E)",
        "category" : "Text Editor",
    }

class EditExternal(bpy.types.Operator) :
    bl_idname = "text.edit_external"
    bl_label = "Edit External"
    bl_context = "text_edit"

    def invoke(self, context, event) :
        if context.edit_text != None :
            the_text = context.edit_text.as_string()
            tempfile_fd, tempfile_name = tempfile.mkstemp(text = True)
            the_file = os.fdopen(tempfile_fd, "rb+")
            the_file.seek(0, os.SEEK_SET)
            the_file.truncate()
            the_file.write(the_text.encode())
            the_file.flush()
            completed = subprocess.run(args = ("emacsclient", tempfile_name))
            if completed.returncode == 0 :
                the_file.seek(0, os.SEEK_SET)
                context.edit_text.clear()
                context.edit_text.write(the_file.read().decode())
            #end if
            the_file.close()
            #os.close(tempfile_fd) # done by closing file object
            os.unlink(tempfile_name)
            return_status = {"FINISHED"}
        else :
            self.report({"ERROR"}, "select/create a text block first")
            return_status = {"CANCELLED"}
        #end if
        return return_status
    #end invoke

#end EditExternal

def add_to_menu(self, context) :
    self.layout.operator(EditExternal.bl_idname, icon = "TEXT")
#end add_to_menu

def register() :
    bpy.utils.register_class(EditExternal)
    the_keymap = bpy.context.window_manager.keyconfigs["blender"].keymaps["Text"]
    args = [EditExternal.bl_idname]
    kwargs = {"type" : "E", "value" : "PRESS", "alt" : True, "head" : True}
    the_keymap.keymap_items.new(*args, **kwargs)
    bpy.types.TEXT_MT_text.append(add_to_menu)
#end register

def unregister() :
    bpy.types.TEXT_MT_text.remove(add_to_menu)
    the_keymap = bpy.context.window_manager.keyconfigs["blender"].keymaps["Text"]
    for the_key in the_keymap.keymap_items :
        if the_key.idname == EditExternal.bl_idname :
            the_keymap.keymap_items.remove(the_key)
            break
        #end if
    #end for
    bpy.utils.unregister_class(EditExternal)
#end unregister

if __name__ == "__main__" :
    register()
#end if
