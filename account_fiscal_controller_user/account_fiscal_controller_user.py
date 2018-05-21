# -*- coding: utf8 -*-
#
#    Copyright (C) 2018 NDP Systèmes (<http://www.ndp-systemes.fr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from openerp import models, api, _
from openerp.exceptions import UserError


class FiscalControlerUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def unlink(self):
        user_fiscal_controller = self.env.ref('account_fiscal_controller_user.user_fiscal_controller')
        if user_fiscal_controller in self:
            raise UserError(_(u"You are not allowed to delete fiscal controller user."))
        return super(FiscalControlerUsers, self).unlink()
