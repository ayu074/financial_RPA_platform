import re
import sys
import pickle

import KingdaeFunction as KF
import constFunction

from SqlFunction import *


def voucher_vat_separation(tb_obj: KF.TB, workorder_id: str, user_name: str) -> list:
    selling_vat_account = '2221.07.03.01'
    closing_month = tb_obj.record_list[0].month
    closing_year = tb_obj.record_list[0].year
    closing_day = constFunction.day_mapping(closing_month)
    closing_date_str = '-'.join([str(closing_year), str(closing_month), str(closing_day)])
    sub_voucher_list = []
    sub_voucher_session = create_session()
    entity_gen_info_record = sub_voucher_session.query(tBaseKdEntity).filter(
        tBaseKdEntity.r_code == str(tb_obj.record_list[0].entity_code)
    ).first()
    closing_entity_info_record = sub_voucher_session.query(tBaseClosingEntityInfo).filter(
        tBaseClosingEntityInfo.r_id == tBaseKdEntity.r_id,
        tBaseKdEntity.r_code == str(tb_obj.record_list[0].entity_code)
    ).first()
    vat_separation_acc_record = sub_voucher_session.query(
        tBaseClosingSmallTaxeeArgs
    ).filter(tBaseClosingSmallTaxeeArgs.r_is_separation_acc == 0).all()
    vat_separation_acc_list = []
    for each in vat_separation_acc_record:
        vat_separation_acc_list.append(each.r_account_code)

    # hq dept does not apply this function
    # todo: update filter
    # not small taxee:
    if int(closing_entity_info_record.r_is_small) != 0:
        normal_vat_rate = float(sub_voucher_session.query(tBaseClosingArgs.r_value).filter(
            tBaseClosingArgs.r_code == 'genVAT'
        ).first()[0])
        for record in tb_obj.record_list:
            if (record.balance_type == '1'
                    and record.account_code in vat_separation_acc_list
                    and float(record.period_pl_local_currency) != 0.0
                    and record.currency_code == 'GLC'
                    and tb_obj.is_leaf_account(record.account_code)):
                tax_local = round((float(record.period_pl_local_currency) / (1 + normal_vat_rate)) * normal_vat_rate, 2)
                if record.has_asst == '0':
                    sub_voucher_list.append({
                        'companyNumber': record.entity_code,
                        'bookedDate': closing_date_str,
                        'bizDate': closing_date_str,
                        'periodYear': str(closing_year),
                        'periodNumber': str(closing_month),
                        'voucherType': '记',
                        'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月价税分离',
                        'entrySeq': len(sub_voucher_list) + 1,
                        'voucherAbstract': '价税分离',
                        'accountNumber': record.account_code,
                        'currencyNumber': 'BB01',
                        'entryDC': -1,
                        'originalAmount': -tax_local,
                        'debitAmount': 0.0,
                        'creditAmount': -tax_local,
                        'creator': user_name,
                        'description': workorder_id,
                    })
                    sub_voucher_list.append({
                        'companyNumber': record.entity_code,
                        'bookedDate': closing_date_str,
                        'bizDate': closing_date_str,
                        'periodYear': str(closing_year),
                        'periodNumber': str(closing_month),
                        'voucherType': '记',
                        'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月价税分离',
                        'entrySeq': len(sub_voucher_list) + 1,
                        'voucherAbstract': '价税分离',
                        'accountNumber': selling_vat_account,
                        'currencyNumber': 'BB01',
                        'entryDC': -1,
                        'originalAmount': tax_local,
                        'debitAmount': 0.0,
                        'creditAmount': tax_local,
                        'creator': user_name,
                        'description': workorder_id,
                    })
                else:
                    curr_asst_tb_obj = tb_obj.get_asst_tb(record.account_code)
                    for asst_record in curr_asst_tb_obj.asst_list:
                        if (asst_record.balance_type == '1'
                                and float(asst_record.period_pl_ori_currency) != 0.0
                                and asst_record.currency_code == 'GLC'):
                            tax_local = round((float(asst_record.period_pl_local_currency) / (1 + normal_vat_rate)) * normal_vat_rate, 2)
                            sub_voucher_list.append({
                                'companyNumber': record.entity_code,
                                'bookedDate': closing_date_str,
                                'bizDate': closing_date_str,
                                'periodYear': str(closing_year),
                                'periodNumber': str(closing_month),
                                'voucherType': '记',
                                'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月价税分离',
                                'entrySeq': len(sub_voucher_list) + 1,
                                'voucherAbstract': '价税分离',
                                'accountNumber': record.account_code,
                                'currencyNumber': 'BB01',
                                'entryDC': -1,
                                'originalAmount': -tax_local,
                                'debitAmount': 0.0,
                                'creditAmount': -tax_local,
                                'creator': user_name,
                                'description': workorder_id,
                                'asstActType1': asst_record.asst_type1,
                                'asstActNumber1': asst_record.asst_code1,
                                'asstActType2': asst_record.asst_type2,
                                'asstActNumber2': asst_record.asst_code2,
                            })
                            sub_voucher_list.append({
                                'companyNumber': record.entity_code,
                                'bookedDate': closing_date_str,
                                'bizDate': closing_date_str,
                                'periodYear': str(closing_year),
                                'periodNumber': str(closing_month),
                                'voucherType': '记',
                                'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月价税分离',
                                'entrySeq': len(sub_voucher_list) + 1,
                                'voucherAbstract': '价税分离',
                                'accountNumber': selling_vat_account,
                                'currencyNumber': 'BB01',
                                'entryDC': -1,
                                'originalAmount': tax_local,
                                'debitAmount': 0.0,
                                'creditAmount': tax_local,
                                'creator': user_name,
                                'description': workorder_id,
                            })
    # small taxee in season end:
    elif int(tb_obj.record_list[0].month) in (3, 6, 9, 12):
        # base information prepared
        seasonal_rev_total = tb_obj.get_small_taxee_revenue_total(allow_online_update=False)
        small_taxee_threshold = float(sub_voucher_session.query(tBaseClosingArgs.r_value).filter(
            tBaseClosingArgs.r_code == 'smallVATThreshold'
        ).first()[0])
        if seasonal_rev_total >= small_taxee_threshold:
            tax_record = sub_voucher_session.query(tBaseClosingArgs).filter(
                tBaseClosingArgs.r_code == 'smallTaxRate'
            ).first()[0]
            cal_record = sub_voucher_session.query(tBaseClosingArgs).filter(
                tBaseClosingArgs.r_code == 'smallCalTaxNormal'
            ).first()[0]
        else:
            tax_record = sub_voucher_session.query(tBaseClosingArgs).filter(
                tBaseClosingArgs.r_code == 'smallTaxRate'
            ).first()[0]
            cal_record = sub_voucher_session.query(tBaseClosingArgs).filter(
                tBaseClosingArgs.r_code == 'smallCalTaxDiscount'
            ).first()[0]

        # build voucher
        for record in tb_obj.record_list:
            if (record.balance_type == '1'
                    and record.currency_code == 'GLC'
                    and record.account_code in vat_separation_acc_list
                    and tb_obj.is_leaf_account(record.account_code)):
                bal_dict = tb_obj.get_small_taxee_revenue_record(record.account_code)
                if bal_dict:
                    for asst_code in bal_dict:
                        if bal_dict[asst_code] != 0:
                            tax_local = round(bal_dict[asst_code] / (1 + float(tax_record.r_value))
                                              * float(cal_record.r_value), 2)
                            sub_voucher_list.append({
                                'companyNumber': record.entity_code,
                                'bookedDate': closing_date_str,
                                'bizDate': closing_date_str,
                                'periodYear': str(closing_year),
                                'periodNumber': str(closing_month),
                                'voucherType': '记',
                                'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月价税分离',
                                'entrySeq': len(sub_voucher_list) + 1,
                                'voucherAbstract': '价税分离',
                                'accountNumber': record.account_code,
                                'currencyNumber': 'BB01',
                                'entryDC': -1,
                                'originalAmount': -tax_local,
                                'debitAmount': 0.0,
                                'creditAmount': -tax_local,
                                'creator': user_name,
                                'description': workorder_id,
                                'asstActType1': None if asst_code == 'None' else tb_obj.guess_asst_type(asst_code),
                                'asstActNumber1': None if asst_code == 'None' else asst_code,
                            })
                            sub_voucher_list.append({
                                'companyNumber': record.entity_code,
                                'bookedDate': closing_date_str,
                                'bizDate': closing_date_str,
                                'periodYear': str(closing_year),
                                'periodNumber': str(closing_month),
                                'voucherType': '记',
                                'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月价税分离',
                                'entrySeq': len(sub_voucher_list) + 1,
                                'voucherAbstract': '价税分离',
                                'accountNumber': cal_record.r_desc,
                                'currencyNumber': 'BB01',
                                'entryDC': -1,
                                'originalAmount': tax_local,
                                'debitAmount': 0.0,
                                'creditAmount': tax_local,
                                'creator': user_name,
                                'description': workorder_id,
                            })
        


    sub_voucher_session.close()
    KF.save_voucher_into_database(sub_voucher_list, workorder_id)
    return sub_voucher_list


def voucher_vat_collection(tb_obj: KF.TB, workorder_id: str, user_name: str) -> list:
    sub_voucher_list = []
    closing_month = tb_obj.record_list[0].month
    closing_year = tb_obj.record_list[0].year
    closing_day = constFunction.day_mapping(closing_month)
    closing_date_str = '-'.join([str(closing_year), str(closing_month), str(closing_day)])
    sub_voucher_session = create_session()
    entity_gen_info_record = sub_voucher_session.query(tBaseKdEntity).filter(
        tBaseKdEntity.r_code == str(tb_obj.record_list[0].entity_code)
    ).first()
    entity_closing_info_record = sub_voucher_session.query(tBaseClosingEntityInfo).filter(
        tBaseClosingEntityInfo.r_id == str(tb_obj.record_list[0].entity_code)
    )
    vat_acc_list = str(sub_voucher_session.query(tBaseClosingArgs.r_desc).filter(
        tBaseClosingArgs.r_code == 'vatCollectionAcc'
    ).first()[0]).split(';')
    vat_collection_dict = {}
    for each in vat_acc_list:
        vat_collection_dict[each] = 0

    # check current workorder to see if there is any new vat value
    local_voucher_record_list = sub_voucher_session.query(tEntry).filter(
        tVoucher.r_work_order_id == str(workorder_id),
        tEntry.r_voucher_id == tVoucher.r_id
    ).all()
    for entry in local_voucher_record_list:
        if entry.r_accountNumber in vat_collection_dict:
            vat_collection_dict[entry.r_accountNumber] -= round(float(entry.r_creditAmount), 2)
            vat_collection_dict[entry.r_accountNumber] += round(float(entry.r_debitAmount), 2)

    # check current tb:
    for record in tb_obj.record_list:
        if (record.account_code in vat_collection_dict
                and record.balance_type == '1'
                and record.currency_code == 'BB01'):
            vat_collection_dict[record.account_code] += round(float(record.end_balance_local_currency), 2)

    # build voucher:
    sub_total = 0
    for acc in vat_collection_dict:
        if vat_collection_dict[acc] != 0:
            sub_voucher_list.append({
                'companyNumber': entity_gen_info_record.r_code,
                'bookedDate': closing_date_str,
                'bizDate': closing_date_str,
                'periodYear': str(closing_year),
                'periodNumber': str(closing_month),
                'voucherType': '记',
                'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月增值税结转',
                'entrySeq': len(sub_voucher_list) + 1,
                'voucherAbstract': '增值税结转',
                'accountNumber': acc,
                'currencyNumber': 'BB01',
                'entryDC': 1 if vat_collection_dict[acc] < 0 else -1,
                'originalAmount': abs(vat_collection_dict[acc]),
                'debitAmount': abs(vat_collection_dict[acc]) if abs(vat_collection_dict[acc]) < 0 else 0.0,
                'creditAmount': abs(vat_collection_dict[acc]) if abs(vat_collection_dict[acc]) > 0 else 0.0,
                'creator': user_name,
                'description': workorder_id,
            })
            sub_total += vat_collection_dict[acc]
    if sub_total != 0:
        sub_voucher_list.append({
            'companyNumber': entity_gen_info_record.r_code,
            'bookedDate': closing_date_str,
            'bizDate': closing_date_str,
            'periodYear': str(closing_year),
            'periodNumber': str(closing_month),
            'voucherType': '记',
            'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月增值税结转',
            'entrySeq': len(sub_voucher_list) + 1,
            'voucherAbstract': '增值税结转',
            'accountNumber': '2221.07.05',
            'currencyNumber': 'BB01',
            'entryDC': 1 if sub_total > 0 else -1,
            'originalAmount': abs(sub_total),
            'debitAmount': abs(sub_total) if sub_total > 0 else 0,
            'creditAmount': abs(sub_total) if sub_total < 0 else 0,
            'creator': user_name,
            'description': workorder_id,
        })
        if (entity_closing_info_record.r_is_sub != 0
                or entity_closing_info_record.r_is_collected == 0
                or sub_total < 0):
            sub_voucher_list.append({
                'companyNumber': entity_gen_info_record.r_code,
                'bookedDate': closing_date_str,
                'bizDate': closing_date_str,
                'periodYear': str(closing_year),
                'periodNumber': str(closing_month),
                'voucherType': '记',
                'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月增值税结转',
                'entrySeq': len(sub_voucher_list) + 1,
                'voucherAbstract': '增值税结转',
                'accountNumber': '2221.07.05',
                'currencyNumber': 'BB01',
                'entryDC': 1 if sub_total < 0 else -1,
                'originalAmount': abs(sub_total),
                'debitAmount': abs(sub_total) if sub_total < 0 else 0,
                'creditAmount': abs(sub_total) if sub_total > 0 else 0,
                'creator': user_name,
                'description': workorder_id,
            })
            sub_voucher_list.append({
                'companyNumber': entity_gen_info_record.r_code,
                'bookedDate': closing_date_str,
                'bizDate': closing_date_str,
                'periodYear': str(closing_year),
                'periodNumber': str(closing_month),
                'voucherType': '记',
                'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月增值税结转',
                'entrySeq': len(sub_voucher_list) + 1,
                'voucherAbstract': '增值税结转',
                'accountNumber': '2221.08.01',
                'currencyNumber': 'BB01',
                'entryDC': 1 if sub_total > 0 else -1,
                'originalAmount': abs(sub_total),
                'debitAmount': abs(sub_total) if sub_total > 0 else 0,
                'creditAmount': abs(sub_total) if sub_total < 0 else 0,
                'creator': user_name,
                'description': workorder_id,
            })
    sub_voucher_session.close()
    KF.save_voucher_into_database(sub_voucher_list, workorder_id)
    return sub_voucher_list


