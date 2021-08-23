{
    'name': 'Fabrication IT',
    'summary': "Fabrication Réaliser par ItAdvisor",
    'description': """
        Fabrication Réaliser par ItAdvisor
    """,
    'sequence': '1',
    'version': '12.0.1.1.15',
    'author': 'ItAdvisor Inc',
    'maintainer': 'BBA',
    'category': 'Custom',
    'depends': ['sale', 'sale_management', 'mail', 'product', 'stock', 'purchase', 'uom', 'hr'],
    'data': ['security/fabrication_security.xml',
             'security/ir.model.access.csv',
             'views/manufacture.xml',
             'views/ordre_fabrication.xml',
             'views/product_template.xml',
             'report/ordre_fabrication_report.xml',
             'report/report_production.xml',
             'data/ir_sequence.xml',
             'data/fabrication_location.xml',
             'views/sale.xml',
             'views/manufacture_product.xml',
             'views/stock_picking_fabrication_views.xml'
             ],
    'application': True,
    'installable': True,
}
