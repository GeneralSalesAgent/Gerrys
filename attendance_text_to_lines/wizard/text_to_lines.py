# -*- coding: utf-8 -*-
from calendar import month_abbr
from datetime import datetime,date,timedelta
import pty
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import re
from xlrd import open_workbook

class AttendanceTicketText(models.TransientModel):
    _name = 'attendance.ticket.text'

    file_to_upload = fields.Binary(string="Attendance File")
    file_name = fields.Char(string="Filename")
            
    #for Pegasus Airline
    def attendance_ticket_lines_from_text(self):
        pax_sales = self.env['x_pax_sales'].search([('id','=',self._context.get('active_id'))])
        if not self.file_to_upload:
            raise UserError('Please upload file first')

        wb = open_workbook(file_contents = base64.b64decode(self.file_to_upload))
        sheet = wb.sheets()[0]
        values = []
        for row in range(sheet.nrows):
            col_value = []
            for col in range(sheet.ncols):
                value  = (sheet.cell(row,col).value)
                try:
                    value  = datetime(int(value))
                except:
                    pass
                col_value.append(value)
            values.append(col_value)
        raise UserError(str(values))
        