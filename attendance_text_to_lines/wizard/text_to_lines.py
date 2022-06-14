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
            
    def attendance_ticket_lines_from_text(self):
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
#         raise UserError(str(values))
        
        values.pop(0) #removing headers

        for val in values:
            employee = self.env['hr.employee'].search([('x_studio_machine_code','=',val[0])])
            if employee:
                time_in_check = False
                time_out_check = False

                #default datetime
                default_date_time_str = '01/01/90 00:00:00'
                default_date_time_obj = datetime.strptime(default_date_time_str, '%d/%m/%y %H:%M:%S')

                if val[4] != '' or val[4]:
                    # date_year = val[1].split('-')[0]
                    # date_month = val[1].split('-')[1]
                    # date_date = val[1].split('-')[2]
                    time_in_date_time_str = val[1]+' '+val[4]
                    time_in_date_time_obj = datetime.fromisoformat(time_in_date_time_str)
                    time_in_check = True

                if val[5] != '' or val[5]:
                    time_out_date_time_str = val[1]+' '+val[5]
                    # time_out_date_time_obj = datetime.strptime(time_out_date_time_str, '%d-%m-%y %H:%M:%S')
                    time_out_date_time_obj = datetime.fromisoformat(time_out_date_time_str)
                    time_out_check = True

                attendance_id = self.env['hr.attendance'].create({
                    'employee_id': employee.id,
                    'x_studio_on_duty': val[2],
                    'x_studio_off_duty': val[3],
                    'check_in': time_in_date_time_obj if time_in_check else default_date_time_obj,
                    'check_out': time_out_date_time_obj if time_out_check else default_date_time_obj,
                })
        
