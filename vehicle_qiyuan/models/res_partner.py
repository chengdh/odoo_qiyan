# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    vehicle = fields.Boolean(string='是否车辆', help="是否车辆.")

    v_driver = fields.Char(string='司机姓名', size=10, help="司机姓名.")

    v_model = fields.Char(string='型号', size=60, help="型号.")

    v_weight = fields.Float(string='载重量(吨)', help="载重量.", digits=(16, 2))

    v_w = fields.Float(string='宽度(米)', help="宽度.", digits=(16, 2))
    v_l = fields.Float(string='长度(米)', help="长度.", digits=(16, 2))
    v_h = fields.Float(string='高度(米)', help="高度.", digits=(16, 2))
    v_order = fields.Integer(string='排班序号', help="排班序号.", default=-1)
    v_state = fields.Selection([
        ('free', '空闲'),
        ('busy', '工作中'),
    ],
                               string='车辆状态',
                               index=True,
                               default='free')

    vehicle_cat_id = fields.Many2one(
        'qiyuan.vehicle_cat', string='所属分类', help="车辆所属分类.")


class VehicleCat(models.Model):
    '''
    车辆分类
    '''
    _name = "qiyuan.vehicle_cat"
    _description = '车辆分类'
    _order = 'order_by'

    name = fields.Char(string='分类名称', required=True)
    active = fields.Boolean(
        default=True,
        string="有效",
        help=
        "The active field allows you to hide the category without removing it."
    )
    note = fields.Char(string='分类说明')
    order_by = fields.Integer(string='排序', help="排序.", default=1)