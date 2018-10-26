# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    pieces_qty = fields.Integer(
        string="块数", compute='_compute_pieces_qty', default=0, store=True)

    @api.depends('product_id', 'qty_done')
    def _compute_pieces_qty(self):
        '''
        基础数量是立方米,根据数量计算块数
        '''
        for line in self:
            if line.product_id:
                p_volume = line.product_id.volume
                # FIXME 四舍五入?
                pieces_qty = 0
                if p_volume > 0:
                    pieces_qty = round(line.qty_done / p_volume)
                line.pieces_qty = pieces_qty
