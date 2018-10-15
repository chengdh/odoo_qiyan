# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Picking(models.Model):

    _inherit = "stock.picking"

    po_id = fields.Many2one('purchase.order', string='车辆运输订单',help='该配送单关联的运输订单')

    @api.multi
    def create_po(self):
        '''
        根据当前出库单生成车辆运输订单
        '''
        for picking in self:

