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
import base64
import StringIO

from openerp.osv import osv, fields
from openerp.tools.misc import cache
from openerp.tools.translate import _
from openerp.tools.convert import convert_xml_import

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
      
    def _default_tax(self, cursor, user_id, context):

        model = self.pool.get('afs.model').read(cursor, user_id, context['model'])

        if model['tax_id']:
            return model['tax_id'][0]

        return None

    def _default_payment_mode(self, cursor, user_id, context):

        try:
            return self._get_payments_mode(cursor, user_id, context)[0]
        except KeyError:
            return

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

    @cache(5)
    def _get_payments_mode(self, cursor, user_id, context=None):

        """
        We returns the Payment mode associated with the model specified in context.
        Only modes that have a line in TCC entries are returned.
        """

        if 'model' not in context:
            return

        model = self.pool.get('afs.model').browse(cursor, user_id, context['model'])
        modes = [a.payment_mode for a in model.ttc_accounts]

        return [(k, v) for k, v in PAYMENTS_MODES if k in modes]

    def on_amount_ht_changed(self, cursor, user_id, id, amount_ht, tax):

        if not tax:
            result = {
                'amount_ttc' : 0,
                'amount_ht' : 0
            }
        else:
            tax = self.pool.get('account.tax').browse(cursor, user_id, tax)
            computed_prices = self.pool.get('account.tax').compute_all(cursor, user_id, [tax], amount_ht, 1)
            result = {
                'amount_ttc' : computed_prices['total_included'],
                'amount_ht' : computed_prices['total']
            }

        return {'value': result}

    def on_amount_ttc_changed(self, cursor, user_id, id, amount_ttc, tax_id):

        result = {}

        if not tax_id:
            return result

        taxes = self.pool.get('account.tax').browse(cursor, user_id, [tax_id])
        computed = self.pool.get('account.tax').compute_inv(cursor, user_id, taxes, amount_ttc, 1)[0]

        result = {
            'amount_ttc' : amount_ttc,
            'amount_ht' : computed['price_unit']
        }

        return {'value': result}

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
        'tax_id' : fields.many2one('account.tax', _('Tax'), readonly=True),
        'payment_mode' : fields.selection(_get_payments_mode, _('Payment mode'), required=True),
        'save' : fields.boolean(_('Remember the price')),
    }
    _defaults = {
        'date' : fields.date.today,
        'period' : _default_period,
        'ref' : _default_ref,
        'partner' : _default_partner,
        'tax_id' : _default_tax,
        'amount_ht' : _default_amount_ht,
        'amount_ttc' : 0.0,
        'save' : _default_save,
        'payment_mode' : _default_payment_mode,
    }

class ImportExportWizard(osv.osv_memory):

    """
    This wizard manage the import/export function of this module.
    """

    def on_import_clicked(self, cursor, user_id, ids, context=None):

        """
        Load the XML file, and close the window if everything is ok.
        """

        file_data = self.read(cursor, user_id, ids[0], context=context)['file']
        file_data = base64.decodestring(file_data)

        fake_file = StringIO.StringIO(file_data)

        convert_xml_import(cursor, 'account_fr_simplified', fake_file, mode='update', noupdate=True)
        
    def get_export_file(self, cursor, user_id, context=None):

        """
        Fills the 'file' field with export data. An XML file is created which contains :
            - Categories
            - Models
            - Models entries
        """

        if context and 'export' not in context:
            return

        pmodels, pcategory, pentry = get_poolers(cursor, 'afs.model', 'afs.model.category', 'afs.model.entry')

        data  = '<?xml version="1.0" encoding="utf-8"?>'
        data += '<openerp><data>'

        category_ids = pcategory.search(cursor, user_id, [], context=context)
        categories = pcategory.browse(cursor, user_id, category_ids, context=context)
        model_ids = pmodels.search(cursor, user_id, [], context=context)
        models = pmodels.browse(cursor, user_id, model_ids, context=context)

        for category in categories:
            data += '<record model="afs.model.category" id="category_%d">' % category.id
            data += '<field name="name">%s</field>' % category.name
            if category.parent_id.id:
                data += '<field name="parent_id" ref="category_%d"/>' % category.parent_id.id
            data += '<field name="sequence">%d</field></record>' % category.sequence

        # Create a record for each model, category and entries
        for model in models:

            # Now, add the model basic data
            data += '<record model="afs.model" id="model_%d">' % model.id
            if model.category_id.id:
                data += '<field name="category_id" ref="category_%d"/>' % model.category_id.id
            if model.partner_id.id:
                data += '<field name="partner_id" search="[(\'name\', \'=\', \'%s\')]"/>' % model.partner_id.name
            if model.tax_id.id:
                data += "<field name=\"tax_id\" search=\"['|', ('name', '=', '%s'), ('description', '=', '%s')]\"/>" % (
                    model.tax_id.name, model.tax_id.description)
            for field in ('name', 'ref', 'save_price', 'ht_position', 'tva_position', 'ttc_position'):
                data += '<field name="%s">%s</field>' % (field, getattr(model, field))
            data += '<field name="ht_account" search="[(\'code\', \'=\', %s)]"/>' % model.ht_account.code
            data += '<field name="tva_account" search="[(\'code\', \'=\', %s)]"/>' % model.tva_account.code
            data += '</record>'

            # And model TTC entries
            for ttc_entry in model.ttc_accounts:
                data += '<record model="afs.model.entry" id="ttc_account_%d">' % ttc_entry.id
                data += '<field name="model_id" ref="model_%d"/>' % model.id
                data += '<field name="account_id" search="[(\'code\', \'=\', %s)]"/>' % ttc_entry.account_id.code
                data += '<field name="journal" search="[(\'code\', \'=\', \'%s\')]"/>' % ttc_entry.journal.code
                data += '<field name="payment_mode">%s</field>' % ttc_entry.payment_mode
                data += '</record>'

        data += '</data></openerp>'

        return base64.encodestring(data.encode('utf-8'))

    _name = 'afs.wizard.import_export'

    _columns = {
        'file' : fields.binary(_('File')),
        'file_name' : fields.char(_('File name'), size=255),
        'state' : fields.selection((('import', 'Import'), ('export', 'Export')))
    }

    _defaults = {
        'state' :
            lambda self, cursor, user_id, context: context.get('import', False) and 'import' or 'export',
        'file' : get_export_file,
        'file_name' : 'export.xml',
    }

CreateEntryWizard(), ImportExportWizard()
