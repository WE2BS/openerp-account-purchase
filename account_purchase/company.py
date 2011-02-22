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

from osv import osv, fields
from tools.translate import _

class Company(osv.osv):

    """
    We redefine the company model to add a configuration field about VAT.
    """

    _inherit = 'res.company'
    _name = 'res.company'
    _columns = {
        'afs_vat' : fields.boolean(_('Apply the tax in account_purchase'),
            help=_("Uncheck this if your company don't pay tax on purchase. For example, it's the in France "
                   "if you are not subjected to VAT, like some associations."))
    }
    _defaults = {
        'afs_vat' : True,
    }

Company()
