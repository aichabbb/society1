# -*- coding: utf-8 -*-


{
    'name': "template_gamma ",

    'summary': """  """,

    'description': """ """,

    'author': "itadvisor",
    'website': "http://www.itadvisor.ma",

    'category': 'Uncategorized',
    'version': '12.0.0.1.0',


    'depends': ['base', 'hr_expense', 'hr','employee','sale_expense'],


    'data': [

        'security/ir.model.access.csv',

        'views/modification_form_note_frais.xml',
        'reports/rapport.xml',



    ],



    'installable': True,
    'application': True,
    'auto_install': False,
}
