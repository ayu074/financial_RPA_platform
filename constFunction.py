import time
import os
import re
import traceback
import pickle
import SqlFunction

from functools import wraps


AbsPath = os.path.abspath(__file__)
AbsPath_Folder = re.search('(.*)\\\\', AbsPath).group(1) + '\\'


class FinTime:
    def __init__(self, raw_time: [str, tuple, list]):
        """
        parse algorithm: extract first connector symbol -> left sliced all digits and connector -> split YMD
        :param time_string:
        """
        all_digits_pattern = re.compile('(^[\\d]*$)')
        self.initiated = False
        self.ISO_string = None
        self.year = 1900
        self.month = 1
        self.day = 1
        if type(raw_time) == str:
            if re.match(all_digits_pattern, raw_time):
                if len(raw_time) >= 8:
                    self.year = int(raw_time[0: 4])
                    self.month = int(raw_time[4: 6])
                    self.day = int(raw_time[6: 8])
                    self.initiated = True
                else:
                    self.year = 2000 + int(raw_time[0: 2])
                    self.month = int(raw_time[2: 4])
                    self.day = int(raw_time[4: 6])
                    self.initiated = True
            else:
                connector = re.search('\\d+([^\\d]+)', raw_time).group(1)
                time_tuple = raw_time.split(connector)
                try:
                    self.year = int(time_tuple[0]) + 2000 if int(time_tuple[0]) < 100 else int(time_tuple[0])
                    self.month = int(time_tuple[1])
                    self.initiated = True
                except Exception as e:
                    manual_error_log(str(e))
                    print(e)
                try:
                    self.day = int(re.match('(\\d+)', time_tuple[2]).group(1)[0: 2])
                except Exception:
                    pass
        else:
            if len(raw_time) >= 2:
                try:
                    self.year = int(raw_time[0]) + 2000 if int(raw_time[0]) < 100 else int(raw_time[0])
                    self.month = int(raw_time[1])
                    self.initiated = True
                except Exception as e:
                    manual_error_log(str(e))
                    print(e)
                try:
                    self.day = int(raw_time[3])
                except Exception:
                    self.day = 1
            else:
                pass
        if self.initiated:
            try:
                if (self.month < 1 or self.month > 12) or (self.day < 1 or self.day > day_mapping(self.month, leap_year=is_leap_year(self.year))):
                    self.initiated = False
                    self.year = 1900
                    self.month = 1
                    self.day = 1
            except TypeError:
                self.initiated = False
                self.year = 1900
                self.month = 1
                self.day = 1
        if self.initiated:
            str_month = '0' + str(self.month) if self.month < 10 else str(self.month)
            str_day = '0' + str(self.day) if self.day < 10 else str(self.day)
            self.ISO_string = '-'.join((str(self.year), str_month, str_day))

    def _update_ISO_string(self):
        if self.initiated:
            str_month = '0' + str(self.month) if self.month < 10 else str(self.month)
            str_day = '0' + str(self.day) if self.day < 10 else str(self.day)
            self.ISO_string = '-'.join((str(self.year), str_month, str_day))

    def _to_serial(self):
        pass

    def _previous_month(self):
        self.month = self.month - 1 if self.month != 1 else 12
        self.year = self.year if self.month != 1 else self.year - 1
        return None

    def _next_month(self):
        self.month = self.month + 1 if self.month != 12 else 1
        self.year = self.year if self.month != 12 else self.year + 1
        return None

    def _previous_day(self):
        if self.day == 1:
            self._previous_month()
            self.day = day_mapping(self.month, is_leap_year(self.year))
        else:
            self.day -= 1
        return None

    def _next_day(self):
        if self.day == day_mapping(self.month, is_leap_year(self.year)):
            self.day = 1
            self._next_month()
        else:
            self.day += 1

    def move_by_day(self, day_step: int):
        if day_step >= 0:
            while day_step > 0:
                self._next_day()
                day_step -= 1
        else:
            while day_step < 0:
                self._previous_day()
                day_step += 1
        self._update_ISO_string()


