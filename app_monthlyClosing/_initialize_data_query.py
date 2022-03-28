import openpyxl
import SqlFunction as SqlF
import re
from tkinter import filedialog


def _import_entity_info():
    """
    kd report standard form
    :return:
    """
    fp = filedialog.askopenfilename()
    wb = openpyxl.load_workbook(fp)
    sht = wb.active
    pass


def _add_args():
    id = SqlF.generate_key()
    desc = input("参数备注：")
    code = input("参数代码：")
    value = input("参数数值：")
    args_session = SqlF.create_session()
    args_session.add(SqlF.tBaseClosingArgs(**{
        'r_id': str(id),
        'r_value': float(value),
        'r_code': str(code),
        'r_desc': str(desc)
    }))
    args_session.commit()
    args_session.close()


def _update_entity_from_kd_report():
    """
    column t is a filter to determine whether the entity
    :return:
    """
    pass


if __name__ == '__main__':
    pass