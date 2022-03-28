import re

import KingdaeFunction as KF
import redisFunction as rF
from constFunction import day_mapping
from SqlFunction import generate_key


def get_raw_data(entity_account_dict: dict, order_id: str) -> dict:
    """
    vat only care about CNY balance, therefore the filter excludes other currency, only extract the asst type from
     trial balance and format result dictionary.
    :param entity_account_dict:
    {
        year:
        month:
        data: {
            entity_code:[account_code_list],
        }
    }
    :return:
    {
        year:
        month:
        data: {
            entity_code: {
                account_code: [[balance, asst_type, asst_code]];
                }
        }
    }
    :param order_id:
    """
    result_dict = {'year': entity_account_dict.get('year'),
                   'month': entity_account_dict.get('month'),
                   'data': {}}
    if not entity_account_dict.get('data'):
        return result_dict
    ssid = KF.login_service()
    r = rF.set_redis_connection()
    for entity in entity_account_dict['data']:
        result_dict['data'][entity] = {}
        if entity_account_dict['data'].get(entity):
            if entity_account_dict['data'][entity] is not None:
                r.set(order_id, '正在获取科目余额表： 组织代码-' + entity)
                tb = KF.get_account_balance(entity,
                                            str(entity_account_dict.get('year')),
                                            str(entity_account_dict.get('month')),
                                            ssid)
            else:
                tb = None
            if not tb:
                continue
            for tb_line in tb:
                if tb_line[5] in entity_account_dict['data'][entity] and tb_line[0] == '1' and tb_line[7] == 'BB01':
                    if tb_line[5] not in result_dict['data'][entity]:
                        result_dict['data'][entity][tb_line[5]] = []
                    asst_record_list = [-round(float(tb_line[14]), 2), tb_line[40], tb_line[39]]
                    result_dict['data'][entity][tb_line[5]].append(asst_record_list)
    r.set(order_id, '0000')
    rF.shut_all_redis_connection()
    return result_dict


def build_voucher(entity_account_bal_dict: dict, user_name: str, desc: str) -> list:
    """

    :param entity_account_bal_dict:
    :param user_name:
    :param desc: work order id, this function should build voucher for only one work order
    :return:
    """
    voucher_list = []
    str_year = entity_account_bal_dict.get('year')
    str_month = entity_account_bal_dict.get('month')
    str_date = str(str_year) + '-' + str(str_month) + '-' + str(day_mapping(str_month))
    hq_abs_appendix = '_收缴增值税及附加'
    sub_abs_appendix = '总部收缴增值税及附加'

    # dept voucher:
    for entity in entity_account_bal_dict['data']:
        entry_int = 1
        subtotal = 0
        if not entity_account_bal_dict['data'][entity]:
            continue
        for account in entity_account_bal_dict['data'][entity]:
            if not entity_account_bal_dict['data'][entity][account]:
                continue
            for record in entity_account_bal_dict['data'][entity][account]:
                if record[0] != 0:
                    if record[1] == 'None':
                        voucher_list.append({
                            'companyNumber': entity,
                            'bookedDate': str_date,
                            'bizDate': str_date,
                            'periodYear': str_year,
                            'periodNumber': str_month,
                            'voucherType': '记',
                            'voucherNumber': str(entity) + '结转',
                            'entrySeq': entry_int,
                            'voucherAbstract': sub_abs_appendix,
                            'accountNumber': account,
                            'currencyNumber': 'BB01',
                            'localRate': 1,
                            'entryDC': 1,
                            'originalAmount': round(float(record[0]), 2),
                            'debitAmount': round(float(record[0]), 2),
                            'creditAmount': 0.0,
                            'creator': user_name,
                            'description': desc,
                        })
                        entry_int += 1
                        subtotal += record[0]
                    else:
                        voucher_list.append({
                            'companyNumber': entity,
                            'bookedDate': str_date,
                            'bizDate': str_date,
                            'periodYear': str_year,
                            'periodNumber': str_month,
                            'voucherType': '记',
                            'voucherNumber': str(entity) + '结转',
                            'entrySeq': entry_int,
                            'voucherAbstract': sub_abs_appendix,
                            'accountNumber': account,
                            'currencyNumber': 'BB01',
                            'localRate': 1,
                            'entryDC': 1,
                            'originalAmount': round(float(record[0]), 2),
                            'debitAmount': round(float(record[0]), 2),
                            'creditAmount': 0.0,
                            'creator': user_name,
                            'asstActType1': record[1],
                            'asstActNumber1': record[2],
                            'description': desc,
                        })
                        entry_int += 1
                        subtotal += record[0]
        if subtotal != 0:
            voucher_list.append({
                'companyNumber': entity,
                'bookedDate': str_date,
                'bizDate': str_date,
                'periodYear': str_year,
                'periodNumber': str_month,
                'voucherType': '记',
                'voucherNumber': str(entity) + '结转',
                'entrySeq': entry_int,
                'voucherAbstract': sub_abs_appendix,
                'accountNumber': '1151.08',
                'currencyNumber': 'BB01',
                'localRate': 1,
                'entryDC': -1,
                'originalAmount': round(float(subtotal), 2),
                'debitAmount': 0.0,
                'creditAmount': round(float(subtotal), 2),
                'creator': user_name,
                'asstActType1': '客户',
                'asstActNumber1': 'A001',
                'description': desc,
            })

    # hq voucher:
    entry_int = 1
    chs_name_dict = KF.get_entity_chs_name_dict()
    supplier_dict = KF.get_default_supplier_dict()
    for entity in entity_account_bal_dict['data']:
        subtotal = 0
        if not entity_account_bal_dict['data'][entity]:
            continue
        for account in entity_account_bal_dict['data'][entity]:
            if not entity_account_bal_dict['data'][entity][account]:
                continue
            for record in entity_account_bal_dict['data'][entity][account]:
                if record[0] != 0:
                    voucher_list.append({
                        'companyNumber': '1.01.001',
                        'bookedDate': str_date,
                        'bizDate': str_date,
                        'periodYear': str_year,
                        'periodNumber': str_month,
                        'voucherType': '记',
                        'voucherNumber': '总部结转',
                        'entrySeq': entry_int,
                        'voucherAbstract': chs_name_dict.get(entity) + hq_abs_appendix,
                        'accountNumber': account,
                        'currencyNumber': 'BB01',
                        'localRate': 1,
                        'entryDC': -1,
                        'originalAmount': round(float(record[0]), 2),
                        'debitAmount': 0.0,
                        'creditAmount': round(float(record[0]), 2),
                        'creator': user_name,
                        'description': desc,
                    })
                    entry_int += 1
                    subtotal += record[0]
        if subtotal != 0:
            voucher_list.append({
                'companyNumber': '1.01.001',
                'bookedDate': str_date,
                'bizDate': str_date,
                'periodYear': str_year,
                'periodNumber': str_month,
                'voucherType': '记',
                'voucherNumber': '总部结转',
                'entrySeq': entry_int,
                'voucherAbstract': chs_name_dict.get(entity) + '-' + hq_abs_appendix,
                'accountNumber': '1151.08',
                'currencyNumber': 'BB01',
                'localRate': 1,
                'entryDC': 1,
                'originalAmount': round(float(subtotal), 2),
                'debitAmount': round(float(subtotal), 2),
                'creditAmount': 0.0,
                'creator': user_name,
                'asstActType1': '客户',
                'asstActNumber1': supplier_dict.get(entity),
                'description': desc,
            })
        entry_int += 1
    return voucher_list