def voucher_labour_union_fee(tb_obj: KF.TB, workorder_id: str, user_name: str) -> list:
    sub_voucher_list = []
    closing_month = tb_obj.record_list[0].month
    closing_year = tb_obj.record_list[0].year
    closing_day = constFunction.day_mapping(closing_month)
    closing_date_str = '-'.join([str(closing_year), str(closing_month), str(closing_day)])
    sub_voucher_session = create_session()
    entity_gen_info_record = sub_voucher_session.query(tBaseKdEntity).filter(
        tBaseKdEntity.r_code == str(tb_obj.record_list[0].entity_code)
    ).first()
    labor_union_accrual_record = sub_voucher_session.query(tBaseClosingArgs).filter(
        tBaseClosingArgs.r_code == 'genLabourUnionRate'
    ).first()
    labor_union_commit_record = sub_voucher_session.query(tBaseClosingArgs).filter(
        tBaseClosingArgs.r_code == 'genLabourUnionCommitRate'
    ).first()
    union_fee_acc = '6602.03'  # need to determine if the entity has asst
    payroll_dict = {}
    for acc in str(labor_union_accrual_record.r_desc).split(';'):
        payroll_dict[acc] = {}

    # check local entries to update base and result
    local_voucher_record = sub_voucher_session.query(tEntry).filter(
        tEntry.r_voucher_id == tVoucher.r_id,
        tVoucher.r_work_order_id == str(workorder_id)
    ).all()
    for entry_record in local_voucher_record:
        if entry_record.r_accountNumber in payroll_dict:
            if not payroll_dict[entry_record.r_accountNumber].get(entry_record.r_asstActNumber1):
                payroll_dict[entry_record.r_accountNumber][entry_record.r_asstActNumber1] = 0
            payroll_dict[entry_record.r_accountNumber][entry_record.r_asstActNumber1] += float(entry_record.r_originalAmount) * int(entry_record.r_entryDC)  # 借正贷负

    # check tb to update base
    for record in tb_obj.record_list:
        if (record.balance_type == '1'
                and record.account_code in payroll_dict
                and record.currency_code == 'BB01'
                and tb_obj.is_leaf_account(record.account_code)):
            if record.has_asst == '0':
                if not payroll_dict[record.account_code].get('None'):
                    payroll_dict[record.account_code]['None'] = 0
                payroll_dict[record.account_code]['None'] += float(record.period_pl_local_currency)
            else:
                asst_bal = tb_obj.get_asst_tb(record.account_code)
                for each in asst_bal.asst_list:
                    if (each.balance_type == '1'
                            and each.currency_code == 'BB01'):
                        if not payroll_dict[record.account_code].get(each.asst_code1):
                            payroll_dict[record.account_code][each.asst_code1] = 0
                        payroll_dict[record.account_code][each.asst_code1] += float(each.period_pl_local_currency)

    # check tb to build result dict
    result_bal_dict = {}
    current_union_fee_dict = {}
    for record in tb_obj.record_list:
        if (record.balance_type == '1'
                and record.account_code == union_fee_acc
                and record.currency_code == 'GLC'):
            if record.has_asst == '0':
                result_bal_dict = {'None': 0}
                current_union_fee_dict['None'] = float(record.period_pl_local_currency)
                break
            else:
                asst_bal = tb_obj.get_asst_tb(union_fee_acc)
                for each in asst_bal.asst_list:
                    if each.balance_type == '1' and each.currency_code == 'BB01':
                        result_bal_dict[each.asst_code1] = 0
                        current_union_fee_dict[each.asst_code1] = float(each.period_pl_local_currency)
                break
    if not result_bal_dict:
        acc_info = KF.get_account_asst_type(entity_code=tb_obj.record_list[0].entity_code,
                                            account_number=union_fee_acc)
        if not acc_info:
            result_bal_dict = {'None': 0}
            current_union_fee_dict = {'None': 0}
        else:
            for each in acc_info:
                result_bal_dict[each] = 0
                current_union_fee_dict[each] = 0

    # calculate union fee
    for account in payroll_dict:
        for asst in payroll_dict[account]:
            if asst in result_bal_dict:
                result_bal_dict[asst] += round(float(payroll_dict[account][asst]) * float(labor_union_accrual_record.r_value), 2)
            elif 'None' in result_bal_dict:
                result_bal_dict['None'] += round(float(payroll_dict[account][asst]) * float(labor_union_accrual_record.r_value), 2)
            else:
                # random pick one asst
                result_bal_dict[list(result_bal_dict.keys())[0]] += round(float(payroll_dict[account][asst]) * float(labor_union_accrual_record.r_value), 2)
    for key in current_union_fee_dict:
        result_bal_dict[key] -= current_union_fee_dict[key]

    # build voucher:
    # account 2211.05 has different asst type, need to determine first
    union_fee_lia_acc = '2211.05'
    union_fee_lia_asst_type = KF.get_account_asst_type(entity_code=entity_gen_info_record.r_code,
                                                       account_number=union_fee_lia_acc)
    union_fee_lia_asst_code = None
    if union_fee_lia_asst_type != 'None':
        try:
            if union_fee_lia_asst_type == '供应商':
                union_fee_lia_asst_code = KF.get_default_supplier_dict()[entity_gen_info_record.r_code]
            elif union_fee_lia_asst_type == '成本中心':
                union_fee_lia_asst_code = KF.get_default_cost_center_dict()[entity_gen_info_record.r_code]
        except Exception:
            pass
    else:
        union_fee_lia_asst_type = None
    for asst in result_bal_dict:
        if 'None' == asst:
            sub_voucher_list.append({
                'companyNumber': entity_gen_info_record.r_code,
                'bookedDate': closing_date_str,
                'bizDate': closing_date_str,
                'periodYear': str(closing_year),
                'periodNumber': str(closing_month),
                'voucherType': '记',
                'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月计提工会经费',
                'entrySeq': len(sub_voucher_list) + 1,
                'voucherAbstract': '计提工会经费',
                'accountNumber': '6602.03',
                'currencyNumber': 'BB01',
                'entryDC': 1,
                'originalAmount': result_bal_dict[asst],
                'debitAmount': result_bal_dict[asst],
                'creditAmount': 0,
                'creator': user_name,
                'description': workorder_id,
            })
        else:
            sub_voucher_list.append({
                'companyNumber': entity_gen_info_record.r_code,
                'bookedDate': closing_date_str,
                'bizDate': closing_date_str,
                'periodYear': str(closing_year),
                'periodNumber': str(closing_month),
                'voucherType': '记',
                'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月计提工会经费',
                'entrySeq': len(sub_voucher_list) + 1,
                'voucherAbstract': '计提工会经费',
                'accountNumber': '6602.03',
                'currencyNumber': 'BB01',
                'entryDC': 1,
                'originalAmount': result_bal_dict[asst],
                'debitAmount': result_bal_dict[asst],
                'creditAmount': 0,
                'creator': user_name,
                'description': workorder_id,
                'asstActType1': '客户' if re.match('[a-zA-Z]+', asst) else '成本中心',
                'asstActNumber1': asst,
            })
        sub_voucher_list.append({
            'companyNumber': entity_gen_info_record.r_code,
            'bookedDate': closing_date_str,
            'bizDate': closing_date_str,
            'periodYear': str(closing_year),
            'periodNumber': str(closing_month),
            'voucherType': '记',
            'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月计提工会经费',
            'entrySeq': len(sub_voucher_list) + 1,
            'voucherAbstract': '计提工会经费',
            'accountNumber': union_fee_lia_acc,
            'currencyNumber': 'BB01',
            'entryDC': -1,
            'originalAmount': result_bal_dict[asst],
            'debitAmount': 0,
            'creditAmount': result_bal_dict[asst],
            'creator': user_name,
            'description': workorder_id,
            'asstActType1': union_fee_lia_asst_type,
            'asstActNumber1': union_fee_lia_asst_code,
        })
        sub_voucher_list.append({
            'companyNumber': entity_gen_info_record.r_code,
            'bookedDate': closing_date_str,
            'bizDate': closing_date_str,
            'periodYear': str(closing_year),
            'periodNumber': str(closing_month),
            'voucherType': '记',
            'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月计提工会经费',
            'entrySeq': len(sub_voucher_list) + 1,
            'voucherAbstract': '计提工会经费',
            'accountNumber': union_fee_lia_acc,
            'currencyNumber': 'BB01',
            'entryDC': -1,
            'originalAmount': -round(result_bal_dict[asst] * float(labor_union_commit_record.r_value), 2),
            'debitAmount': 0,
            'creditAmount': -round(result_bal_dict[asst] * float(labor_union_commit_record.r_value), 2),
            'creator': user_name,
            'description': workorder_id,
            'asstActType1': union_fee_lia_asst_type,
            'asstActNumber1': union_fee_lia_asst_code,
        })
        # 2241.04.03 doesn't consider asst type
        sub_voucher_list.append({
            'companyNumber': entity_gen_info_record.r_code,
            'bookedDate': closing_date_str,
            'bizDate': closing_date_str,
            'periodYear': str(closing_year),
            'periodNumber': str(closing_month),
            'voucherType': '记',
            'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月计提工会经费',
            'entrySeq': len(sub_voucher_list) + 1,
            'voucherAbstract': '计提工会经费',
            'accountNumber': '2241.04.03',
            'currencyNumber': 'BB01',
            'entryDC': -1,
            'originalAmount': round(result_bal_dict[asst] * float(labor_union_commit_record.r_value), 2),
            'debitAmount': 0,
            'creditAmount': round(result_bal_dict[asst] * float(labor_union_commit_record.r_value), 2),
            'creator': user_name,
            'description': workorder_id,
        })
    sub_voucher_session.close()
    KF.save_voucher_into_database(sub_voucher_list, workorder_id)
    return sub_voucher_list


