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

class Company(osv.osv):

    """
    We redefine the company model to add a configuration field about VAT.
    """

    _inherit = 'res.company'
    _name = 'res.company'
    _columns = {
        'afs_vat' : fields.boolean(_('This company is subject to VAT.'),
            help=_('Check this if you company is subject to VAT. This is used by the Account '
                   'FR Simplified module to handle journal entries.'))
    }

Company()
