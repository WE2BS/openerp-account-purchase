# -*- encoding: utf-8 -*-
#
# Copyright (C) 2010-2011 Thibaut DIRLIK (Une idée derrière l'écran)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
This module provide a powerful functionality for OpenERP 6. You can now
automatically create menus with your some OpenERP objects in your modules.

This is usefull in many way, for example you want to create a model named
"Category" which represents a category and you want to create a menu
for each of theses category. Now it's possible in  few lines of code.

1. How does it work?
2. Example
3. Customization

1. How does it work ?

To automatically create/delete a menu with an OpenERP object, you have
to make this object inherit from the AttachMenu class. This means that
you class will inherit both osv.osv and AttachMenu.

After, on you have to configure the menu generation with class variables
that starts with _menu_ (see Customization for more information).

2. Example

class MyCategory(AttachMenu, osv.osv):

    def _get_parent_menu_id(self, cursor, user_id, object_data, context=None):

        # Return the id of the parent category menu.

        if not object_data['parent_id']:
            return 'afs_menu'

        parent = self.read(cursor, user_id, object_data['parent_id'][0])

        return parent['menu_id'][0]

    # Menu configuration
    _menu_name = 'name'
    _menu_parent = _get_parent_menu_id # Callable !

    _name = "my.category"
    _columns = {
        "name" : fields.char(_("Name"), size=120, required=True),
        "parent_id" : fields.many2one("afs.model.category", _("Parent")),
    }

3. Customization

You can define a lot of options in your class:

_menu_name = 'field_name
    The name of the field which will be used to get the menu name.

_menu_parent = 'id'
    The id or xmlid of the parent menu.

_menu_res_model : None
    The view to open, if None, options below will be ignored.
    Note: If the menu does not open a view, it won't be visible
    until a submenu that opens a view is available.

_menu_icon = 'STOCK_OPEN'
    Icon of the menu item.

_menu_view_type = 'form'
    If the menu must open a view, set the type of the view

_menu_view_mode = 'form,tree'
    The the type is form, set the mode available.

_menu_context = '{}'
    Context to pass to the view.

_menu_help = None
    Help text to show on the view.

_menu_domain : None,
    Domain.

_menu_target : 'current'
    Can be new or current.

_menu_groups : None
    List of groups allowed to show this menu: ['account.group_account_user', '...']

