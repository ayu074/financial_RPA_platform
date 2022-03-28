import json
import time

from flask import Blueprint, render_template, request, send_from_directory, redirect, make_response, jsonify

import constFunction as cF
import securityFunction as sF
import SqlFunction as SqlF
import KingdaeFunction as KF


from app_monthlyClosing import *
from app_monthlyClosing import function_monthlyClosing


@monthlyClosing.before_request
def monthlyClosing_auth_check():
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


@monthlyClosing.route('/main')
def main_view():
    """

    :return:
    """
    return render_template('worksheet.html')


@monthlyClosing.route('/get_entity_list')
def get_entity_list():
    owner = request.cookies.get('owner')
    entity_name_dict = {}
    el_session = SqlF.create_session()
    entity_base_record = el_session.query(SqlF.tBaseKdEntity).all()
    for each in entity_base_record:
        entity_name_dict[each.r_id] = (each.r_code, each.r_chs_name)
    closing_entity_list = el_session.query(SqlF.tBaseClosingEntityInfo).filter(
        SqlF.tBaseClosingEntityInfo.r_responsible_user_id.like('%' + owner + '%')
    ).all()
    result_list = []
    for record in closing_entity_list:
        result_list.append({
            'r_id': record.r_id,
            'r_code': entity_name_dict.get(record.r_id)[0],
            'r_chs_name': entity_name_dict.get(record.r_id)[1],
            'r_is_sub': record.r_is_sub,
        })
    return jsonify(result_list)


@monthlyClosing.route('/get_function_list')
def get_function_list():
    entity_id = request.args.get('entity_id')
    fl_session = SqlF.create_session()
    if entity_id:
        f_record = fl_session.query(SqlF.tBaseClosingFunctions).filter(
            SqlF.tBaseClosingFunctions.r_id == SqlF.tBaseClosingEnityFunctionRecon.r_closing_function_id,
            SqlF.tBaseClosingEnityFunctionRecon.r_entity_id == entity_id,
            SqlF.tBaseClosingEnityFunctionRecon.r_available == 0
        ).all()
    else:
        f_record = fl_session.query(SqlF.tBaseClosingFunctions).all()
    fl_session.close()
    result_list = []
    if f_record:
        for record in f_record:
            result_list.append({
                'r_id': record.r_id,
                'r_chs_name': record.r_chs_name,
                'r_key': record.r_pointer_key,
            })
    else:
        result_list.append({
            'r_id': '00x0',
            'r_chs_name': '无',
            'r_key': 'none',
        })
    return jsonify(result_list)


@monthlyClosing.route('/new')
def new_id():
    id = SqlF.generate_key()
    return redirect('new_monthlyClosing?workorder_id=' + id)


@monthlyClosing.route('/new_monthlyClosing')
def new():
    return render_template('monthlyClosing/monthlyClosing.html')


@monthlyClosing.route('/generate_workorder', methods=['POST'])
def generate_workorder():
    workorder_id = request.form.get('workorder_id')
    curr_year = str(request.form.get('select_year'))
    curr_month = str(request.form.get('select_month'))
    order_date = time.strftime('%Y-%m-%d')
    owner = request.cookies.get('owner')
    w_session = SqlF.create_session()
    user_name = w_session.query(SqlF.tUser.r_chs_name).filter(SqlF.tUser.r_id == owner).first()[0]
    module_id = 'UID5d95fe2deeaa4628329'
    abstract = user_name + order_date + '经办' + curr_year + '年' + curr_month + '月结账'
    number = cF.generate_order_number()
    if not w_session.query(SqlF.tWorkOrderMain).filter(SqlF.tWorkOrderMain.r_id == workorder_id).first():
        w_session.add(SqlF.tWorkOrderMain(**{
            'r_id': workorder_id,
            'r_number': number,
            'r_date': order_date,
            'r_keyword': abstract,
            'r_doc_status': '1',
            'r_creator': owner,
            'r_module_id': module_id
        }))
        w_session.commit()
        w_session.close()


@monthlyClosing.route('/build_voucher', methods=['POST'])
def build_voucher():
    try:
        workorder_id = request.form.get('workorder_id')
        entity_id = request.form.get('entity_id')
        curr_year = str(request.form.get('select_year'))
        curr_month = str(request.form.get('select_month'))
        function_id_list = str(request.form.get('func_list_str')).split(';')[:-1]
        function_sorting_list = []
        owner = request.cookies.get('owner')
        get_tb_session = SqlF.create_session()
        for func in function_id_list:
            func_record = get_tb_session.query(SqlF.tBaseClosingFunctions).filter(
                SqlF.tBaseClosingFunctions.r_id == func
            ).first()
            if not function_sorting_list:
                function_sorting_list.append(func_record)
                continue
            for i, exsit_func in enumerate(function_sorting_list):
                if int(func_record.r_priority) <= int(exsit_func.r_priority):
                    function_sorting_list.insert(i, func_record)
                    break
        entity_code = get_tb_session.query(SqlF.tBaseKdEntity.r_code).filter(SqlF.tBaseKdEntity.r_id == entity_id).first()[0]
        ssid = KF.login_service()
        curr_entity_tb_record_list = KF.TB(KF.get_account_balance(entity_code, curr_year, curr_month, ssid))
        user_name = get_tb_session.query(SqlF.tUser.r_chs_name).filter(SqlF.tUser.r_id == owner).first()[0]
        for func in function_sorting_list:
            avail = get_tb_session.query(SqlF.tBaseClosingEnityFunctionRecon).filter(
                SqlF.tBaseClosingEnityFunctionRecon.r_entity_id == entity_id,
                SqlF.tBaseClosingEnityFunctionRecon.r_closing_function_id == func.r_id
            ).first()
            if avail.r_available == 0:
                lambda_function = eval('function_monthlyClosing.' + str(func.r_pointer_key))
                lambda_function(curr_entity_tb_record_list, workorder_id, user_name)
                time.sleep(0.5)
        return '0'
    except Exception as e:
        print(e)
        return '1'
