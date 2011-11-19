import pygtk
pygtk.require('2.0')
import gtk
import collections # for defaultdict
import listbox

class Base:
    """Base GUI class"""

    def __init__(self, database):
        self.database = database
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Shorthand")

        # destroy events
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)

        self.vbox = gtk.VBox(homogeneous=False)
        self.window.add(self.vbox)

        # create and add the entry/search bar
        self.entry_bar = gtk.HBox()
        self.entry = gtk.Entry()
        self.entry_bar.pack_start(self.entry, True, True, 0)
        self.vbox.pack_start(self.entry_bar, False, True, 0)
        
        # connect the relevant entry bar events
        self.entry.connect("changed", self.entry_changed)
        self.entry.connect("key-press-event", self.entry_keypress)

        # enable global keyboard shortcuts
        # TODO 18/11/2011 Add more shortucts
        shortcuts = [(gtk.gdk.keyval_from_name('l'), gtk.gdk.CONTROL_MASK, self.entry_mode),
                     (gtk.gdk.keyval_from_name('k'), gtk.gdk.CONTROL_MASK, self.move_selection_up),
                     (gtk.gdk.keyval_from_name('j'), gtk.gdk.CONTROL_MASK, self.move_selection_down),
                     # 65288 is the code for backspace, don't know official key name
                     (65288, gtk.gdk.CONTROL_MASK, self.delete_note)]

        self.accel = self.create_keyboard_shortcuts(shortcuts)
        self.window.add_accel_group(self.accel)

        # create pane for listbox and textarea
        self.pane = gtk.VPaned()

        # create listbox to display notes
        self.listbox = listbox.ListBox(self, self.database.all(), ['Title', 'Date modified'])

        # connect keypress event for keyboard shortcuts
        self.listbox.treeview.connect("key-press-event", self.listbox_keypress)

        # embed listbox in scrolled window
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.listbox.treeview)
        sw.set_size_request(-1, 200)
        self.pane.pack1(sw)

        # create textarea to display note content
        self.textarea = gtk.TextView()
        self.textarea.set_property('wrap-mode', gtk.WRAP_WORD)

        # embed textarea in scrolled window
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.textarea)
        self.pane.pack2(sw)

        # add pane
        self.vbox.pack_start(self.pane, True, True, 0)

        # new buffer generating function
        def create_buffer():
            b = gtk.TextBuffer()
            b.connect('changed', self.update_note)
            return b
        # create defaultdict of buffers
        self.buffers = collections.defaultdict(create_buffer)

        # resize and show window
        self.window.resize(350, 500)
        self.window.show_all()

    # the following functions are event handlers and related functions

    def entry_changed(self, widget, data=None):
        """Handle changed event for self.entry"""
        self.textarea.hide()
        results = self.database.search(widget.get_text())
        self.listbox.set(results)

    def update_selection(self, selected_title, number):
        """Update the currenlty selected note and change the textarea accordingly"""
        self.textarea.show()
        retrieved = self.database[selected_title]
        buf = self.buffers[selected_title]
        self.textarea.set_buffer(buf)
        if not buf.get_text(*buf.get_bounds()) == retrieved:
            buf.set_text(retrieved)
            self.listbox.set_selected(num=number)

    def clear_note(self, widget, event):
        """Clear the textarea from view (hide it)"""
        self.textarea.hide()

    def entry_keypress(self, widget, event):
        """
        Handle the key-press-event for self.entry

        Used to manage keyboard shortcuts
        """
        if event.keyval == gtk.gdk.keyval_from_name("Return"): #65293: # code for "Enter"
            if len(self.listbox.liststore) > 0:
                self.listbox.set_selected(num=0)
                self.edit_note()
            else:
                self.create_note()
            return True
        elif event.keyval == 65364: # code for Down arrow
            self.listbox.set_selected(num=0)
            return False
        elif event.keyval == gtk.gdk.keyval_from_name("Escape"):
            self.clear_search()
            return False
        return False

    def listbox_keypress(self, widget, event):
        """
        Handle the key-press-event for self.listbox.treeview

        Used to manage keyboard shortcuts
        """
        if event.keyval == gtk.gdk.keyval_from_name("Return"):
            self.textarea.grab_focus()
        elif event.keyval == gtk.gdk.keyval_from_name("Delete") or event.keyval == 65288:
            self.listbox.clear_selection()

    def clear_search(self):
        """Clear the entry box"""
        self.entry.set_text("")

    def update_listbox(self):
        """Update the listbox rows based on the current search text"""
        self.listbox.set(self.database.search(self.entry.get_text()))

    def create_note(self):
        """Create a new note; used when no note is found and the user tries to edit it"""
        title = self.entry.get_text()
        self.listbox.set_selected(text=title)
        self.database.add(title)
        self.textarea.show()
        self.textarea.set_buffer(self.buffers[title])
        self.textarea.grab_focus()

    def edit_note(self):
        """Prepare to edit an existing note"""
        title = self.listbox.get_selected()[1]
        self.textarea.show()
        self.textarea.set_buffer(self.buffers[title])
        self.textarea.grab_focus()


    def get_current_key(self):
        """
        Return the "current note of interest"

        Depending on context, it may be two things:
        1) the title of the selected note, if a note is selected in the listbox
        2) the content of the entry bar, if no note is selected
        """
        if self.listbox.is_selected():
            return self.listbox.get_selected()[1]
        else:
            return self.entry.get_text()

    def update_note(self, widget,data=None):
        """Update the changed note in the database"""
        text = widget.get_text(*widget.get_bounds())
        self.database[self.get_current_key()] = text

    def entry_mode(self, accel_group, acceleratable, keyval, modifier):
        """Prepare interface for the user to use the entry box, grabbing focus and selecting existing text"""
        self.entry.grab_focus()
        self.entry.select_region(0, -1)

    def move_selection_up(self, accel_group, acceleratable, keyyal, modifier):
        """Move cursor to the previous item in the listbox, or to the entry box if already at the top"""
        self.listbox.treeview.grab_focus()
        pos = self.listbox.get_selected()[0]
        if pos > 0:
            self.listbox.set_selected(num=pos - 1)
        else:
            self.entry_mode(None, None, None, None)

    def move_selection_down(self, accel_group, acceleratable, keyval, modifier):
        """Move cursor to the next item in the listbox, if possible"""
        if self.entry.has_focus():
            self.listbox.set_selected(num=0)
            self.listbox.treeview.grab_focus()
            return
        self.listbox.treeview.grab_focus()
        pos = self.listbox.get_selected()[0]
        if pos < len(self.listbox.liststore) - 1:
            self.listbox.set_selected(num=pos + 1)

    def delete_note(self, *args):
        """Delete the selected note from the database (based on get_current_note)"""
        del self.database[self.get_current_key()]
        self.update_listbox()

    def create_keyboard_shortcuts(self, shortcuts):
        """Create keyboard shortucts from a list of (keyval, modifier_mask, callback) tuples"""
        a = gtk.AccelGroup()
        for keyval, mask, callback in shortcuts:
            a.connect_group(keyval, mask, gtk.ACCEL_VISIBLE, callback)
        return a

    def delete_event(self, widget, event, data=None):
        """Delete event for the main window"""
        return False

    def destroy(self, widget, data=None):
        """Quit the application"""
        gtk.main_quit()

    def main(self):
        """Main loop"""
        gtk.main()