"""

from openerp.pooler import get_pool
from openerp.osv import fields

class Menu(object):

    """
    A simple class used to manipulate menus as object.
    """

    @classmethod
    def create(cls, cursor, user_id, name, parent=None, icon='STOCK_OPEN'):

        """
        Create a new menu and returns its ID.
        """

        pool = get_pool(cursor.dbname).get('ir.ui.menu')
        menu_id = pool.create(cursor, user_id, {
            'name' : name,
            'parent_id' : parent.id if parent else None, # parent must be a Menu object
            'icon' : icon,
        })

        return Menu(pool.browse(cursor, user_id, menu_id))

    @classmethod
    def get_from_id(cls, cursor, user_id, id):

        """
        Returns a Menu object obtained from a DB ID or an XMLID.
        """

        if isinstance(id, basestring):
            # Argument considered as an XMLID, we look into
            # ir.model.mata to get the DB ID associated to this xmlid.
            data_pool = get_pool(cursor.dbname).get('ir.model.data')
            data_id = data_pool.search(cursor, user_id, [('name', '=', id),])
            if not data_id:
                raise Exception(u'Menu with XMLID %s does not exist.' % id)
            data_id = data_id[0]
            menu_id = data_pool.read(cursor, user_id, data_id)['res_id']
        elif isinstance(id, (int, long)):
            # Argument is already the menu DB ID
            menu_id = id
        else:
            raise Exception(u'Invalid argument to get_from_id: %s (%s)' % (id, type(id)))

        return Menu(get_pool(cursor.dbname).get('ir.ui.menu').browse(
            cursor, user_id, menu_id
        ))

    def __init__(self, menu, action=None, values=None):

        """
        Simply store informations about the menu.
        """

        self.id = menu.id
        self.name = menu.name
        self.parent = Menu(menu.parent_id) if menu.parent_id.id else None
        self.icon = menu.icon

        if not action:
            self.action_model = None
            self.action_view_type = None
            self.action_view_mode = None

    def create_action(self, cursor, user_id, model, view_type, view_mode,
                      context, target, help, domain):

        """
        Create an action to associate to this menu. Works only if the
        model hasn't any action for now.
        """

        pool_action = get_pool(cursor.dbname).get('ir.actions.act_window')
        pool_values = get_pool(cursor.dbname).get('ir.values')

        action_id = pool_action.create(cursor, user_id, {
            'name' : self.name,
            'type' : 'ir.actions.act_window',
            'res_model' : model,
            'view_type' : view_type,
            'view_mode' : view_mode,
            'context' : context,
            'target' : target,
            'help' : help,
            'domain' : domain,
        })

        values_id = pool_values.create(cursor, user_id, {
            'name' : 'Menuitem',
            'key' : 'action',
            'key2' : 'tree_but_open',
            'model' : 'ir.ui.menu',
            'value' : 'ir.actions.act_window,%i' % action_id,
            'res_id' : self.id,
            'object' : True,
         })

        self.action_id = action_id
        self.action_model = model
        self.action_view_type = view_type
        self.action_view_mode = view_mode
        self.values_id = values_id

    def get_action(self, cursor, user_id):

        """
        Pull action's information from the DB. Return False if this menu
        has not any action associated to it.
        """

        pool_values = get_pool(cursor.dbname).get('ir.values')
        pool_action = get_pool(cursor.dbname).get('ir.actions.act_window')

        value_id = pool_values.search(cursor, user_id, [
            ('res_id', '=', self.id),
        ])

        if not value_id:
            return False

        value_id = value_id[0]
        value_data = pool_values.read(cursor, user_id, value_id)

        action_id = int(value_data['value'].split(',')[1])
        action_data = pool_action.read(cursor, user_id, action_id)

        self.value_id = value_id
        self.action_id = action_data['id']
        self.action_model = action_data['res_model']
        self.action_view_type = action_data['view_type']
        self.action_view_mode = action_data['view_mode']

        return True

    def update(self, cursor, user_id, name=None, icon=None, parent=None):

        """
        Update fields of a menu.
        """

        pool = get_pool(cursor.dbname).get('ir.ui.menu')

        data = dict()
        if name: self.name = data['name'] = name
        if icon: self.icon = data['icon'] = icon
        if parent:
            data['parent_id'] = parent.id
            self.parent = parent

        pool.write(cursor, user_id, self.id, data)

    def delete(self, cursor, user_id):

        """
        Removes the menu from the DB.
        """

        pool_menu = get_pool(cursor.dbname).get('ir.ui.menu')
        pool_values = get_pool(cursor.dbname).get('ir.values')
        pool_action = get_pool(cursor.dbname).get('ir.actions.act_window')

        if self.get_action(cursor, user_id):
            pool_values.unlink(cursor, user_id, self.value_id)
            pool_action.unlink(cursor, user_id, self.action_id)

        pool_menu.unlink(cursor, user_id, self.id)

class AttachMenu(object):

    def __new__(cls, *args, **kwargs):

        # A new column is automatically added if it does not exist:
        # menu_id, which correspond to the menu attached to this item.

        if 'menu_id' not in cls._columns:
            cls._columns['menu_id'] = fields.many2one('ir.ui.menu')

        defaults = {
            '_menu_icon' : 'STOCK_OPEN',
            '_menu_parent' : None,
            '_menu_name' : 'name',
            '_menu_view_type' : 'form',
            '_menu_view_mode' : 'form,tree',
            '_menu_res_model' : None,
            '_menu_context' : '{}',
            '_menu_help' : None,
            '_menu_domain' : None,
            '_menu_target' : 'current',
            '_menu_groups' : None,
        }

        for variable in defaults:
            if not hasattr(cls, variable):
                setattr(cls, variable, defaults[variable])

        return super(AttachMenu, cls).__new__(cls, *args, **kwargs)

    def get_config_values(self, cursor, user_id, object, context=None):

        # Returns a dictionary which contains all configuration values
        # calculated for this object (the _menu_ is truncated)

        config_variables = [var for var in dir(self) if var.startswith('_menu_')]
        config_values = dict()

        for config_name in config_variables:
            attr = getattr(self, config_name)
            name = config_name[6:]
            if callable(attr):
                config_values[name] = attr(cursor, user_id, object, context)
            else:
                config_values[name] = attr

        return config_values

    def create(self, cursor, user_id, object_data, context=None):

        #
        # Override the default create() function to automatically create
        # the menu once the object has been created. We must create the menu
        # before the object.
        #

        # We create a temporary menu.
        menu = Menu.create(cursor, user_id, 'temp_menu')
        
        object_data['menu_id'] = menu.id
        object_id = super(AttachMenu, self).create(cursor, user_id, object_data, context)
        object = self.browse(cursor, user_id, object_id, context=context)
        
        config = self.get_config_values(cursor, user_id, object, context)
        name = getattr(object, config['name'])

        if config['parent']:
            menu_parent = Menu.get_from_id(cursor, user_id, config['parent'])
        else:
            menu_parent = None
        
        menu.update(cursor, user_id, name=name, icon=config['icon'], parent=menu_parent)

        # We create an action associated to this menu if _menu_res_model
        # was specified. This would mean this menu must open something.
        if config['res_model']:
            menu.create_action(cursor, user_id,
                               config['res_model'],
                               config['view_type'],
                               config['view_mode'],
                               config['context'],
                               config['target'],
                               config['help'],
                               config['domain'])

        return object_id

    def unlink(self, cursor, user_id, ids, context=None):

        #
        # Override the default unlink() to remove menus corresponding to
        # objects we are deleting.
        #

        try:
            iter(ids)
        except TypeError:
            ids = [ids]

        objects = self.browse(cursor, user_id, ids, context=context)

        for object in objects:
            if not hasattr(object, 'menu_id') or not object.menu_id.id:
                # May not happen, but we check to avoid errors
                continue
            menu = Menu.get_from_id(cursor, user_id, object.menu_id.id)
            menu.delete(cursor, user_id)

        return super(AttachMenu, self).unlink(cursor, user_id, ids)

    def write(self, cursor, user_id, ids, values, context=None):

        #
        # We override the default write() method to rename the menu if the
        # name of the object changed, and change the menu parent if needed.
        #

        result = super(AttachMenu, self).write(cursor, user_id, ids, values, context)
        
        try:
            iter(ids)
        except TypeError:
            ids = [ids]

        objects = self.browse(cursor, user_id, ids, context=context)

        for object in objects:

            # Note: The config values returned are based on the new values
            # because we saved the object with super().
            config = self.get_config_values(cursor, user_id, object, context)
            name_field = config['name']
            
            menu = Menu.get_from_id(cursor, user_id, object.menu_id.id)
            to_update = {}

            if name_field in values:
                unicode_name = values[name_field].decode('utf-8')
                if (getattr(object, name_field) != unicode_name) and object.menu_id.id:
                    to_update['name'] = unicode_name
            
            if config['parent'] != menu.parent.id:
                to_update['parent'] = Menu.get_from_id(cursor, user_id, config['parent'])

            menu.update(cursor, user_id, **to_update)

        return result
