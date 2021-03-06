# -*- coding: utf-8 -*-
{
    'name': "vehicle_qiyuan",

    'summary': """
        启源建材-车辆管理模块
        """,

    'description': """
        启源建材-车辆管理模块:
        1 车辆信息管理
        2 车辆分类管理
    """,

    'author': "cheng.donghui@gmail.com",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/stock_picking_report.xml',
        'report/stock_picking_report_templates.xml',
        'views/res_partner_views.xml',
        'views/stock_picking_views.xml',
        'data/product_data.xml',
        'data/ir_sequence_data.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}