from odoo import models, fields, api,_
from odoo.tools import safe_eval

class AccountsHierarchy(models.TransientModel):
    _name = "accounts.hierarchy"
    _description = "Accounts Hiearchy"

    @api.model
    def get_company_ids(self):
        company_ids = []
        user_id = self.env['res.users'].sudo().search([('id','=',self.env.uid)])
        for rec in user_id.company_ids:
            company_ids.append(rec.id)    
        return "[('id', 'in', %s)]" % (company_ids)

    company_id = fields.Many2one('res.company', string='Company', domain=get_company_ids, required=True, default=lambda self: self.env.user.company_id)

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()

    def _get_html(self):
        result = {}
        rcontext = {}
        context = dict(self.env.context)
        if context.get('active_id') and context.get('active_model') == 'accounts.hierarchy' and context.get('company_id'):
            rcontext['lines'] = self.with_context(context).get_lines(wizard_id=context.get('active_id'))
            rcontext['heading'] = self.env['res.company'].browse(context.get('company_id')).display_name
        report = self.env['ir.actions.report']._get_report_from_name('accounts_hierarchy.report_accounts_heirarchy')
        result['html'] = self.env.ref('accounts_hierarchy.report_accounts_heirarchy')._render(rcontext)
        return report

    @api.model
    def get_lines(self, wizard_id=None, line_id=None, **kw):
        context = dict(self.env.context)
        if wizard_id:            
            context.update({
                'company_id' : self.browse(wizard_id).company_id.id,
                'active_id' : self.browse(wizard_id).id
            })
        rec_id = False
        level = 1
        if kw:
            level = kw.get('level', 0)
            rec_id = kw.get('rec_id')
        res = []        
        accounts = self.env['account.account'].with_context(context).search([
                ('company_id','=',context.get('company_id',False)),('parent_id','=',line_id)])        
        res = self._lines(wizard_id,line_id, rec_id=rec_id, level=level, accounts=accounts)        
        final_vals = sorted(res, key=lambda v: v['code'], reverse=False)
        lines = self._final_vals_to_lines(final_vals, level)
        return lines
    
    @api.model
    def _lines(self, wizard_id=None, line_id=None, rec_id=False, level=0, accounts=[], **kw):
        final_vals = []
        accounts = accounts or []
        context = self._context
        unfoldable = False
        for account in accounts:
            final_vals += self._make_dict_line(level = level, wizard_id = wizard_id, parent_id=line_id, account=account,unfoldable=False)
        return final_vals
    
    # @api.model
    # def _amount_to_str(self, value, currency):
    #     return self.env['ir.qweb.field.monetary'].value_to_html(value, {'display_currency': currency})

    def _make_dict_line(self, level=False, wizard_id=False, parent_id=False, account=False,unfoldable=False):
        data = []
        data = [{
            'wizard_id': wizard_id,
            'id': account.id,
            'level': level,
            'unfoldable': account.has_child and True or False,
            'rec_id': account.id,
            'parent_id': parent_id,
            'code': account.code,
            'name': account.name,
            'type': account.user_type_id.name,
            # _______________________code modified by MzM - ABS_______________________
            'debit': str(account.company_id.currency_id.symbol) + " " + str(account.debit),
            'credit': str(account.company_id.currency_id.symbol) + " " + str(account.credit),
            'balance': str(account.company_id.currency_id.symbol) + " " + str(account.balance)
            # 'debit': self._amount_to_str(account.debit, account.company_id.currency_id),
            # 'credit': self._amount_to_str(account.credit, account.company_id.currency_id),
            # 'balance': self._amount_to_str(account.balance, account.company_id.currency_id),



            }]
        return data

    @api.model
    def _final_vals_to_lines(self, final_vals, level):
        lines = []
        for data in final_vals:
            lines.append({
                'wizard_id': data['wizard_id'],
                'id': data['id'],
                'level': level,
                'unfoldable': data['unfoldable'],
                'rec_id': data['rec_id'],
                'parent_id': data['parent_id'],
                'type': data.get('type'),
                'name': _(data.get('name')),
                'columns': [data.get('code'),data.get('name'),data.get('type'),data.get('debit'),data.get('credit'),data.get('balance')],                
            })
        return lines
    
    def accounts_hierarchy_open_wizard(self):        
        self.ensure_one()
        used_context = {
            'company_id': self.company_id.id,
            'active_id': self.id
        }
        self  = self.with_context(used_context)
        result = {}
        if self.env['account.account'].search([('parent_id','!=',False)],limit=1):
            result = self.env.ref('accounts_hierarchy.accounts_hierarchy_tag').read([])[0]
        else:           
            result = self.env.ref('account.action_account_form').read([])[0]
        result_context = result.get('context','{}') or {}
        used_context.update(result_context, False)
        result['context'] = str(used_context)
        return result

    @api.model
    def get_child_ids(self, wizard_id=None, account_id=None):
        result = []
        context = dict(self.env.context)
        if wizard_id and account_id:
            accounts = self.env['account.account'].sudo().search([('id','child_of',[account_id])]).ids
            result.append(('account_id','child_of',accounts))
            return result
    
    @api.model
    def get_all_lines(self, line_id=False, level=1):
        self.ensure_one()
        result = []
        for line in self.get_lines(self.id, line_id=line_id, level=level):
            result.append(line)
            result.extend(self.get_all_lines(line_id=line['rec_id'], level=line['level']+1))
        return result

    @api.model
    def get_pdf_lines(self, wizard_id):
        lines = self.browse(wizard_id).get_all_lines()
        return lines

    def get_pdf(self):
        context = dict(self.env.context)        
        lines = self.with_context(print_mode=True).get_pdf_lines(wizard_id = context.get('active_id'))
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        rcontext = {
            'mode': 'print',
            'base_url': base_url,           
        }        
        heading = self.env['res.company'].browse(self.browse(context.get('active_id')).company_id.id).display_name
        body = self.env['ir.ui.view'].with_context(context).render_template(
            "accounts_hierarchy.report_accounts_hierarchy_print",
            values=dict(
                rcontext,
                heading= heading,
                lines=lines,
                report=self,
                context=self),
        )
        header = self.env['ir.actions.report'].render_template("web.internal_layout", values=rcontext)
        header = self.env['ir.actions.report'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=header))

        return self.env['ir.actions.report']._run_wkhtmltopdf(
            [body],
            header=header,
            landscape=True,
            specific_paperformat_args={'data-report-margin-top': 10, 'data-report-header-spacing': 10}
        )