def voucher_investor_protection_fee(tb_obj: KF.TB, workorder_id: str, user_name: str) -> list:
    sub_voucher_list = []
    closing_month = tb_obj.record_list[0].month
    closing_year = tb_obj.record_list[0].year
    closing_day = constFunction.day_mapping(closing_month)
    closing_date_str = '-'.join([str(closing_year), str(closing_month), str(closing_day)])
    sub_voucher_session = create_session()
    entity_gen_info_record = sub_voucher_session.query(tBaseKdEntity).filter(
        tBaseKdEntity.r_code == str(tb_obj.record_list[0].entity_code)
    ).first()
    entity_closing_info_record = sub_voucher_session.query(tBaseClosingEntityInfo).filter(
        tBaseClosingEntityInfo.r_id == tBaseKdEntity.r_id,
        tBaseKdEntity.r_code == str(tb_obj.record_list[0].entity_code)
    ).first()
    investor_prot_record = sub_voucher_session.query(tBaseClosingArgs).filter(
        tBaseClosingArgs.r_code == 'genInvestProtectRate'
    ).first()
    # only use default asst
    os_bal = 0
    base_bal = 0

    # check local voucher:
    reg_str_list = str(investor_prot_record.r_desc).split(';')
    local_entry_record = sub_voucher_session.query(tEntry).filter(
        tEntry.r_voucher_id == tVoucher.r_id,
        tVoucher.r_work_order_id == str(workorder_id)
    ).all()
    for entry in local_entry_record:
        for reg_str in reg_str_list:
            if re.match(reg_str, entry.r_accountNumber):
                base_bal += float(entry.r_debitAmount)
                base_bal -= float(entry.r_creditAmount)

    # check tb:
    for record in tb_obj.record_list:
        if (record.balance_type == '1'
                and record.currency_code == 'GLC'
                and tb_obj.is_leaf_account(record.account_code)):
            for reg_str in reg_str_list:
                if re.match(reg_str, record.account_code):
                    base_bal += float(record.year_pl_local_currency)
            if record.account_code == '6602.50':
                os_bal += float(record.year_pl_local_currency)

    # build voucher
    os_bal = base_bal * float(investor_prot_record.r_value) - os_bal
    if os_bal != 0:
        sub_voucher_list.append({
            'companyNumber': entity_gen_info_record.r_code,
            'bookedDate': closing_date_str,
            'bizDate': closing_date_str,
            'periodYear': str(closing_year),
            'periodNumber': str(closing_month),
            'voucherType': '记',
            'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月计提投资者保护基金',
            'entrySeq': len(sub_voucher_list) + 1,
            'voucherAbstract': '计提投资者保护基金',
            'accountNumber': '2241.03.06',
            'currencyNumber': 'BB01',
            'entryDC': -1,
            'originalAmount': round(os_bal, 2),
            'debitAmount': 0,
            'creditAmount': round(os_bal, 2),
            'creator': user_name,
            'description': workorder_id,
        })
        sub_voucher_list.append({
            'companyNumber': entity_gen_info_record.r_code,
            'bookedDate': closing_date_str,
            'bizDate': closing_date_str,
            'periodYear': str(closing_year),
            'periodNumber': str(closing_month),
            'voucherType': '记',
            'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月计提投资者保护基金',
            'entrySeq': len(sub_voucher_list) + 1,
            'voucherAbstract': '计提投资者保护基金',
            'accountNumber': '6602.50',
            'currencyNumber': 'BB01',
            'entryDC': 1,
            'originalAmount': round(os_bal, 2),
            'debitAmount': round(os_bal, 2),
            'creditAmount': 0.0,
            'creator': user_name,
            'description': workorder_id,
            'asstActType1': '成本中心',
            'asstActNumber1': entity_closing_info_record.r_closing_default_cost_center_code,
        })
    sub_voucher_session.close()
    KF.save_voucher_into_database(sub_voucher_list, workorder_id)
    return sub_voucher_list


