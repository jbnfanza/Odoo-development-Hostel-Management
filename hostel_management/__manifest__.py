

{
    'name': "HOSTEL MANAGEMENT",
    'version': '1.0',
    'depends': ['base', 'mail','product','account'],
    'author': "fansa",
    'category': 'Category',
    'description': """
    Description text
    """,
    'application': True,
    'sequence': 1,
    'data': [
        "data/hostel_product_data.xml",

        "data/room_sequence_data.xml",
        "data/facilty_data.xml",
        "data/student_squence_data.xml",
        "security/ir.model.access.csv",
        "views/hostel_view_management.xml",
        "views/hostel_account_move_view.xml",
        "views/student_inf_view.xml",
        "views/hostel_facility_view.xml",
        "views/hostel_leave_view.xml",
        "views/hostel_menu.xml", ],
    'auto_install': False,
}
