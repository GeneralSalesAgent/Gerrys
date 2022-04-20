from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_is_zero
from dateutil.relativedelta import relativedelta
import datetime


class EmployeeLoan(models.Model):
    _name = 'employee.loan'
    _description = 'Loan and Advance application form for employees'
    _rec_name = 'name_sequence'


    # employee_name = fields.Char(string="Emplyee Name")
    employee_name = fields.Many2one('hr.employee', string='Employee Name', required=True)
    loan_date = fields.Date(string="Loan/Advance Date", required=True)
    loan_type = fields.Selection([
        ('loan', 'Loan'),
        ('advance', 'Advance')], string='Loan Type', required=True)
    time_period = fields.Integer(string='Time Period in Months', required=True)
    loan_amount = fields.Integer(string='Amount of Loan', required = True)
    total_amount = fields.Integer(string='Total Amount', compute="compute_all_amounts")
    paid_amount = fields.Integer(string='Paid Amount', compute="compute_all_amounts")
    unpaid_amount = fields.Integer(string='Unpaid Amount', compute="compute_all_amounts")

    # next_due_date = fields.Char(string='Next Due Date', readonly = True)
    name_sequence = fields.Char(string="Loan Reference", required=True, copy=False, readonly=True, index=True, default=lambda self:_('New'))
    
    loan_lines = fields.One2many('employee.loan.lines', 'loan_reference', string='Loan Lines')

    def btn_compute_installments(self):
        if self.loan_lines:
            raise UserError('You cannot compute installments again')
        lines=[]
        loandate = self.loan_date
        # raise UserError(str(type(loandate)))
        for i in range(self.time_period):
            loandate=loandate + relativedelta(months=1)
            adate = str(loandate)
            bdate = datetime.datetime.strptime(adate, "%Y-%m-%d")
            lines.append((0,0,{
                'loan_reference':self.name_sequence,
                'employee_name':self.employee_name.id,
                'amount_to_pay':self.loan_amount/self.time_period,
                'original_amount_to_pay':self.loan_amount/self.time_period,
                'due_date': loandate,
                'month': bdate.month,
                'year': bdate.year,
                'type_loan': self.loan_type,
                'status': 'unpaid',
            }))

            # raise UserError(str(lines))

        self.update({
                'loan_lines': lines,
            })

    @api.model
    def create(self, vals):
        if vals.get('name_sequence', _('New')) == _('New'):
            vals['name_sequence'] = self.env['ir.sequence'].next_by_code('employee.loan.sequence') or _('New')
        result = super(EmployeeLoan, self).create(vals)
        return result

    def compute_all_amounts(self):
        self.total_amount = 0
        self.paid_amount = 0
        self.unpaid_amount = 0

        # self.total_amount = self.loan_amount
        
        if self.loan_lines:
            self.total_amount = self.loan_amount
            for record in self.loan_lines:
                if record.status == 'paid':
                    self.paid_amount = self.paid_amount + record.amount_to_pay
                elif record.status == 'unpaid':
                    self.unpaid_amount = self.unpaid_amount + record.amount_to_pay

    @api.onchange('loan_lines')
    def loan_lines_change(self):
        update = 0
        lineadd = 0
        countr=0
        difference = 0
        for record in self.loan_lines:
            countr+=1
            if str(record.amount_to_pay) != str(record.original_amount_to_pay):
                difference = record.original_amount_to_pay - record.amount_to_pay
                record.original_amount_to_pay = record.amount_to_pay
                update = 1
                lineadd = 1
                continue

            if update == 1:
                record.amount_to_pay = record.amount_to_pay + difference
                record.original_amount_to_pay = record.amount_to_pay
                update = 0
                lineadd = 0
                continue

        if update == 1 and lineadd == 1:
            lines=[]
            loandate = self.loan_lines[-1]['due_date']
            loandate=loandate + relativedelta(months=1)
            adate = str(loandate)
            bdate = datetime.datetime.strptime(adate, "%Y-%m-%d")
            amounttopay = 0 + difference
            originalamounttopay = amounttopay
            # seq = str(self.name_sequence)
            loanid = self.env['employee.loan'].search([('name_sequence', '=', self.name_sequence)])
            split = str(self.id).split('_')[1]
            # raise UserError(str(loanid))
            lines.append((0,0,{
                'loan_reference':loanid,
                'employee_name':self.employee_name.id,
                'amount_to_pay':amounttopay,
                'original_amount_to_pay':originalamounttopay,
                'due_date': loandate,
                'month': bdate.month,
                'year': bdate.year,
                'type_loan': self.loan_type,
                'status': 'unpaid',
            }))

                # raise UserError(str(lines))

            self.update({
                    'loan_lines': lines,
                })

            


class EmployeeLoanLine(models.Model):
    _name = 'employee.loan.lines'
    _description = 'Loan and Advance application lines for employees'

    loan_reference = fields.Many2one('employee.loan', string='Loan Reference', required=True)
    employee_name = fields.Many2one('hr.employee', string='Employee Name', required=True)
    amount_to_pay = fields.Integer(string='Amount To Pay')
    original_amount_to_pay = fields.Integer(string='Original Amount To Pay')
    due_date = fields.Date(string='Due Date')
    month = fields.Char(string='Month#')
    year = fields.Char(string='Year#')
    type_loan = fields.Char(string='Loan Type', readonly=True)
    status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid')], string='Loan Type', required=True, default="unpaid")

    # loan_date = fields.Date(string="Loan/Advance Date", required=True)
    # loan_type = fields.Selection([
    #     ('loan', 'Loan'),
    #     ('advance', 'Advance')], string='Loan Type', required=True)


