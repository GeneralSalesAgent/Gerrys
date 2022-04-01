from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape

import json

import xlwt
import io
import base64

class AccountsHierarchyController(http.Controller):

    @http.route('/accounts_hierarchy/<string:output_format>/<string:report_name>/<int:report_id>', type='http', auth='user')
    def report(self, output_format, report_name, token, report_id=False, **kw):
        accounts_hierarchy_obj = request.env['accounts.hierarchy'].sudo().browse(report_id)
        try:
            if output_format == 'pdf':
                response = request.make_response(
                    accounts_hierarchy_obj.with_context(active_id=report_id).get_pdf(),
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', 'attachment; filename=' + 'accounts_hierarchy' + '.pdf;')
                    ]
                )
                response.set_cookie('fileToken', token)
                return response
            if output_format == "xls":
                wizard_obj = request.env['accounts.hierarchy'].sudo().browse(report_id)
                heading = request.env['res.company'].browse(wizard_obj.company_id.id).name
                lines = request.env['accounts.hierarchy'].with_context(print_mode=True, output_format=output_format).sudo().get_pdf_lines(report_id)
                if lines:
                    if len(lines) > 65535:
                        raise UserError(_('There are too many rows (%s rows, limit: 65535) to export as Excel 97-2003 (.xls) format.') % len(lines))
                    workbook = xlwt.Workbook()
                    sheet = workbook.add_sheet('Chart of Account')

                    normal = xlwt.easyxf('font: name Times New Roman ;align: horiz left;', num_format_str='#,##0.00')            
                    bold = xlwt.easyxf('font: name Times New Roman bold ;align: horiz left;', num_format_str='#,##0.00')
                    head = xlwt.easyxf('font: name Times New Roman bold ;align: horiz centre, vert centre;', num_format_str='#,##0.00')
                    if heading:
                        sheet.write_merge(0, 1, 0,5, 'Chart of Account Hierarchy for ' + heading + '', bold)
                    else:
                        sheet.write_merge(0, 1, 0,5, 'Chart of Account Hierarchy', head)

                    sheet.write(3, 0,'Code', bold)
                    sheet.write(3, 1,'Name', bold)
                    sheet.write(3, 2,'Type', bold)
                    sheet.write(3, 3,'Debit', bold)
                    sheet.write(3, 4,'Credit', bold)
                    sheet.write(3, 5,'Balance', bold)

                    i = 4

                    for line in lines:
                        sheet.write(i, 0, line['columns'][0] or '', normal)
                        sheet.write(i, 1, line['columns'][1] or '', normal)
                        sheet.write(i, 2, line['columns'][2] or '', normal)
                        sheet.write(i, 3, line['columns'][3] or '0', normal)
                        sheet.write(i, 4, line['columns'][4] or '0', normal)
                        sheet.write(i, 5, line['columns'][5] or '0', normal)            
                        i += 1  
                    fp = io.BytesIO()
                    workbook.save(fp)
                    data = fp.getvalue()
                    fp.close()
                    
                response = request.make_response(
                    data,
                    headers=[('Content-Type', 'application/vnd.ms-excel'),
                            ('Content-Disposition', 'attachment; filename=coahiearchy.xls')],
                    cookies={'fileToken': token}
                )
                return response

        except Exception as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))
