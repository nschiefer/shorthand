import pygtk
pygtk.require('2.0')
import gtk

class ListBox:
    """
    Encapsulates the logic related to the manipulation of a list box

    Implemented as a treeview
    """

    def __init__(self, gui, data=[], columns=[]):
        self.liststore = gtk.ListStore(str, str)
        self.treeview = gtk.TreeView(self.liststore)
        self.gui = gui
        for datum in data:
            self.liststore.append(datum)
        for index, column in enumerate(columns):
            c = gtk.TreeViewColumn(column)
            cell = gtk.CellRendererText()
            c.pack_start(cell, True)
            c.add_attribute(cell, 'text', index)
            c.set_property('resizable', True)
            self.treeview.append_column(c)
        self.treeview.connect('cursor-changed', self.cursor_changed)
        self._selection = self.treeview.get_selection()

    def append(self, datum):
        """Add a new row the listbox"""
        self.liststore.append(datum)

    def set(self, data):
        """Set the rows of the listbox to the new data values"""
        self.liststore.clear()
        for datum in data:
            self.liststore.append(datum)

    def cursor_changed(self, widget, data=None):
        """Handle cursor-changed event for the Listbox's Treeview"""
        # [0][0] selects the actual first row, see pyGTK
        self.gui.update_selection(*reversed(self.get_selected()))

    def set_selected(self, text=None, num=None):
        """Set the cursor the row with the given text or index"""
        if text:
            for i, data in enumerate(map(list, list(self.liststore))):
                if data[0] == text:
                    self.treeview.set_cursor(i)
        elif num != None:
            self.treeview.set_cursor(num)

    def get_selected(self):
        """Return the currently selected row in the format (index, title)"""
        i = self._selection.get_selected_rows()[1][0][0]
        return i, self.liststore[i][0]

    def is_selected(self):
        """Return True if the cursor is currently set to a row"""
        return bool(self.treeview.get_cursor()[0])

    def clear_selection(self):
        """Clear the cursor; no rows are selected"""
        self._selection.unselect_all()
