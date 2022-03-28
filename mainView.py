import os
import pickle
import re
import time
import traceback

from flask import Blueprint, render_template, request, send_from_directory, redirect, make_response, jsonify

import constFunction as cF
import redisFunction as rF
import securityFunction as sF
import SqlFunction as SqlF
import KingdaeFunction as KD


mainView = Blueprint('mainView', __name__)


@mainView.route('/')
def home():
    return render_template('home.html')


@mainView.route('/getUserName')
def get_user_name(local_user_id=None):
    if local_user_id is None:
        user_id = request.args.get('owner')
    else:
        user_id = local_user_id
    if user_id:
        user_name_session = SqlF.create_session()
        user_name = user_name_session.query(SqlF.tUser.r_chs_name).filter(SqlF.tUser.r_id == user_id).first().r_chs_name
        user_name_session.close()
        return user_name
    else:
        return None


@mainView.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@mainView.route('/login_check', methods=['GET', 'POST'])
def login_check():
    if request.method == 'POST':
        user_name = request.form.get('username')
        pwd = request.form.get('pwd')
        auto_login = request.form.get('auto_login')
        ip = request.remote_addr
        user_id_session = SqlF.create_session()
        user_id = user_id_session.query(SqlF.tUser.r_id).filter(SqlF.tUser.r_name == user_name).first()[0]
        user_id_session.close()
        pwd_checked = sF.check_pwd(raw_password=pwd, user_id=user_id)
        if pwd_checked == 0:
            resp = make_response(redirect('/'))
            if auto_login == 'True':
                sF.set_auto_login(ip, user_id)
            curr_cookies = sF.generate_cookies(user_id)
            resp.set_cookie('owner', user_id)
            resp.set_cookie('token', curr_cookies)
            return resp
        else:
            return redirect('/login')


@mainView.before_request
def check_auto_login_status():
    cookie_owner = request.cookies.get('owner')
    if not cookie_owner:
        ip = request.remote_addr
        path = request.path
        user_id = sF.get_auto_login_owner(ip)
        if user_id:
            curr_cookie = sF.generate_cookies(user_id)
            resp = make_response(redirect(path))
            resp.set_cookie('owner', user_id)
            resp.set_cookie('token', curr_cookie)
            return resp
    return None


@mainView.route('/change_pwd')
def change_pwd_view():
    return render_template('change_pwd.html', success='0')


@mainView.route('/change_pwd_submit', methods=['POST'])
def change_pwd_submit():
    if request.method == 'POST':
        old_pwd = request.form.get('old_pwd')
        new_pwd = request.form.get('new_pwd')
        user_id = request.form.get('user_id')
        try:
            if sF.check_pwd(old_pwd, user_id) == 0:
                result = sF.update_pwd(new_pwd, user_id)
                if result == 0:
                    return render_template('home.html')
                else:
                    return render_template('change_pwd.html', success='9')
            else:
                return render_template('change_pwd.html', success='1')
        except Exception as e:
            return render_template('change_pwd.html', success='9')


@mainView.route('/logout')
def log_out():
    ip = request.remote_addr
    sF.clean_auto_login(ip)
    resp = make_response(redirect('/login'))
    resp.delete_cookie('owner')
    resp.delete_cookie('token')
    return resp


@mainView.route('/getWorkOrderData/')
def get_work_order_data():
    """
    检查cookie确认权限
    根据用户id
    封装
    :return:
    """
    user_id = request.cookies.get('owner')
    user_name = get_user_name(local_user_id=user_id)
    module_name = request.args.get('module')
    work_order_session = SqlF.create_session()
    work_order_list = work_order_session.query(SqlF.tWorkOrderMain).filter(
        SqlF.tWorkOrderMain.r_creator == user_id,
        SqlF.tWorkOrderMain.r_module_id == SqlF.tModule.r_id,
        SqlF.tModule.r_code == str(module_name)
    ).order_by(SqlF.tWorkOrderMain.r_number.desc()).all()
    result_list = []
    for each in work_order_list:
        result_list.append({
            'r_id': each.r_id,
            'r_number': each.r_number,
            'r_date': each.r_date,
            'r_keyword': each.r_keyword,
            'r_doc_status': each.r_doc_status,
            'r_creator': user_name,
        })
    work_order_session.close()
    return jsonify(result_list)


@mainView.route('/voucherView')
def voucher_view():
    """
    parse args and return template
    :return:
    """
    voucher_session = SqlF.create_session()
    workorder_id = request.args.get('workorder_id')
    voucher_id = request.args.get('voucher_id')
    user_id = request.cookies.get('owner')
    if voucher_id:
        owner_id = voucher_session.query(SqlF.tWorkOrderMain.r_creator).filter(
            SqlF.tVoucher.r_id == voucher_id,
            SqlF.tWorkOrderMain.r_id == SqlF.tVoucher.r_work_order_id
        ).first()
    elif workorder_id:
        owner_id = voucher_session.query(SqlF.tWorkOrderMain.r_creator).filter(
            SqlF.tWorkOrderMain.r_id == workorder_id
        ).first()
    else:
        owner_id = 'N'
    # check auth:
    if sF.viewer_auth_check(user_id) != 0:
        if user_id != owner_id[0]:
            voucher_session.close()
            return render_template('login.html')
    voucher_session.close()
    return render_template('voucher_view.html')


