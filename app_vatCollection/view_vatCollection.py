import json
import time

from flask import Blueprint, render_template, request, send_from_directory, redirect, make_response

import constFunction as cF
import securityFunction as sF
import SqlFunction as SqlF
import KingdaeFunction as KF


from app_vatCollection import *
from app_vatCollection import function_vatCollection


@vatCollection.before_request
def vatCollection_auth_check():
    """
    no auth request
    :return:
    """
    cookie_owner = request.cookies.get('owner')
    if not cookie_owner:
        return redirect('/login')
    else:
        cookie_token = request.cookies.get('token')
        if sF.check_cookies(cookie_owner, cookie_token) == 0:
            return None
        else:
            return redirect('/login')


@vatCollection.route('/main')
def main_view():
    """

    :return:
    """
    return render_template('worksheet.html')


@vatCollection.route('/new_vatCollection')
def new_vatCollection():
    return render_template('vatCollection/new_vatCollection.html')


@vatCollection.route('/new')
def new_id():
    id = SqlF.generate_key()
    return redirect('new_vatCollection?workorder_id=' + id)


@vatCollection.route('/vat_submit', methods=['POST'])
def vat_submit():
    json_str = request.form.get('entity_account_dict')
    entity_account_dict = json.loads(json_str)
    user_id = request.cookies.get('owner')
    user_name_session = SqlF.create_session()
    user_name = user_name_session.query(SqlF.tUser.r_chs_name).filter(SqlF.tUser.r_id == user_id).first().r_chs_name
    user_name_session.close()
    order_id = request.form.get('workorder_id')
    order_number = cF.generate_order_number()
    order_date = time.strftime('%Y-%m-%d')
    order_affective_month = entity_account_dict['month']
    if int(order_affective_month) == 1:
        order_affective_month = 12
    else:
        order_affective_month -= 1
    order_keyword = user_name + order_date + '收缴' + str(order_affective_month) + '月增值税'
    doc_status = '1'
    module_id = 'UID5d7a58f22a1e0401049'
    user_name_session.add(SqlF.tWorkOrderMain(**{
        'r_id': order_id,
        'r_number': order_number,
        'r_date': order_date,
        'r_keyword': order_keyword,
        'r_doc_status': doc_status,
        'r_creator': user_id,
        'r_module_id': module_id
    }))
    try:
        user_name_session.commit()
    except Exception as e:
        user_name_session.rollback()
        return render_template('error_page.html')
    result_dict = function_vatCollection.get_raw_data(entity_account_dict, order_id)
    voucher_list = function_vatCollection.build_voucher(result_dict, user_name=user_name, desc=order_id)
    KF.save_vouchers_into_database(voucher_list, work_order_id=order_id)
    # return redirect('/voucherView?workorder_id=' + order_id)
    # return redirect('/processing?workorder_id=' + order_id + '&destination=voucherView')
    user_name_session.close()
    return '0'
