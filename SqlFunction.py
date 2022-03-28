import traceback
import re
import time
import random

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Float, DECIMAL


BASE = declarative_base()


class tUser(BASE):
    __tablename__ = 't_user'
    r_id = Column(String(30), primary_key=True)
    r_name = Column(String(20), unique=True)
    r_chs_name = Column(String(20))
    r_hash_pwd = Column(String(100))
    r_module_auth = Column(String(500))
    r_admin_auth = Column(String(10))


class tVoucher(BASE):
    __tablename__ = 't_voucher'
    r_id = Column(String(30), primary_key=True)
    r_work_order_id = Column(String(30))
    r_sys_voucher_number = Column(String(50))
    r_kd_voucher_number = Column(String(50))
    r_entity_code = Column(String(50))
    r_abstract = Column(String(500))
    r_year = Column(Integer())
    r_month = Column(Integer())
    r_type = Column(String(5))
    r_debit_total = Column(DECIMAL(15, 2))
    r_credit_total = Column(DECIMAL(15, 2))
    r_import_result = Column(String(500))
    r_description = Column(String(500))
    r_is_deleted = Column(Integer())


class tEntry(BASE):
    __tablename__ = 't_entry'
    r_id = Column(String(30), primary_key=True)
    r_voucher_id = Column(String(30))
    r_companyNumber = Column(String(30))
    r_bookedDate = Column(String(30))
    r_bizDate = Column(String(30))
    r_periodYear = Column(Integer())
    r_periodNumber = Column(Integer())
    r_voucherType = Column(String(5))
    r_voucherNumber = Column(String(100))
    r_entrySeq = Column(Integer())
    r_voucherAbstract = Column(String(500))
    r_accountNumber = Column(String(30))
    r_currencyNumber = Column(String(10))
    r_localRate = Column(DECIMAL(15, 2))
    r_entryDC = Column(Integer())
    r_originalAmount = Column(DECIMAL(15, 2))
    r_debitAmount = Column(DECIMAL(15, 2))
    r_creditAmount = Column(DECIMAL(15, 2))
    r_creator = Column(String(10))
    r_description = Column(String(500))
    r_asstActType1 = Column(String(10))
    r_asstActNumber1 = Column(String(20))
    r_asstActType2 = Column(String(10))
    r_asstActNumber2 = Column(String(20))


class tBaseKdEntity(BASE):
    __tablename__ = 't_base_kd_entity'
    r_id = Column(String(30), primary_key=True)
    r_code = Column(String(30))
    r_chs_name = Column(String(50))
    r_thumbnail_code = Column(String(50))
    r_desc = Column(String(100))
    r_module_affected = Column(String(500))


class tBaseKdSupplier(BASE):
    __tablename__ = 't_base_kd_supplier'
    r_id = Column(String(30), primary_key=True)
    r_entity_id = Column(String(30))
    r_code = Column(String(30))
    r_module = Column(String(50))
    r_desc = Column(String(100))


class tBaseKdCostCenter(BASE):
    __tablename__ = 't_base_kd_cost_center'
    r_id = Column(String(30), primary_key=True)
    r_entity_id = Column(String(30))
    r_code = Column(String(30))
    r_module = Column(String(50))
    r_desc = Column(String(100))


class tBaseCounterEntity(BASE):
    __tablename__ = 't_base_counter_entity'
    r_id = Column(String(30), primary_key=True)
    r_entity_id = Column(String(30))
    r_code = Column(String(30))
    r_chs_name = Column(String(50))
    r_desc = Column(String(100))


class tBaseKdAccount(BASE):
    __tablename__ = 't_base_kd_account'
    r_id = Column(String(30), primary_key=True)
    r_account_code = Column(String(30))
    r_account_name = Column(String(50))
    r_account_full_name = Column(String(200))
    r_entity_id = Column(String(30))
    r_currency_type = Column(String(200))
    r_asst_type = Column(String(50))
    r_last_update_period = Column(String(45))


class tModule(BASE):
    __tablename__ = 't_module'
    r_id = Column(String(30), primary_key=True)
    r_code = Column(String(100))
    r_name = Column(String(100))
    r_desc = Column(String(1000))
    r_img_locale = Column(String(1000))
    r_url_prefix = Column(String(200))


class tWorkOrderMain(BASE):
    __tablename__ = 't_work_order_main'
    r_id = Column(String(30), primary_key=True)
    r_number = Column(String(30))
    r_date = Column(String(30))
    r_keyword = Column(String(1000))
    r_doc_status = Column(String(10))
    r_creator = Column(String(30))
    r_module_id = Column(String(30))


