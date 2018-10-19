# -*- coding: utf-8 -*-

from odoo import models, fields, api
class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    vehicle_service_order = fields.Boolean(string='是否车辆服务订单', help="是否车辆服务订单.")