def voucher_sub_tax(tb_obj: KF.TB, workorder_id: str, user_name: str) -> list:
    sub_voucher_list = []
    closing_month = tb_obj.record_list[0].month
    closing_year = tb_obj.record_list[0].year
    closing_day = constFunction.day_mapping(closing_month)
    closing_date_str = '-'.join([str(closing_year), str(closing_month), str(closing_day)])
    sub_voucher_session = create_session()
    entity_gen_info_record = sub_voucher_session.query(tBaseKdEntity).filter(
        tBaseKdEntity.r_code == str(tb_obj.record_list[0].entity_code)
    ).first()
    cons_tax = sub_voucher_session.query(tBaseClosingArgs).filter(
        tBaseClosingArgs.r_code == 'genConsTax'
    ).first()
    edu_tax = sub_voucher_session.query(tBaseClosingArgs).filter(
        tBaseClosingArgs.r_code == 'genEduTax'
    ).first()
    local_edu_tax = sub_voucher_session.query(tBaseClosingArgs).filter(
        tBaseClosingArgs.r_code == 'genLocalEduTax'
    ).first()
    tax_record_list = [cons_tax, edu_tax, local_edu_tax]
    vat_base = 0
    vat_base_account = '2221.08.01'
    sub_tax_os_dict = {}

    # check local entries:
    local_entry_record = sub_voucher_session.query(tEntry).filter(
        tEntry.r_voucher_id == tVoucher.r_id,
        tVoucher.r_work_order_id == str(workorder_id)
    ).all()
    for entry in local_entry_record:
        if entry.r_accountNumber == vat_base_account:
            vat_base += float(entry.r_debitAmount)
            vat_base -= float(entry.r_creditAmount)

    # check tb, per book is determined by PL account:
    sub_tax_account_list = []
    for record in tax_record_list:
        sub_tax_os_dict[record] = 0
        sub_tax_account_list.append(str(record.r_desc).split('-')[1])  # 6602
    for record in tb_obj.record_list:
        if (record.balance_type == '1'
                and record.currency_code == 'GLC'
                and record.account_code == vat_base_account):
            vat_base += float(record.end_balance_local_currency)
        if (record.balance_type == '1'
                and record.currency_code == 'GLC'
                and record.account_code in sub_tax_account_list):
            for sql_record in tax_record_list:
                if record.account_code == str(record.r_desc).split('-')[1]:
                    tax_record_list[sql_record] += record.period_pl_local_currency

    # calculate os
    for record in tax_record_list:
        sub_tax_os_dict[record] = (vat_base * float(record.r_value)) - sub_tax_os_dict[record]


    # todo： 分支机构10万优惠政策逻辑更新
    # build voucher
    for record in sub_tax_os_dict:
        if sub_tax_os_dict[record] != 0:
            sub_voucher_list.append({
                'companyNumber': entity_gen_info_record.r_code,
                'bookedDate': closing_date_str,
                'bizDate': closing_date_str,
                'periodYear': str(closing_year),
                'periodNumber': str(closing_month),
                'voucherType': '记',
                'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月计提附加税',
                'entrySeq': len(sub_voucher_list) + 1,
                'voucherAbstract': '计提附加税',
                'accountNumber': str(record.r_desc).split('-')[1],
                'currencyNumber': 'BB01',
                'entryDC': 1,
                'originalAmount': round(sub_tax_os_dict[record], 2),
                'debitAmount': round(sub_tax_os_dict[record], 2),
                'creditAmount': 0,
                'creator': user_name,
                'description': workorder_id,
            })
            sub_voucher_list.append({
                'companyNumber': entity_gen_info_record.r_code,
                'bookedDate': closing_date_str,
                'bizDate': closing_date_str,
                'periodYear': str(closing_year),
                'periodNumber': str(closing_month),
                'voucherType': '记',
                'voucherNumber': entity_gen_info_record.r_chs_name + str(closing_month) + '月计提附加税',
                'entrySeq': len(sub_voucher_list) + 1,
                'voucherAbstract': '计提附加税',
                'accountNumber': str(record.r_desc).split('-')[0],
                'currencyNumber': 'BB01',
                'entryDC': -1,
                'originalAmount': round(sub_tax_os_dict[record], 2),
                'debitAmount': 0.0,
                'creditAmount': round(sub_tax_os_dict[record], 2),
                'creator': user_name,
                'description': workorder_id,
            })
    sub_voucher_session.close()
    KF.save_voucher_into_database(sub_voucher_list, workorder_id)
    return sub_voucher_list


