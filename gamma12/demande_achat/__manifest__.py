{
'name':"Demande d'achat",
'sequence': '1',
'description':' ',
'depends':['base','purchase','product','mail','hr'],
'data':[ 'data/ir_sequence.xml',
         'security/ir.model.access.csv',
         'reports/demande_achat.xml',
         'reports/report.xml',
         'wizard/motif_wizard.xml',
         'views/view.xml',
         'views/purchase_order.xml',

         ],

}