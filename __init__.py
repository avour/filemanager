
from filechooserthumbview import FileChooserThumbView

from kivy.uix.modalview import ModalView
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.gridlayout import GridLayout

from kivy.properties import ObjectProperty, OptionProperty
from kivy.factory import Factory
from kivy.core.window import Window
from kivy.utils import platform
from kivy.lang import Builder

import os
from functools import partial

from kivystudio.behaviors import HighlightBehavior
from kivystudio.widgets.splitter import StudioSplitter

file_path = os.path.dirname(__file__)

from kivy.resources import resource_add_path
resource_add_path(os.path.join(file_path, 'images'))
resource_add_path(os.path.join(file_path, 'file_formats'))

Builder.load_file(os.path.join(file_path,'main.kv'))


filepath_for_cool_icons ='/usr/share/icons/Vibrancy-Kali/apps/64'


class SideSelector_(HighlightBehavior, FocusBehavior, GridLayout):
    pass


class FileManager(ModalView):

    _dir_selector = ObjectProperty(None)
    '''internal widget used to show and display the current dir path'''

    _file_chooser = ObjectProperty(None)
    ''' the internal file chooser a subclass of FileChooserController'''

    mode = OptionProperty('open_file', options=['open_file', 'save_file', 'choose_dir'])

    __events__ = ('on_finished', )

    def __init__(self, **k):
        super(FileManager, self).__init__(**k)
        self.new_bub = Factory.NewFolderBub_()

        self.new_bub.ids.input.bind(on_text_validate=self.create_new_folder)

        self._file_chooser.path = self.get_defualt_user_dir()

        # self.mode = 'save_file'

    def get_defualt_user_dir(self):
        username = os.getlogin()
        if platform == 'linux':
            if username != 'root':
                defualt_dir = r'/home/%s'%username
            else:
                defualt_dir = r'/root'

        elif platform == 'Windows':
            defualt_dir = r'C:\\Users\\%s'%username

        return defualt_dir

    def set_side_panel_dir(self, name):
        user_dir = self.get_defualt_user_dir()

        self._file_chooser.path = os.path.join(user_dir, name)

    def on_path(self, path):
        path_list = path.split('/')

        self._dir_selector.clear_widgets()
        for i in path_list:
            if i:
                btn = Factory.DirButton_(size_hint=(None,1), text=str(i))

                btn.bind(on_release=partial(self._go_dir_with_btn, btn))

                if btn.width <= btn.texture_size[0]:
                    btn.width = btn.texture_size[0]+10

                self._dir_selector.add_widget(btn)
        else:
            if i:
                self.ids.dir_scroll.scroll_to(btn)

    def _go_dir_with_btn(self, btn, *args):
        path_list = []
        children = self._dir_selector.children[:]
        children.reverse()
        for child in children:
            path_list.append(child.text)
            if child == btn:
                break

        self._file_chooser.path = '/'+ '/'.join(path_list)

    def on_open(self):
        Window.bind(on_key_down=self.handle_key)

    def on_dismiss(self):
        Window.unbind(on_key_down=self.handle_key)

        # remove bubble if open
        if self.new_bub in Window.children:
            Window.remove_widget(self.new_bub)

    def handle_key(self, keyboard, key, codepoint, text, modifier, *args):
        if key == 8:    # if user press the backspace reverse dir
            self.reverse_dir()

        elif key == 27:
            self.handle_escape()
        
        elif key == 13:     # enter
            pass

    def reverse_dir(self):
        previous_path = os.path.dirname(self._file_chooser.path)

        if os.path.exists(previous_path):
            self._file_chooser.path = previous_path

    def on_mode(self, *args):
        if self.mode == 'save_file':
            self.save_widget = Factory.SaveWidget_()
            self.save_widget.ids.input.bind(on_text_validate=self.handle_saving)

            self.ids.saving_container.add_widget(self.save_widget)

    def handle_escape(self):
        if self.new_bub in Window.children:
            Window.remove_widget(self.new_bub)
        else:
            self.dismiss()
        

    def handle_bubble(self, btn):
        if self.new_bub in Window.children:
            Window.remove_widget(self.new_bub)
        else:
            self.new_bub.pos = (btn.x - (self.new_bub.width-btn.width), btn.y - self.new_bub.height)
            Window.add_widget(self.new_bub)

    def create_new_folder(self, textinput):
        path = os.path.join(self._file_chooser.path, textinput.text)
        if not os.path.exists(path):
            print('making folder ', path)
            try:
                os.mkdir(path)

                # a simple trick to force the file chooser to recompute the files
                former_path = self._file_chooser.path
                self._file_chooser.path = 'eeraef7h98fwb38rh3f8h23yr8i'  # change to an invaid path
                self._file_chooser.path = former_path       # then change back
                Window.remove_widget(self.new_bub)

            except OSError:
                print('error making dir')
        else:
            print('already exists')

    def handle_saving(self, textinput):
        path = os.path.join(self._file_chooser.path, textinput.text)
        if not os.path.exists(path):
            pass
        else:
            print('error making dir')

    def file_selected(self, obj, path):
        if self.mode == 'open_file':
            self.dispatch('on_finished', path)
            self.dismiss()

    def on_finished(self, path):
        self.callback(path)

    def open_file(self, path='', callback=None):
        self.mode = 'open_file'
        self.callback = callback
        self.open()

    def save_file(self, path='', callback=None):
        self.mode = 'save_file'
        self.callback = callback
        self.open()
        
    def choose_dir(self, path='', callback=None):
        self.mode = 'choose_dir'
        self.callback = callback
        self.open()

filemanager = FileManager()


if __name__ == "__main__":
    from kivy.base import runTouchApp
    from kivy.uix.button import Button

    file_picker = FileManager()
    btn = Button(text='push me')
    btn.bind(on_release=lambda *args: file_picker.open())
    runTouchApp(btn)
