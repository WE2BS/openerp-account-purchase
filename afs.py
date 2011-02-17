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

from openerp.osv import osv, fields
from openerp.tools.translate import _

from . menu import AttachMenu

PAYMENTS_MODES = (
    ('cash', _('Cash')),
    ('bank', _('Bank')),
    ('account', _('Account')),
    ('ce', _('Instrument of trade')),
)

AMOUNT_TYPES = (
    ('ttc', _('Incl. Tax')),
    ('ht', _('Excl. Tax')),
    ('tva', _('VAT')),
)

POSITION = (
    ('d', _('Debit')),
    ('c', _('Credit')),
)

ACCOUNTS_DOMAIN = [('type', '!=', 'view')]
TAX_DOMAIN = [('type_tax_use', 'in', ('purchase', 'all'))]
JOURNALS_DOMAIN = [('code', 'in', ('VT', 'BQ', 'HA', 'OD'))]
JOURNALS = {
    'VT' : 'ventes',
    'HA' : 'achats',
    'BQ' : 'banque',
    'OD' : 'divers',
}

class Tax(osv.osv):

    """
    We just redefine the account.tax model to override name_get method wich returns
    by default the code instead of the name.
    """

    _name = 'account.tax'
    _inherit = 'account.tax'

    def name_get(self, cursor, user_id, ids, context=None):

        if not ids:
            return []

        return [(t['id'], t['name']) for t in self.read(cursor, user_id, ids, ['name'], context=context)]

class Model(AttachMenu, osv.osv):
    
    """
    Represents a model, like 'Elecricity Invoice'.
    """

    def _get_parent_menu_id(self, cursor, user_id, object, context=None):

        """
        The parent menu of a Model is the menu of its category.
        """

        return object.category_id.menu_id.id

    def _get_menu_context(self, cursor, user_id, object, context=None):

        """
        Returns the context used by the menu. This context will be used in the wizard.
        """

        return "{'category' : %d, 'model' : %d }" % (object.category_id.id, object.id)

    # Configure menu auto-generation
    _menu_name = 'name'
    _menu_icon = 'STOCK_EXECUTE'
    _menu_parent = _get_parent_menu_id
    _menu_res_model = 'afs.wizard.create'
    _menu_view_type = 'form'
    _menu_view_mode = 'form'
    _menu_context = _get_menu_context
    _menu_target = 'new'
    
    _name = "afs.model"
    _defaults = {'save_price' : False, 'tva_position' : 'd', 'ttc_position' : 'c', 'ht_position' : 'd'}
    _columns = {
        "name" : fields.char(_("Name"), size=120, required=True),
        "category_id" : fields.many2one("afs.model.category", _("Category"), required=True),
        "partner_id" : fields.many2one("res.partner", _("Partner")),
        "tax_id" : fields.many2one("account.tax", _('Tax'), domain=TAX_DOMAIN),
        "ref" : fields.char(_("REF"), size=120, required=True),
        "save_price" : fields.float(),
        "ht_position": fields.selection(POSITION, _('Untaxed Position'), required=True),
        "tva_position" : fields.selection(POSITION, _('VAT Position'), required=True),
        "ttc_position" : fields.selection(POSITION, _('Taxed Position'), required=True),
        "ht_account" : fields.many2one("account.account", _('Untaxed Account'), domain=ACCOUNTS_DOMAIN, required=True),
        "tva_account" : fields.many2one("account.account", _('VAT Account'), domain=ACCOUNTS_DOMAIN, required=True),
        "ttc_accounts" : fields.one2many("afs.model.entry", "model_id", _('Taxed Accounts'), required=True)
    }

class ModelCategory(AttachMenu, osv.osv):
    
    """
    Categories for models.
    """

    def name_get(self, cr, uid, ids, context=None):

        """
        The showed name of the category must contains its children.
        """

        if not len(ids):
            return []

        objects = self.read(cr, uid, ids, ['name','parent_id'], context)
        result = []

        for category in objects:
            name = category['name']
            if category['parent_id']:
                name = "%s / %s" % (category['parent_id'][1], name)
            result.append((category['id'], name))
        return result

    def on_parent_changed(self, cursor, user_id, objects_ids, parent_id):
        
        """
        The category sequence is the same than its parent.
        """
        
        if not parent_id:
            sequence = self._get_default_sequence(cursor, user_id)
        else:
            sequence = self.read(cursor, user_id, parent_id)['sequence'] + 1
        
        return {'value' : {'sequence' : sequence}}

    def _get_complete_name(self, cursor, user_id, object_ids, field_name, arg, context=None):
        
        return dict(self.name_get(cursor, user_id, object_ids, context))
    
    def _get_default_sequence(self, cursor, user_id, context=None):
        
        """
        Returns the default sequence based on the previous one + 100.
        """
        
        bigger = self.search(cursor, user_id, [('sequence', '>=', '0')], order="sequence")

        try:
            bigger = self.read(cursor, user_id, bigger)[-1]['sequence']
        except IndexError:
            new = 0
        else:
            new = bigger + 100
        
        return new

    def unlink(self, cursor, user_id, ids, context=None):

        """
        We have to remove all models manually because 'CASACDE' doesn't call unlink().
        """

        for id in ids:
            self.pool.get('afs.model').unlink(cursor, user_id,
                self.pool.get('afs.model').search(cursor, user_id,
                    [('category_id', '=', id),]
                ), context
            )

        return super(ModelCategory, self).unlink(cursor, user_id, ids, context)

    def _get_parent_menu_id(self, cursor, user_id, object, context=None):

        """
        Must returns the parent menu id.
        """

        if not object.parent_id.id:
            return 'afs_menu'

        return object.parent_id.menu_id.id
    
    # Configure menu auto-generation
    _menu_name = 'name'
    _menu_parent = _get_parent_menu_id
    
    _name = "afs.model.category"
    _order = "sequence,id"
    _defaults = {'sequence' : _get_default_sequence}
    _columns = {
        "name" : fields.char(_("Name"), size=120, required=True),
        "complete_name": fields.function(_get_complete_name, method=True, type="char", string='Name'),
        "parent_id" : fields.many2one("afs.model.category", _("Parent")),
        "child_ids": fields.one2many('afs.model.category', 'parent_id', _('Child Categories')),
        "model_ids" : fields.one2many("afs.model", "category_id", _("Models")),
        "sequence": fields.integer("Sequence", help="Represents the weight of the item in the menu. Bigger number means menu will be at bottom."),
    }

class TTCModelEntry(osv.osv):

    _name = "afs.model.entry"
    _rec_name = "payment_mode"
    _columns = {
        "model_id" : fields.many2one("afs.model", _("Model"), required=True, ondelete='cascade'),
        "account_id" : fields.many2one("account.account", _("Account"), required=True, domain=ACCOUNTS_DOMAIN),
        "journal" : fields.many2one("account.journal", _('Journal'), domain=JOURNALS_DOMAIN, required=True),
        "payment_mode" : fields.selection(PAYMENTS_MODES, _("Payment mode"), required=True),
    }

# - Instances -
ModelCategory(), Model(), TTCModelEntry(), Tax()
