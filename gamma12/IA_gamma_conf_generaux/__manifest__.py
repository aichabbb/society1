# -*- coding: utf-8 -*-
{
    'name': "Gamma configuration",

    'summary': """ Add Fields to res company  """,

    'description': """

    """,

    'author': 'ItAdvisor Inc',
    'maintainer': 'ItAdvisor',
    'category': 'Custom',
    'version': '12.0.0.0.1',
    'website': "https://www.itadvisor.ma",
    'sequence': '1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'en-tete_gamma', 'info_societe'],

    # always loaded
    'data': [
        'Views/inherit_res_company.xml'
    ],
    'auto_install': True,
    'instalable': True
}