@mainView.route('/getVoucherData', methods=['POST'])
def get_voucher_data():
    """
    only consider the situation when the function will be call by browser, using post
    no extra auth check performed due to browser has already checked
    get actual voucher data
    filter user id and order/voucher id, these two args are compulsory
    :return:
    """
    voucher_session = SqlF.create_session()
    workorder_id = request.form.get('workorder_id')
    voucher_id = request.form.get('voucher_id')
    if workorder_id:
        voucher_list = voucher_session.query(SqlF.tVoucher).filter(
            SqlF.tVoucher.r_work_order_id == workorder_id,
        ).all()
    elif voucher_id:
        voucher_list = voucher_session.query(SqlF.tVoucher).filter(
            SqlF.tVoucher.r_id == voucher_id
        ).all()
    else:
        voucher_list = []
    return_voucher_list = []
    if voucher_list:
        entity_name_dict = KD.get_entity_chs_name_dict()
        for voucher in voucher_list:
            return_voucher_line = {
                'r_id': voucher.r_id,
                'r_work_order_id': voucher.r_work_order_id,
                'r_sys_voucher_number': voucher.r_sys_voucher_number,
                'r_kd_voucher_number': voucher.r_kd_voucher_number,
                'r_entity_code': voucher.r_entity_code,
                'r_abstract': voucher.r_abstract,
                'r_year': voucher.r_year,
                'r_month': voucher.r_month,
                'r_type': voucher.r_type,
                'r_debit_total': float(voucher.r_debit_total),
                'r_credit_total': float(voucher.r_credit_total),
                'r_import_result': voucher.r_import_result,
                'r_description': voucher.r_description,
                'r_entity_chs_name': entity_name_dict.get(voucher.r_entity_code),
            }
            return_voucher_list.append(return_voucher_line)
    voucher_session.close()
    return jsonify(return_voucher_list)


@mainView.route('/getEntryData', methods=['POST'])
def get_entry_data():
    entry_session = SqlF.create_session()
    workorder_id = request.form.get('workorder_id')
    voucher_id = request.form.get('voucher_id')
    if workorder_id:
        entry_list = entry_session.query(SqlF.tEntry).filter(
            SqlF.tEntry.r_voucher_id == SqlF.tVoucher.r_id,
            SqlF.tVoucher.r_work_order_id == workorder_id,
        ).all()
    elif voucher_id:
        entry_list = entry_session.query(SqlF.tEntry).filter(
            SqlF.tEntry.r_voucher_id == voucher_id
        ).all()
    else:
        entry_list = []
    return_entry_list = []
    if entry_list:
        entity_name_dict = KD.get_entity_chs_name_dict()
        account_name_dict = KD.get_account_full_name_dict(entity_code=entry_list[0].r_companyNumber)
        for entry in entry_list:
            return_entry_line = {
                'r_id': entry.r_id,
                'r_voucher_id': entry.r_voucher_id,
                'r_companyNumber': entry.r_companyNumber,
                'r_bookedDate': entry.r_bookedDate,
                'r_bizDate': entry.r_bizDate,
                'r_periodYear': entry.r_periodYear,
                'r_periodNumber': entry.r_periodNumber,
                'r_voucherType': entry.r_voucherType,
                'r_voucherNumber': entry.r_voucherNumber,
                'r_entrySeq': entry.r_entrySeq,
                'r_voucherAbstract': entry.r_voucherAbstract,
                'r_accountNumber': entry.r_accountNumber,
                'r_currencyNumber': entry.r_currencyNumber,
                'r_localRate': float(entry.r_localRate),
                'r_entryDC': entry.r_entryDC,
                'r_originalAmount': float(entry.r_originalAmount),
                'r_debitAmount': float(entry.r_debitAmount),
                'r_creditAmount': float(entry.r_creditAmount),
                'r_creator': entry.r_creator,
                'r_description': entry.r_description,
                'r_asstActType1': entry.r_asstActType1,
                'r_asstActNumber1': entry.r_asstActNumber1,
                'r_asstActType2': entry.r_asstActType2,
                'r_asstActNumber2': entry.r_asstActNumber2,
                'r_entity_chs_name': entity_name_dict.get(entry.r_companyNumber),
                'r_account_chs_name': account_name_dict.get(entry.r_accountNumber),
            }
            return_entry_list.append(return_entry_line)
    entry_session.close()
    return jsonify(return_entry_list)


@mainView.route('/processing')
def processing():
    return render_template('status_view.html')


@mainView.route('/get_process_status')
def get_process_status():
    work_id = request.args.get('workorder_id')
    r = rF.set_redis_connection()
    status_str = r.get(work_id)
    if not status_str:
        status_str = '开始处理单据，请稍后……'
    print(status_str)
    return status_str


