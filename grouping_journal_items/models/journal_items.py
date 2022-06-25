# -*- coding: utf-8 -*-
import pandas as pd
from odoo import models, fields, api
from odoo.exceptions import UserError

accounts_list = []
account_amount = {}
class AccountMoveGroupTotal(models.Model):
    _name = 'account.move.group.total'
    _description = 'Account move line group by account'
    _order = "debit desc, id"
    _check_company_auto = True

    move_id = fields.Many2one('account.move', string='Journal Entry Total',
                              index=True, required=True, readonly=True, auto_join=True, ondelete="cascade")
    company_id = fields.Many2one(related='move_id.company_id', store=True, readonly=True)
    company_currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency',
                                          readonly=True, store=True,
                                          help='Utility field to express amount currency')
    debit = fields.Monetary(string='Debit', default=0.0, currency_field='company_currency_id')
    credit = fields.Monetary(string='Credit', default=0.0, currency_field='company_currency_id')
    balance = fields.Monetary(string='Balance', store=True,
                              currency_field='company_currency_id',
                              compute='_compute_balance')
    account = fields.Char(string='Account', index=True)
    planned_amount = fields.Float(String="Planned")
    practical_amount = fields.Float(String="Planned")

    @api.depends('debit', 'credit')
    def _compute_balance(self):
        for line in self:
            line.balance = line.debit - line.credit


class AccountMove(models.Model):
    _inherit = 'account.move'

    account_move_group_total = fields.One2many('account.move.group.total', 'move_id', string='Journal Items By Account',
                                               copy=True, readonly=True,
                                               compute="_compute_total_groups", index=1, store=1)
    account_move_grouped_total = fields.Boolean(default=False, compute="_compute_total_groups")
    

    @api.depends('line_ids', 'state')
    def _compute_total_groups(self):
        for move in self:
            total_ids = [(5, 0, 0)]
            lines = []
            #Asir Custom code
            account_amount = {}
            for line in move.invoice_line_ids:
                account_amount.update({
                    str(line.account_id.name):line.x_studio_planned,
                    str(line.account_id.name + "_practical"):line.x_studio_practical,
                })
                
            for line in move.line_ids:
#                 raise UserError(str(account_amount))
                #Asir Custom Code
                try:
                    line_data = {
                        "account": line.account_id.code + " " + line.account_id.name,
                        "debit": line.debit,
                        "credit": line.credit,
                        "planned_amount": account_amount[str(line.account_id.name)],
                        "practical_amount": account_amount[str(line.account_id.name + "_practical")],
                        "line_type": 1 if line.debit > 0 else 0
                    }
                except:
                    line_data = {
                        "account": line.account_id.code + " " + line.account_id.name,
                        "debit": line.debit,
                        "credit": line.credit,
#                         "planned_amount": account_amount[str(line.account_id.id)],
                        "line_type": 1 if line.debit > 0 else 0
                    }
                lines.append(line_data)
            if lines:
                column_counts = 0
                df = pd.DataFrame(lines)
                totals = df.groupby(['account', 'line_type']).sum()
                for idx in totals.index:
                    d = {'account': idx[0]}
                    d = {**d, **{col: totals.loc[idx, col] for col in totals}}
                    column_counts+=1
                    total_ids.append((0, 0, d))
#             raise UserError(str(total_ids))
#             raise UserError(str(account_amount.items()))
            #Asir Custom Code
            try:
                for data in total_ids:
                    raise UserError(str(data))
                    if data != total_ids[0] and data[2]['planned_amount'] != 0:
                        for key, value in account_amount.items():
                            if key in data[2]['account'] and value != data[2]['planned_amount']:
                                data[2]['planned_amount'] = value
#                                 data[2]['planned_amount'] = data[2]['planned_amount']
#                                 data[2]['planned_amount'] = data[2]['planned_amount']/column_counts
                                break
            except:
                pass
            
            try:
                for data in total_ids:
                    if data != total_ids[0] and data[2]['practical_amount'] != 0:
                        for key, value in account_amount.items():
                            if key in data[2]['account'] and value != data[2]['practical_amount']:
                                data[2]['planned_amount'] = value
#                                 data[2]['practical_amount'] = data[2]['practical_amount']
#                                 data[2]['practical_amount'] = data[2]['practical_amount']/column_counts
                                break
            except:
                pass
            
            move.account_move_group_total = total_ids
            move.account_move_grouped_total = True
        #Asir calling custom method
#         self.myMethod()

    def total_debit_credit(self):
            res = {}
            for move in self:
                dr_total = 0.0
                cr_total = 0.0
                for line in move.line_ids:
                    dr_total += line.debit
                    cr_total += line.credit
                res.update({'cr_total': cr_total, 'dr_total': dr_total})
            return res

    def totals_debit_credit(self):
            res = {}
            for move in self:
                dr_total = 0.0
                cr_total = 0.0
                for line in move.account_move_group_total:
                    dr_total += line.debit
                    cr_total += line.credit
                res.update({'cr_total': round(cr_total, 2), 'dr_total': round(dr_total, 2)})
            return res

    def group_lines(self):
        self._compute_total_groups()
