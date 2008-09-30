import pygtk
pygtk.require('2.0')
import gtk

class GUI(object):
    def __init__(self, app):
        self.app = app

        self.surface = None

        self.main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.main_window.connect('delete_event', self.delete_event)
        self.main_window.connect('destroy', self.destroy)
        self.main_window.set_default_size(640, 480)
        self.main_window.set_title(u'Chavier')

        vbox = gtk.VBox()
        self.main_window.add(vbox)
        vbox.show()

        menubar, toolbar = self._create_ui_manager()

        vbox.pack_start(menubar, False, False)
        menubar.show()

        vbox.pack_start(toolbar, False, False)
        toolbar.show()

        hpaned = gtk.HPaned()
        vbox.pack_start(hpaned, True, True)
        hpaned.show()

        vpaned = gtk.VPaned()
        hpaned.add1(vpaned)
        vpaned.show()

        block1 = self._create_sidebar_block(u'Data sets',
                                            self._datasets_notebook_creator)
        self._create_dataset("Dataset 1")
        block1.set_size_request(-1, 200)

        vpaned.add1(block1)
        block1.show()

        block2 = self._create_sidebar_block(u'Options',
                                            self._options_treeview_creator)
        vpaned.add2(block2)
        block2.show()

        self.drawing_area = gtk.DrawingArea()
        self.drawing_area.connect('expose_event',
                                  self.drawing_area_expose_event)
        self.drawing_area.connect('size_allocate',
                                  self.drawing_area_size_allocate_event)
        hpaned.add2(self.drawing_area)
        self.drawing_area.show()

        self.main_window.show()


    # Internal methods
    def _create_ui_manager(self):
        self.uimanager = gtk.UIManager()
        accel_group = self.uimanager.get_accel_group()
        self.main_window.add_accel_group(accel_group)

        action_group = gtk.ActionGroup('default')
        action_group.add_actions([
                ('file', None, '_File', None, 'File', None),
                ('quit', gtk.STOCK_QUIT, None, None, 'Quit the program',
                 self.quit),

                ('edit', None, '_Edit', None, 'Edit', None),
                ('add_dataset', gtk.STOCK_ADD, '_Add dataset',
                 '<ctrl><alt>plus', 'Add another dataset', self.add_dataset),
                ('remove_dataset', gtk.STOCK_REMOVE, '_Remove dataset',
                 '<ctrl><alt>minus', 'Remove the current dataset',
                 self.remove_dataset),
                ('edit_dataset', gtk.STOCK_EDIT, '_Edit dataset name',
                 '<ctrl><alt>e', 'Edit the name of the current dataset',
                 self.edit_dataset),
                ('add_point', gtk.STOCK_ADD, 'Add _point', '<ctrl>plus',
                 'Add another point to the current dataset', self.add_point),
                ('remove_point', gtk.STOCK_REMOVE, 'Remove p_oint',
                 '<ctrl>minus',
                 'Remove the current point of the current dataset',
                 self.remove_point),
                ('edit_point', gtk.STOCK_EDIT, 'Edit po_int', '<ctrl>e',
                 'Edit the current point of the current dataset',
                 self.edit_point),
                ('edit_option', gtk.STOCK_EDIT, 'Edit op_tion', None,
                 'Edit the current option',
                 self.edit_option),

                ('view', None, '_View', None, 'View', None),
                ('refresh', gtk.STOCK_REFRESH, None, '<ctrl>r',
                 'Update the chart', self.refresh),
                ])
        action_group.add_radio_actions([
                ('verticalbar', None, '_Vertical bars', None,
                 'Use vertical bars chart', self.app.VERTICAL_BAR_TYPE),
                ('horizontalbar', None, '_Horizontal bars', None,
                 'Use horizontal bars chart', self.app.HORIZONTAL_BAR_TYPE),
                ('line', None, '_Line', None,
                 'Use lines chart', self.app.LINE_TYPE),
                ('pie', None, '_Pie', None,
                 'Use pie chart', self.app.PIE_TYPE),
                ('scatter', None, '_Scatter', None,
                 'Use scatter chart', self.app.SCATTER_TYPE),
                ], self.app.VERTICAL_BAR_TYPE, self.on_chart_type_change)
        self.uimanager.insert_action_group(action_group, -1)

        ui = """<ui>
  <menubar name="MenuBar">
    <menu action="file">
      <menuitem action="quit"/>
    </menu>
    <menu action="edit">
      <menuitem action="add_dataset"/>
      <menuitem action="remove_dataset"/>
      <menuitem action="edit_dataset"/>
      <separator />
      <menuitem action="add_point"/>
      <menuitem action="remove_point"/>
      <menuitem action="edit_point"/>
      <separator />
      <menuitem action="edit_option"/>
    </menu>
    <menu action="view">
      <menuitem action="refresh"/>
      <separator />
      <menuitem action="verticalbar"/>
      <menuitem action="horizontalbar"/>
      <menuitem action="line"/>
      <menuitem action="pie"/>
      <menuitem action="scatter"/>
    </menu>
  </menubar>
  <toolbar name="ToolBar">
    <toolitem action="quit"/>
    <separator />
    <toolitem action="add_dataset"/>
    <toolitem action="remove_dataset"/>
    <separator />
    <toolitem action="add_point"/>
    <toolitem action="remove_point"/>
    <separator />
    <toolitem action="refresh"/>
  </toolbar>
</ui>
"""
        self.uimanager.add_ui_from_string(ui)
        self.uimanager.ensure_update()
        menubar = self.uimanager.get_widget('/MenuBar')
        toolbar = self.uimanager.get_widget('/ToolBar')

        return menubar, toolbar

    def _create_sidebar_block(self, title, child_widget_creator):
        box = gtk.VBox(spacing=6)
        box.set_border_width(6)
        label = gtk.Label()
        label.set_markup(u'<span size="large" weight="bold">%s</span>' % title)
        label.set_alignment(0.0, 0.5)
        box.pack_start(label, False, False)
        label.show()

        child_widget = child_widget_creator()
        box.pack_start(child_widget, True, True)
        child_widget.show()

        return box

    def _datasets_notebook_creator(self):
        self.datasets_notebook = gtk.Notebook()
        self.datasets_notebook.set_scrollable(True)
        return self.datasets_notebook

    def _dataset_treeview_creator(self):
        store = gtk.ListStore(float, float)
        treeview = gtk.TreeView(store)

        column1 = gtk.TreeViewColumn('x', gtk.CellRendererText(), text=0)
        treeview.append_column(column1)

        column2 = gtk.TreeViewColumn('y', gtk.CellRendererText(), text=1)
        treeview.append_column(column2)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(treeview)
        treeview.show()

        return scrolled_window

    def _options_treeview_creator(self):
        self.options_store = gtk.TreeStore(str, str, object)
        options = self.app.get_default_options()
        self._fill_options_store(options, None, self.app.OPTIONS_TYPES)

        self.options_treeview = gtk.TreeView(self.options_store)

        column1 = gtk.TreeViewColumn('Name', gtk.CellRendererText(), text=0)
        self.options_treeview.append_column(column1)

        column2 = gtk.TreeViewColumn('Value', gtk.CellRendererText(), text=1)
        self.options_treeview.append_column(column2)

        self.options_treeview.expand_all()

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(self.options_treeview)
        self.options_treeview.show()

        return scrolled_window

    def _fill_options_store(self, options, parent_node, types):
        for name, value in options.items():
            value_type = types[name]
            if isinstance(value, dict):
                current_parent = self.options_store.append(parent_node, (name, None, None))
                self._fill_options_store(value, current_parent, value_type)

            else:
                print value_type
                if value is not None:
                    value = str(value)
                self.options_store.append(parent_node, (name, value, value_type))

    def _get_current_dataset_tab(self):
        current_tab = self.datasets_notebook.get_current_page()
        if current_tab != -1:
            return self.datasets_notebook.get_nth_page(current_tab)

    def _create_dataset(self, name):
        scrolled_window = self._dataset_treeview_creator()
        scrolled_window.show()
        label = gtk.Label(name)
        self.datasets_notebook.append_page(scrolled_window, label)

    def _get_datasets(self):
        datasets = []
        n_pages = self.datasets_notebook.get_n_pages()
        for i in range(n_pages):
            tab = self.datasets_notebook.get_nth_page(i)
            label = self.datasets_notebook.get_tab_label(tab)
            name = label.get_label()
            treeview = tab.get_children()[0]
            model = treeview.get_model()
            points = [(x, y) for x, y in model]
            if len(points) > 0:
                datasets.append((name, points))
        return datasets

    def _get_chart_type(self):
        action_group = self.uimanager.get_action_groups()[0]
        action = action_group.get_action('verticalbar')
        return action.get_current_value()

    def _get_options(self, iter):
        options = {}
        first_child = self.options_store.iter_children(iter)
        if first_child is not None:
            name = self.options_store.get_value(iter, 0)
            options[name] = self._get_options(first_child)

        iter = self.options_store.iter_next(iter)
        while iter is not None:
            name = self.options_store.get_value(iter, 0)
            options[name] = self._get_options(iter)
            iter = self.options_store.iter_next(iter)

        return options

    # Event and signal handlers
    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def drawing_area_expose_event(self, widget, event, data=None):
        if self.surface is None:
            return

        cr = widget.window.cairo_create()
        cr.rectangle(event.area.x, event.area.y,
                     event.area.width, event.area.height)
        cr.clip()
        cr.set_source_surface(self.surface, 0, 0)
        cr.paint()

    def drawing_area_size_allocate_event(self, widget, event, data=None):
        if self.surface is not None:
            self.refresh()

    def on_chart_type_change(self, action, current, data=None):
        if self.surface is not None:
            self.refresh()

    # Action handlers
    def quit(self, action):
        self.main_window.destroy()

    def add_dataset(self, action):
        n_pages = self.datasets_notebook.get_n_pages()
        suggested_name = u'Dataset %d' % (n_pages + 1)
        dialog = TextInputDialog(self.main_window, suggested_name)
        response = dialog.run()
        if response == gtk.RESPONSE_ACCEPT:
            name = dialog.get_name()
            self._create_dataset(name)
            self.datasets_notebook.set_current_page(n_pages)
        dialog.destroy()

    def remove_dataset(self, action):
        current_tab = self.datasets_notebook.get_current_page()
        assert current_tab != -1

        self.datasets_notebook.remove_page(current_tab)

    def edit_dataset(self, action):
        tab = self._get_current_dataset_tab()
        assert tab is not None

        label = self.datasets_notebook.get_tab_label(tab)
        name = label.get_label()
        dialog = TextInputDialog(self.main_window, name)
        response = dialog.run()
        if response == gtk.RESPONSE_ACCEPT:
            name = dialog.get_name()
            label.set_label(name)
        dialog.destroy()

    def add_point(self, action):
        tab = self._get_current_dataset_tab()
        assert tab is not None

        treeview = tab.get_children()[0]
        model = treeview.get_model()

        dialog = PointDialog(self.main_window, len(model) * 1.0, 0.0)
        response = dialog.run()
        if response == gtk.RESPONSE_ACCEPT:
            x, y = dialog.get_point()
            model.append((x, y))
            self.refresh()
        dialog.destroy()

    def remove_point(self, action):
        tab = self._get_current_dataset_tab()
        assert tab is not None

        treeview = tab.get_children()[0]
        selection = treeview.get_selection()
        model, selected = selection.get_selected()
        if selected is None:
            warning(self.main_window, "You must select the point to remove")
            return

        model.remove(selected)
        self.refresh()

    def edit_point(self, action):
        tab = self._get_current_dataset_tab()
        assert tab is not None

        treeview = tab.get_children()[0]
        selection = treeview.get_selection()
        model, selected = selection.get_selected()
        if selected is None:
            warning(self.main_window, "You must select the point to edit")
            return

        x, y = model.get(selected, 0, 1)

        dialog = PointDialog(self.main_window, x, y)
        response = dialog.run()
        if response == gtk.RESPONSE_ACCEPT:
            x, y = dialog.get_point()
            model.set(selected, 0, x, 1, y)
            self.refresh()
        dialog.destroy()

    def edit_option(self, action):
        selection = self.options_treeview.get_selection()
        model, selected = selection.get_selected()
        if selected is None:
            warning(self.main_window, "You must select the option to edit")
            return

        name, value, value_type = model.get(selected, 0, 1, 2)
        parents = []
        parent = model.iter_parent(selected)
        while parent is not None:
            parents.append(model.get_value(parent, 0))
            parent = model.iter_parent(parent)
        parents.reverse()
        parents.append(name)
        label = u'.'.join(parents)

        dialog = OptionDialog(self.main_window, label, value, value_type)
        response = dialog.run()
        if response == gtk.RESPONSE_ACCEPT:
            new_value = dialog.get_value()
            model.set_value(selected, 1, new_value)
            self.refresh()
        dialog.destroy()

    def refresh(self, action=None):
        datasets = self._get_datasets()
        if datasets:
            root = self.options_store.get_iter_first()
            options = self._get_options(root)

            chart_type = self._get_chart_type()
            alloc = self.drawing_area.get_allocation()
            self.surface = self.app.get_chart(datasets, None, chart_type,
                                              alloc.width, alloc.height)
            self.drawing_area.queue_draw()
        else:
            self.surface = None

    # Public API
    def run(self):
        gtk.main()