@mainView.route('/importVoucher', methods=['POST'])
def import_voucher_post():
    """
    using post to eliminate the risk of direct key url in browser
    import one voucher at a time, front end should use ajax to update voucher info
    work flow:
    1 - reading the args to determine which voucher to import
    2 - examine each voucher status to see if is ready to import
    3 - import and record result
    :return: import result in string
    """
    voucher_id = request.form.get('voucher_id')
    voucher_import_session = SqlF.create_session()
    voucher_status = voucher_import_session.query(SqlF.tVoucher.r_kd_voucher_number).filter(
        SqlF.tVoucher.r_id == voucher_id
    ).first()
    if voucher_status[0] is not None:
        return str(voucher_status[0])
    ssid = KD.login_service()
    result_dict = KD.import_voucher_by_id(voucher_id=voucher_id, ssid=ssid)
    return jsonify(result_dict)


@mainView.route('/deleteVoucher', methods=['POST'])
def delete_voucher_post():
    voucher_id = request.form.get('voucher_id')
    delete_session = SqlF.create_session()
    voucher_info = delete_session.query(SqlF.tVoucher).filter(
        SqlF.tVoucher.r_id == voucher_id
    ).first()
    if voucher_info.r_is_deleted != 0 and voucher_info.r_kd_voucher_number:
        ssid = KD.login_service()
        result = KD.delete_voucher(entity_code=voucher_info.r_entity_code,
                                   period='.'.join([str(int(voucher_info.r_year)), str(int(voucher_info.r_month))]),
                                   voucher_number=voucher_info.r_kd_voucher_number,
                                   desc=voucher_info.r_description,
                                   ssid=ssid)
        if int(result) == 0:
            delete_session.query(SqlF.tVoucher).filter(SqlF.tVoucher.r_id == voucher_id).update({
                SqlF.tVoucher.r_is_deleted == 0
            })
            delete_session.commit()
        return str(result)
    else:
        return '-2'


@mainView.route('/exportVoucher')
def export_voucher():
    """
    not key function, allow to use get method
    :return:
    """
    entry_session = SqlF.create_session()
    workorder_id = request.args.get('workorder_id')
    voucher_id = request.args.get('voucher_id')
    if workorder_id:
        entry_list = entry_session.query(SqlF.tEntry).filter(
            SqlF.tEntry.r_voucher_id == SqlF.tVoucher.r_id,
            SqlF.tVoucher.r_work_order_id == workorder_id,
        ).all()
    elif voucher_id:
        entry_list = entry_session.query(SqlF.tEntry).filter(
            SqlF.tEntry.r_voucher_id == voucher_id
        ).all()
    else:
        entry_list = []
    return_entry_list = []
    if entry_list:
        for entry in entry_list:
            return_entry_line = {
                'id': entry.r_id,
                'voucher_id': entry.r_voucher_id,
                'companyNumber': entry.r_companyNumber,
                'bookedDate': entry.r_bookedDate,
                'bizDate': entry.r_bizDate,
                'periodYear': entry.r_periodYear,
                'periodNumber': entry.r_periodNumber,
                'voucherType': entry.r_voucherType,
                'voucherNumber': entry.r_voucherNumber,
                'entrySeq': entry.r_entrySeq,
                'voucherAbstract': entry.r_voucherAbstract,
                'accountNumber': entry.r_accountNumber,
                'currencyNumber': entry.r_currencyNumber,
                'localRate': float(entry.r_localRate),
                'entryDC': entry.r_entryDC,
                'originalAmount': float(entry.r_originalAmount),
                'debitAmount': float(entry.r_debitAmount),
                'creditAmount': float(entry.r_creditAmount),
                'creator': entry.r_creator,
                'description': entry.r_description,
                'asstActType1': entry.r_asstActType1,
                'asstActNumber1': entry.r_asstActNumber1,
                'asstActType2': entry.r_asstActType2,
                'asstActNumber2': entry.r_asstActNumber2,
            }
            return_entry_list.append(return_entry_line)
    entry_session.close()
    temp_file_name = str(time.time()).replace('.', '')
    temp_file_folder = cF.AbsPath_Folder + 'temp_delivery'
    KD.export_to_excel(voucher_list=return_entry_list, file_name_without_tail=temp_file_folder + '\\' + temp_file_name)
    return send_from_directory(temp_file_folder, temp_file_name + '.xlsx', as_attachment=True)


@mainView.route('/getModule')
def get_module():
    module_session = SqlF.create_session()
    module_records = module_session.query(SqlF.tModule).all()
    result_list = []
    for record in module_records:
        result_list.append({
            'id': record.r_id,
            'name': record.r_name,
            'desc': record.r_desc,
            'url': str(record.r_url_prefix) + '/main',
            'img_locale': record.r_img_locale
        })
    return jsonify(result_list)


if __name__ == '__main__':
    pass