import os
import sys
import re
ROOT_PATH = re.search('(.*)\\\\', os.path.abspath(__file__)).group(1)
sys.path.append(ROOT_PATH + r'\venv\Lib\site-packages')

import time
import threading
import pickle

import KingdaeFunction as KF
import SqlFunction as SF
import constFunction as CF

import _database_query


threadLock = threading.Lock()


class BackgroundThread(threading.Thread):
    def __init__(self, target_function_pointer, lock_needed=False):
        threading.Thread.__init__(self)
        self.function = target_function_pointer
        self.lock_needed = lock_needed

    def run(self):
        print('正在启动线程：' + self.function.__name__)
        if self.lock_needed:
            threadLock.acquire()
            self.function()
            threadLock.release()
        else:
            self.function()


def _save_previous_tb(entity_obj, y, m, fp_prefix, desc) -> None:
    ssid = KF.login_service()
    uid = SF.generate_key()
    file_path = fp_prefix + '\\' + uid + '.pkl'
    tb = KF.TB(KF.get_account_balance(entity_code=entity_obj.r_code,
                                      str_year=y,
                                      str_month=m,
                                      ssid=ssid))
    tb.get_all_asst_tb()
    with open(file_path, 'wb') as t:
        pickle.dump(tb, t)
    tb_save_session = SF.create_session()
    tb_save_session.add(SF.tBackupTBObject(**{
        'r_id': str(uid),
        'r_entity_id': str(entity_obj.r_id),
        'r_year': int(y),
        'r_month': int(m),
        'r_tb_desc': str(desc),
        'r_file_storage_full_path': str(file_path),
        'r_invoke_time_stamp': str(time.time())
    }))
    tb_save_session.commit()
    tb_save_session.close()


def backup_small_taxee_all_tb(delay=86400):
    st_session = SF.create_session()
    entity_list = st_session.query(SF.tBaseKdEntity).filter(
        SF.tBaseKdEntity.r_id == SF.tBaseClosingEntityInfo.r_id,
        SF.tBaseClosingEntityInfo.r_is_small == 0
    ).all()
    st_session.close()
    while True:
        curr_day = int(time.strftime('%d'))
        curr_month = int(time.strftime('%m'))
        curr_year = int(time.strftime('%Y'))
        if curr_month == 1:
            curr_year -= 1
            curr_month = 12
        else:
            curr_month -= 1
        if curr_day >= 20:
            st_session = SF.create_session()
            for entity in entity_list:
                record = st_session.query(SF.tBackupTBObject).filter(
                    SF.tBackupTBObject.r_year == curr_year,
                    SF.tBackupTBObject.r_month == curr_month,
                    SF.tBackupTBObject.r_entity_id == entity.r_id
                ).first()
                if not record:
                    _save_previous_tb(entity,
                                      int(curr_year),
                                      int(curr_month),
                                      'D:\\FP\\app_monthlyClosing\\closing_backup_tb',
                                      '小规模纳税人往期余额表暂存')
            st_session.close()
        time.sleep(delay)


def backup_account_info(delay=86400):
    while True:
        curr_day = int(time.strftime('%d'))
        curr_year, curr_month, _ = CF.locate_period(-1)
        if curr_day >= 20:
            st_session = SF.create_session()
            entity_list = st_session.query(SF.tBaseKdEntity).all()
            for entity in entity_list:
                entity_last_update_tuple = st_session.query(SF.tBaseKdAccount.r_last_update_period).filter(
                    SF.tBaseKdAccount.r_entity_id == entity.r_id
                ).first()
                if entity_last_update_tuple:
                    entity_last_update_str = entity_last_update_tuple[0]
                    save_year, save_month = str(entity_last_update_str).split('-')
                    if int(save_year) <= int(curr_year) and int(save_month) < int(curr_month):
                        _database_query._update_kd_account_from_kd(entity_list=[entity.r_code])
            st_session.close()
        time.sleep(delay)


if __name__ == '__main__':
    applying_function_list = [
        (backup_small_taxee_all_tb, False),
        (backup_account_info, False)
    ]
    threading_list = []
    for each in applying_function_list:
        threading_list.append(BackgroundThread(each[0], each[1]))
    for each in threading_list:
        each.start()
    for each in threading_list:
        each.join()