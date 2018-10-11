# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    unit_price_per_cubic_metre = fields.Float(
        string="单价(元/方)", help="加气砖单价", digits=(16, 2))
    distance = fields.Float(string="距离(公里)", help="工地运输距离", digits=(16, 2))
    carrying_price = fields.Float(
        string="运费单价(元/公里.方)", help="运输单价", digits=(16, 2))
