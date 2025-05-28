

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

        "security/user_group_secutity.xml",
        "security/hostel_rule_security.xml",

        "security/ir.model.access.csv",

        "security/security_company_rules.xml",

        "data/server_action_user.xml",
        "data/base_automation_data.xml",
        "data/ir_cron_data.xml",
        "data/hostel_product_data.xml",
        "data/room_sequence_data.xml",
        "data/facilty_data.xml",
        "data/student_squence_data.xml",


        "report/student_report_template.xml",

        "report/students_report.xml",

        "report/leave_request_report_template.xml",

        "report/leave_request_report.xml",
       "wizard/student_report_wizard_view.xml",
        "wizard/leave_request_report_view.xml",

        "views/hostel_view_management.xml",



        "views/hostel_account_move_view.xml",
        "views/student_inf_view.xml",

        "views/hostel_facility_view.xml",
        "views/hostel_leave_view.xml",
        "views/hostel_cleaning_view.xml",
        "views/hostel_menu.xml",





    ],
    'auto_install': False,
}
