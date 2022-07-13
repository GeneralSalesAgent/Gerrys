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

class AttendanceWorkentries(models.TransientModel):
    _name = 'attendance.workentries'

    # file_to_upload = fields.Binary(string="Attendance File")
    # file_name = fields.Char(string="Filename")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
            
    def attendance_workentries_from_api(self):
        raise UserError("Haris")