def get_function_pointer_dict() -> dict:
    all_func_list = dir(sys.modules[__name__])
    pointer_dict = {}
    for func in all_func_list:
        if re.match('voucher_.*', func) is not None:
            pointer_dict[func] = eval(func)
    return pointer_dict


def _init_functions_in_db():
    init_session = create_session()
    func_dict = get_function_pointer_dict()
    exist_func = init_session.query(tBaseClosingFunctions).all()
    for func in exist_func:
        if func.r_pointer_key in func_dict:
            func_dict.pop(func.r_pointer_key)
    for key in func_dict:
        id = generate_key()
        print('recording info of ' + key)
        name = input('the chs name of voucher:')
        pri = 1
        init_session.add(tBaseClosingFunctions(**{
            'r_id': id,
            'r_chs_name': name,
            'r_pointer_key': key,
            'r_priority': pri,
        }))
        init_session.commit()
    return 0


def _init_function_recon():
    init_session = create_session()
    entity_id_record = init_session.query(tBaseClosingEntityInfo).all()
    entity_id_dict = {}
    for record in entity_id_record:
        entity_id_dict[record.r_id] = {'is_sub': record.r_is_sub}
    function_id_record = init_session.query(tBaseClosingFunctions).all()
    function_id_dict = {}
    for record in function_id_record:
        function_id_dict[record.r_id] = {'is_sub': record.r_is_sub}
    for entity in entity_id_dict:
        for func in function_id_dict:
            db_record = init_session.query(tBaseClosingEnityFunctionRecon).filter(
                tBaseClosingEnityFunctionRecon.r_entity_id == str(entity),
                tBaseClosingEnityFunctionRecon.r_closing_function_id == str(func)
            ).first()
            if not db_record:
                entity_info = init_session.query(tBaseClosingEntityInfo.r_is_sub).filter(
                    tBaseClosingEntityInfo.r_id == entity
                ).first()
                function_info = init_session.query(tBaseClosingFunctions.r_is_sub).filter(
                    tBaseClosingFunctions.r_id == func
                )
                init_session.add(tBaseClosingEnityFunctionRecon(**{
                    'r_id': generate_key(),
                    'r_entity_id': str(entity),
                    'r_closing_function_id': str(func),
                    'r_available': 1 if entity_info[0] != 0 and function_info == 0 else 0
                }))
                init_session.commit()
    init_session.close()


if __name__ == '__main__':
    pass