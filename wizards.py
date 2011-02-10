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
#from StringIO import StringIO

import datetime

from lxml import etree

from openerp.osv import osv, fields
from openerp.tools.translate import _

from . afs import PAYMENTS_MODES
from . tools import get_poolers, search_and_read

class CreateEntryWizard(osv.osv_memory):

    """
    This wizard is opened when the user click on a model in the menu.
    """

    def button_valid(self, cursor, user_id, ids, context=None):

        """
        When the wizzard is validated, we add entries to the journals.
        """

        object = self.read(cursor, user_id, ids[0], context=context)
        puser, pmodel, pentry, pmove, pmoveline = get_poolers(cursor,
            'res.users', 'afs.model', 'afs.model.entry', 'account.move', 'account.move.line')
        model_id = context['model']
        model = pmodel.read(cursor, user_id, model_id)
        use_tva = puser.browse(cursor, user_id, user_id, context=context).company_id.afs_vat
        entries = search_and_read(cursor, user_id, pentry,
            [('model_id', '=', model_id)], context)

        for entry in entries:
            if entry['payment_mode'] == object['payment_mode']:
                journal_id = entry['journal'][0]
                ttc_account_id = entry['account_id'][0]

        if not 'journal_id' in locals():
            raise Exception('Model has no TTC line corresponding to this payement mode.')

        #1 - Create header
        account_move = pmove.create(cursor, user_id, {
            'name' : '/',
            'ref' : object['ref'],
            'journal_id' : journal_id,
            'period_id' : object['period'],
            'state' : 'draft',
            'to_check' : False,
            'partner_id' : object['partner'],
            'date' : object['date'],
            'narration' : '(Automatically created by AFS Module)',
        })

        #2 - Add VAT if enabled
        tva = object['amount_ttc'] - object['amount_ht']
        if tva != 0.00 and use_tva:
            pmoveline.create(cursor, user_id, {
                'name' : object['ref'],
                'debit' : tva if model['tva_position'] == 'd' else None,
                'credit' : tva if model['tva_position'] == 'c' else None,
                'account_id' : model['tva_account'][0],
                'move_id' : account_move,
                'narration' : 'Automatically created by AFS Module.',
                'ref' : object['ref'],
                'period_id' : object['period'],
                'journal_id' : journal_id,
                'partner_id' : object['partner'],
                'date' : object['date'],
                'state' : 'draft',
            })

        if use_tva:
            amount_ht = object['amount_ht']
        else:
            amount_ht = object['amount_ttc']

        #3 - Add untaxed amount
        pmoveline.create(cursor, user_id, {
            'name' : object['ref'],
            'debit' : amount_ht if model['ht_position'] == 'd' else None,
            'credit' : amount_ht if model['ht_position'] == 'c' else None,
            'account_id' : model['ht_account'][0],
            'move_id' : account_move,
            'narration' : 'Automatically created by AFS Module.',
            'ref' : object['ref'],
            'period_id' : object['period'],
            'journal_id' : journal_id,
            'partner_id' : object['partner'],
            'date' : object['date'],
            'state' : 'draft',
        })

        #4 - And taxed amount
        pmoveline.create(cursor, user_id, {
            'name' : object['ref'],
            'debit' : object['amount_ttc'] if model['ttc_position'] == 'd' else None,
            'credit' : object['amount_ttc'] if model['ttc_position'] == 'c' else None,
            'account_id' : ttc_account_id,
            'move_id' : account_move,
            'narration' : 'Automatically created by AFS Module.',
            'ref' : object['ref'],
            'period_id' : object['period'],
            'journal_id' : journal_id,
            'partner_id' : object['partner'],
            'date' : object['date'],
            'state' : 'draft',
        })

        # Remember the price if checked
        pmodel.write(cursor, user_id, context['model'],
           {'save_price' : object['amount_ht'] if object['save'] else None})

        return {
            'type': 'ir.actions.act_window_close',
        }

    def _default_period(self, cursor, user_id, context):

        today = datetime.date.today()
        period_ids = self.pool.get('account.period').search(cursor, user_id,
            [('date_start', '<=', today),
             ('date_stop', '>=', today),
             ('state', '=', 'draft')],
        )
        if not period_ids:
            return False
        periods = self.pool.get('account.period').browse(cursor, user_id, period_ids)
        return periods[0].id

    def _default_ref(self, cursor, user_id, context):

        model = self.pool.get('afs.model').read(cursor, user_id, context['model'])
        return model['ref']

    def _default_partner(self, cursor, user_id, context):

        model = self.pool.get('afs.model').read(cursor, user_id, context['model'])
        if model['partner_id']:
            return model['partner_id'][0]
        return False
      
    def _default_tva(self, cursor, user_id, context):

        model = self.pool.get('afs.model').read(cursor, user_id, context['model'])
        return model['tva']

    def _check_amounts(self, cursor, user_id, ids, context=None):

        for record in self.browse(cursor, user_id, ids):
            if record.amount_ht and record.amount_ht <= 0.0: return False
            if record.amount_ht and record.amount_ht <= 0.0: return False
        return True

    def _default_amount_ht(self, cursor, user_id, context=None):

        model = self.pool.get('afs.model').read(cursor, user_id, context['model'])
        return model['save_price']
    
    def _default_save(self, cursor, user_id, context=None):

        model = self.pool.get('afs.model').read(cursor, user_id, context['model'])
        return model['save_price']
   
    def on_amount_ht_changed(self, cursor, user_id, id, amount_ht, tva):

        result = {}
        try:
            result['amount_ttc'] = float(amount_ht) * (1 + tva / 100.0)
        except ValueError:
            result['amount_ttc'] = 0.0
            result['amount_ht'] = 0.0
        return {'value': result}

    def on_amount_ttc_changed(self, cursor, user_id, id, amount_ttc, tva):

        result = {}
        try:
            result['amount_ht'] = float(amount_ttc) / (1 + tva / 100.0)
        except ValueError:
            result['amount_ttc'] = 0.0
            result['amount_ht'] = 0.0
        return {'value': result}

    def fields_view_get(self, cursor, user_id, view_id=None,
            view_type='form', context=None, toolbar=False, submenu=False):

        """
        Replaces the label text with the model name.
        """

        view = super(CreateEntryWizard, self).fields_view_get(
            cursor, user_id, view_id, view_type, context, toolbar, submenu)

        if view_type != 'form' or 'model' not in context:
            return view

        root = etree.XML(view['arch'])
        label = root[0]

        model = self.pool.get('afs.model').read(cursor, user_id, context['model'])
        label.set('string', model['name'])

        view['arch'] = etree.tostring(root)
        
        return view

    _name = "afs.wizard.create"
    _constraints = (
        (_check_amounts, "Amounts must be superior to 0.", ['amount_ht', 'amount_ttc']),
    )
    _columns = {
        'date' : fields.date(_('Date'), required=True),
        'period' : fields.many2one('account.period', _('Period'), required=True),
        'ref' : fields.char(_('REF'), size=120),
        'partner' : fields.many2one('res.partner', _('Partner')),
        'amount_ht' : fields.float(_('Amount untaxed'), required=True),
        'amount_ttc' : fields.float(_('Amount taxed'), required=True),
        'amount_tva' : fields.float(_('TVA'), readonly=True),
        'payment_mode' : fields.selection(PAYMENTS_MODES, _('Payment mode'), required=True),
        'save' : fields.boolean(_('Remember the price')),
    }
    _defaults = {
        'date' : fields.date.today,
        'period' : _default_period,
        'ref' : _default_ref,
        'partner' : _default_partner,
        'amount_tva' : _default_tva,
        'payment_mode' : 'cash',
        'amount_ht' : _default_amount_ht,
        'amount_ttc' : 0.0,
        'save' : _default_save,
    }

CreateEntryWizard()
