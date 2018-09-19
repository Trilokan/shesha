# -*- coding: utf-8 -GPK*-

{
    "name": "Shesha",
    "version": "1.0",
    "author": "La Mars",
    "website": "http://",
    "category": "Naga Kanni",
    "sequence": 1,
    "summary": "Hospital Management System",
    "description": """
    
    Hospital Management System
    
    Patient Management
    Employee Management
    Purchase Management
    Pharmacy Management
    Assert Management
    Accounts Management
    
    """,
    "depends": ["base", "mail"],
    "data": [
        # Main Menu
        'menu/menu.xml',

        # Sequence
        'sequence/base_pack.xml',
        'sequence/account.xml',
        'sequence/product.xml',
        'sequence/stores.xml',

        # Data

            # Product
            'data/product/group.xml',
            'data/product/sub_group.xml',
            'data/product/uom.xml',
            'data/product/tax.xml',
            'data/product/category.xml',
            'data/product/location.xml',

            # Account
            'data/account/account.xml',

            # Base Pack
            'data/base_pack/base_pack.xml',

        # Views

            # Base Pack
            'views/web_views/base_pack/company.xml',
            'views/web_views/base_pack/users.xml',
            'views/web_views/base_pack/person.xml',
            'views/web_views/base_pack/employee.xml',
            'views/web_views/base_pack/patient.xml',

            # Account
            'views/web_views/account/account.xml',
            'views/web_views/account/year.xml',
            'views/web_views/account/period.xml',

            # Product
            'views/web_views/product/group.xml',
            'views/web_views/product/sub_group.xml',
            'views/web_views/product/uom.xml',
            'views/web_views/product/tax.xml',
            'views/web_views/product/category.xml',
            'views/web_views/product/product.xml',
            'views/web_views/product/location.xml',
            'views/web_views/product/warehouse.xml',

            # Stores
            'views/web_views/stores/stock_adjustment.xml',
            'views/web_views/stores/store_request.xml',
            'views/web_views/stores/store_issue.xml',
            'views/web_views/stores/store_return.xml',
            'views/web_views/stores/store_intake.xml',
            'views/web_views/stores/stock_move.xml',

            # Asserts
            'views/web_views/asserts/asserts_capitalisation.xml',
            'views/web_views/asserts/asserts.xml',
            'views/web_views/asserts/service.xml',
            'views/web_views/asserts/reminder.xml',

            # Hr
            'views/web_views/hr/hr_category.xml',
            'views/web_views/hr/hr_contact.xml',
            'views/web_views/hr/hr_department.xml',
            'views/web_views/hr/hr_designation.xml',
            'views/web_views/hr/hr_experience.xml',
            'views/web_views/hr/hr_qualification.xml',

            # Recruitment
            'views/web_views/recruitment/resume_bank.xml',
            'views/web_views/recruitment/vacancy_position.xml',
            'views/web_views/recruitment/interview_schedule.xml',
            'views/web_views/recruitment/appointment_order.xml',

            # Time Management
            'views/web_views/time_management/shift.xml',
            'views/web_views/time_management/time_configuration.xml',
            'views/web_views/time_management/monthly_attendance.xml',
            'views/web_views/time_management/monthly_attendance_wiz.xml',
            'views/web_views/time_management/week_schedule.xml',
            'views/web_views/time_management/attendance.xml',
            'views/web_views/time_management/time_sheet.xml',
            'views/web_views/time_management/time_sheet_application.xml',

            # Leave Management
            'views/web_views/leave_management/leave.xml',
            'views/web_views/leave_management/comp_off.xml',
            'views/web_views/leave_management/permission.xml',
            'views/web_views/leave_management/leave_account.xml',
            'views/web_views/leave_management/leave_level.xml',
            'views/web_views/leave_management/leave_type.xml',
            'views/web_views/leave_management/leave_configuration.xml',


        # Menu
        'menu/base_pack.xml',
        'menu/account.xml',
        'menu/hr.xml',
        'menu/contact.xml',
        'menu/product.xml',
        'menu/stores.xml',
        'menu/time_management.xml',
        'menu/leave_management.xml',
        'menu/recruitment.xml',
    ],
    "demo": [

    ],
    "qweb": [

    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