class tBaseClosingEntityInfo(BASE):
    __tablename__ = 't_base_closing_entity_info'
    r_id = Column(String(30), primary_key=True)
    r_is_sub = Column(Integer())
    r_is_small = Column(Integer())
    r_is_collected = Column(Integer())
    r_small_threshold_id = Column(String(30))
    r_vat_rate_id = Column(String(30))
    r_small_tax_rate_id = Column(String(30))
    r_small_cal_rate_id = Column(String(30))
    r_responsible_user_id = Column(String(1000))
    r_entity_owner_chs_name = Column(String(30))
    r_closing_default_supplier_code = Column(String(30))
    r_closing_default_cost_center_code = Column(String(30))


class tBaseClosingArgs(BASE):
    __tablename__ = 't_base_closing_args'
    r_id = Column(String(30), primary_key=True)
    r_value = Column(DECIMAL(19, 4))
    r_code = Column(String(50))
    r_abs = Column(String(1000))
    r_desc = Column(String(2000))


class tBaseClosingFunctions(BASE):
    __tablename__ = 't_base_closing_functions'
    r_id = Column(String(30), primary_key=True)
    r_chs_name = Column(String(100))
    r_pointer_key = Column(String(100))
    r_priority = Column(Integer())
    r_is_sub = Column(Integer())


class tBaseClosingEnityFunctionRecon(BASE):
    __tablename__ = 't_base_closing_entity_function_recon'
    r_id = Column(String(30), primary_key=True)
    r_entity_id = Column(String(30))
    r_closing_function_id = Column(String(30))
    r_available = Column(Integer(), default=0)


class tBaseClosingSmallTaxeeArgs(BASE):
    __tablename__ = 't_base_closing_small_taxee_args'
    r_id = Column(String(30), primary_key=True)
    r_entity_id = Column(String(30))
    r_account_code = Column(String(30))
    r_restoration_rate = Column(DECIMAL(19, 4))
    r_is_separation_acc = Column(String(30))
    r_is_cal_base_acc = Column(String(30))
    r_avaiable = Column(Integer(), default=0)


class tBackupTBObject(BASE):
    __tablename__ = 't_backup_tb_object'
    r_id = Column(String(30), primary_key=True)
    r_entity_id = Column(String(30))
    r_year = Column(Integer())
    r_month = Column(Integer())
    r_tb_desc = Column(String(1000))
    r_file_storage_full_path = Column(String(1000))
    r_invoke_time_stamp = Column(String(30))


def generate_key() -> str:
    """
    时间精度1微秒，随机数种子6位数，随机数1000轮测试平均1200次，最少19次产生碰撞
    :return:
    """
    time_prefix = str(hex(int(time.time() * 1000000)))[2:]
    random_tail = random.randint(100000, 999999)
    return 'UID' + time_prefix + str(random_tail)


def init_all_db() -> int:
    global BASE
    user_name = 'name'
    user_pwd = 'pwd'
    db_address = 'localhost'
    db_name = 'fp'
    db_port = '3306'
    engine = sqlalchemy.create_engine('mysql+mysqlconnector://' + user_name + ':' +
                                      user_pwd + '@' + db_address + ':' + db_port + '/' +
                                      db_name, echo=True)
    try:
        BASE.metadata.create_all(engine)
        return 0
    except Exception:
        print(traceback.format_exc())
        return -1


def create_session() -> sqlalchemy.orm.session:
    """

    :return: return an instance of session object, need to manual close
    """
    user_name = 'root'
    user_pwd = '407407Aa'
    db_address = 'localhost'
    db_name = 'fp'
    db_port = '3306'
    engine = sqlalchemy.create_engine('mysql+mysqlconnector://' + user_name + ':' +
                                      user_pwd + '@' + db_address + ':' + db_port + '/' +
                                      db_name, echo=True)
    new_session = sessionmaker(bind=engine)
    session_instance = new_session()
    return session_instance


def _delete_work_order(workorder_id: str) -> None:
    del_session = create_session()
    # delete entries:
    del_session.query(tEntry).filter(
        tEntry.r_voucher_id == tVoucher.r_id,
        tVoucher.r_work_order_id == workorder_id
    ).delete(synchronize_session=False)
    del_session.commit()
    # delete vouchers:
    del_session.query(tVoucher).filter(
        tVoucher.r_work_order_id == workorder_id
    ).delete(synchronize_session=False)
    del_session.commit()
    # delete workorder
    del_session.query(tWorkOrderMain).filter(
        tWorkOrderMain.r_id == workorder_id
    ).delete(synchronize_session=False)
    del_session.commit()
    del_session.close()


if __name__ == '__main__':
    print(generate_key())