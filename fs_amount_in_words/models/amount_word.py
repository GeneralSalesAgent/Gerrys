# -*- coding: utf-8 -*-
##############################################################################
#
#    #
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models
from datetime import datetime


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    # @api.multi
    def _compute_amount_in_word(self):
        for rec in self:
                rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total))

    num_word = fields.Char(string="This sale order is approved for the sum of: ", compute='_compute_amount_in_word')


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    # @api.multi
    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total))

    num_word = fields.Char(string="This purchase order form is approved for the sum of: ", compute='_compute_amount_in_word')


class InvoiceOrder(models.Model):

    _inherit = 'account.move'

    # @api.multi
    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total))

    num_word = fields.Char(string="This invoice is approved for the sum of: ", compute='_compute_amount_in_word')