def day_mapping(month: [int, str], leap_year=False) -> int:
    day_dic = {
        '1': 31,
        '2': 28,
        '3': 31,
        '4': 30,
        '5': 31,
        '6': 30,
        '7': 31,
        '8': 31,
        '9': 30,
        '10': 31,
        '11': 30,
        '12': 31,
        '01': 31,
        '02': 28,
        '03': 31,
        '04': 30,
        '05': 31,
        '06': 30,
        '07': 31,
        '08': 31,
        '09': 30,
    }
    leap_day_dic = {
        '1': 31,
        '2': 29,
        '3': 31,
        '4': 30,
        '5': 31,
        '6': 30,
        '7': 31,
        '8': 31,
        '9': 30,
        '10': 31,
        '11': 30,
        '12': 31,
        '01': 31,
        '02': 29,
        '03': 31,
        '04': 30,
        '05': 31,
        '06': 30,
        '07': 31,
        '08': 31,
        '09': 30,
    }
    return leap_day_dic.get(str(month)) if leap_year else day_dic.get(str(month))


def is_leap_year(year_index: int) -> bool:
    if divmod(year_index, 400)[1] == 0 or (divmod(year_index, 1000)[1] != 0 and divmod(year_index, 4) == 0):
         return True
    else:
        return False


def locate_period(bias=0) -> tuple:
    str_year = time.strftime('%Y')
    str_month = time.strftime('%m')
    str_day = time.strftime('%d')
    int_year = int(str_year)
    int_month = int(str_month)
    int_day = int(str_day)
    if bias == -1:
        if int_month == 1:
            int_month = 12
            int_year -= 1
        else:
            int_month -= 1
        int_day = day_mapping(int_month)
    return str(int_year), str(int_month), str(int_day)


def guess_period() -> tuple:
    curr_day = int(time.strftime('%d'))
    if curr_day <= 5:
        return locate_period(-1)
    else:
        return locate_period(1)


def fulfill_length(ori_str: [int, str], total_length=4, replace_char='0') -> str:
    if len(str(ori_str)) >= total_length:
        return str(ori_str)
    else:
        return replace_char * (total_length - len(str(ori_str))) + str(ori_str)


def generate_order_number() -> str:
    order_session = SqlFunction.create_session()
    curr_date = time.strftime('%Y%m%d')
    try:
        latest_bill_object_list = order_session.query(SqlFunction.tWorkOrderMain.r_number).filter(
            SqlFunction.tWorkOrderMain.r_number.like('W' + curr_date + '%')
        ).all()
        latest_bill_list = []
        for each in latest_bill_object_list:
            latest_bill_list.append(each[0])
        latest_bill = max(latest_bill_list)
        curr_number = int(re.match('W' + curr_date + '(\\d*)', latest_bill).group(1)) + 1
    except Exception:
        curr_number = 1
    order_session.close()
    curr_bill_number = 'W' + curr_date + fulfill_length(str(curr_number), total_length=4, replace_char='0')
    return curr_bill_number


def ip_to_name(ip_addr):
    ip_dic = {
        '127.0.0.1': '俞聿非',
        '10.20.4.56': '俞聿非',
        '172.25.81.24': '俞聿非',
        '172.25.82.186': '陈晶',
        '172.25.82.142': '朱光耀',
        '172.25.82.175': '景白云',
        '172.25.82.171': '范晓亚',
        '172.25.82.143': '奚帅华',
        '172.25.81.21': '曹文轩'
    }
    return ip_dic.get(ip_addr)


def function_log(target_func, input_info=True, output_info=True):
    @wraps(target_func)
    def log_the_func(*args, **kwargs):
        file_name = AbsPath_Folder + 'log\\function_calling_log_' + time.strftime('%Y%m%d') + '.log'
        if input_info:
            time_stamp_enter = time.strftime('%H:%M:%S')
            with open(file_name, 'a+') as f:
                f.write(time_stamp_enter + ': entered function: <' + target_func.__name__ + '> of module: <'
                        + target_func.__module__ + '>;  args are: ' + str(args) + str(kwargs))
                f.write('\n')
        result = target_func(*args, **kwargs)
        if output_info:
            time_stamp_quit = time.strftime('%H:%M:%S')
            with open(file_name, 'a+') as f:
                f.write(time_stamp_quit + ': left function: <' + target_func.__name__ + '> of module: <'
                        + target_func.__module__ + '>; results are: ' + str(result))
                f.write('\n')
            return result
    return log_the_func


def manual_error_log(error_info: str) -> None:
    file_name = AbsPath_Folder + 'log\\manual_error_log_' + time.strftime('%Y%m%d') + '.log'
    time_stamp_enter = time.strftime('%H:%M:%S')
    father_function = traceback.extract_stack()[-2][2]
    with open(file_name, 'a+') as f:
        f.write(time_stamp_enter + ' : MANUAL LOGGED IN FUNCTION: ' + father_function + '; OF WHICH THE ERROR INFO IS: ' + error_info)
        f.write('\n')
    return None


if __name__ == '__main__':
    pass