class TextInputDialog(gtk.Dialog):

    def __init__(self, toplevel_window, suggested_name):
        flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                   gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
        super(TextInputDialog, self).__init__(u'Enter a name for the dataset',
                                              toplevel_window, flags, buttons)
        self.set_default_size(300, -1)

        hbox = gtk.HBox(spacing=6)
        hbox.set_border_width(12)

        label = gtk.Label(u'Name')
        hbox.pack_start(label, False, False)

        self.entry = gtk.Entry()
        self.entry.set_text(suggested_name)
        self.entry.set_activates_default(True)
        hbox.pack_start(self.entry, True, True)

        self.vbox.pack_start(hbox, False, False)

        self.vbox.show_all()

        self.set_default_response(gtk.RESPONSE_ACCEPT)

    def get_name(self):
        return self.entry.get_text()


class PointDialog(gtk.Dialog):
    def __init__(self, toplevel_window, initial_x, initial_y):
        flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                   gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
        super(PointDialog, self).__init__(u'Enter the point values',
                                          toplevel_window, flags, buttons)

        initials = {u'x': str(initial_x), u'y': str(initial_y)}
        self.entries = {}
        for coordinate in (u'x', u'y'):
            hbox = gtk.HBox(spacing=6)
            hbox.set_border_width(12)

            label = gtk.Label(coordinate)
            hbox.pack_start(label, False, False)

            entry = gtk.Entry()
            entry.set_activates_default(True)
            entry.set_text(initials[coordinate])
            hbox.pack_start(entry, True, True)

            self.entries[coordinate] = entry

            self.vbox.pack_start(hbox, False, False)

        self.vbox.show_all()

        self.set_default_response(gtk.RESPONSE_ACCEPT)

    def get_point(self):
        return (float(self.entries[u'x'].get_text()),
                float(self.entries[u'y'].get_text()))


class OptionDialog(gtk.Dialog):
    def __init__(self, toplevel_window, label, value, value_type):
        flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                   gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
        super(OptionDialog, self).__init__(u'Enter the option value',
                                           toplevel_window, flags, buttons)


        hbox = gtk.HBox(spacing=6)
        hbox.set_border_width(12)

        label = gtk.Label(label)
        hbox.pack_start(label, False, False)

        self.entry = gtk.Entry()
        self.entry.set_text(value)
        self.entry.set_activates_default(True)
        hbox.pack_start(self.entry, True, True)

        self.vbox.pack_start(hbox, False, False)

        self.vbox.show_all()

        self.set_default_response(gtk.RESPONSE_ACCEPT)

    def get_value(self):
        return self.entry.get_text()


def warning(window, msg):
    dialog = gtk.MessageDialog(window,
                               gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                               gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, msg)
    dialog.run()
    dialog.destroy()