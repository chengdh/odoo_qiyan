# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Product(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    w = fields.Integer(string="长度(cm)", help="加气砖宽度-厘米", default=30)
    h = fields.Integer(string="宽度(cm)", help="加气砖高度-厘米", default=20)
    l = fields.Integer(string="高度(cm)", help="加气砖宽度-厘米", default=50)

    @api.onchange('w', 'l', 'h')
    def _compute_volume_and_weight(self):
        '''
        根据长宽高计算体积和重量
        '''
        self.volume = (self.w*self.l*self.h)/1000000
        self.weight = self.volume * 10
