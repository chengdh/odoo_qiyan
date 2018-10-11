# -*- coding: utf-8 -*-
from odoo import http

# class VehicleQiyuan(http.Controller):
#     @http.route('/vehicle_qiyuan/vehicle_qiyuan/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vehicle_qiyuan/vehicle_qiyuan/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vehicle_qiyuan.listing', {
#             'root': '/vehicle_qiyuan/vehicle_qiyuan',
#             'objects': http.request.env['vehicle_qiyuan.vehicle_qiyuan'].search([]),
#         })

#     @http.route('/vehicle_qiyuan/vehicle_qiyuan/objects/<model("vehicle_qiyuan.vehicle_qiyuan"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vehicle_qiyuan.object', {
#             'object': obj
#         })