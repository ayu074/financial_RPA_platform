class voucher_input_task {
    constructor(voucher_id_list) {
        this.task_queue = []
        for (i=0; i<voucher_id_list.length; i++) {
            this.task_queue[i] = {
                'id': voucher_id_list[i],
                'status': -1, // -1: ready; 0: finished; 1: processing
                'result': '',
            }
        }
    }
    get_operating_id() {
        let current_id = null;
        for (i=this.task_queue.length - 1; i>=0; i--) {
            if (this.task_queue[i]['status'] == 1) {
                return -1;
            }else if (this.task_queue[i]['status'] == -1) {
                current_id = this.task_queue[i]['id'];
            }
        }
        return current_id;
    }
    set_id_to_processing(process_id) {
        for (i=0; i<this.task_queue.length; i++) {
            if (this.task_queue[i]['id'] == process_id) {
                this.task_queue[i]['status'] = 1;
                break;
            }
        }
    }
    set_id_to_finished(finish_id, result_str) {
        for (i=0; i< this.task_queue.length; i++) {
            if(this.task_queue[i]['id'] == finish_id) {
                this.task_queue[i]['status'] = 0;
                this.task_queue[i]['result'] = result_str;
                break;
            }
        }
    }



}

function get_query_value(query_name) {
    var reg = new RegExp("(^|&)" + query_name + "=([^&]*)(&|$)", "i")
    var r = window.location.search.substr(1).match(reg);
    if ( r != null) {
        return decodeURI(r[2]);
    }else {
        return null;
    }
}

function insert_after(new_child, ref_child) {
    var farther_div = ref_child.parentNode;
    var target_div = ref_child.nextSibling;
    if (target_div != undefined) {
        farther_div.insertBefore(new_child, target_div);
    }else {
        farther_div.appendChild(new_child);
    }
}

function get_voucher_info(info_type, entry_voucher_id) {
    var voucher_data;
    if (get_query_value('voucher_id') != null) {
        var post_args = 'voucher_id=' + get_query_value('voucher_id');
    }else if (get_query_value('workorder_id') != null) {
        var post_args = 'workorder_id=' + get_query_value('workorder_id');
    }else {
        var post_args = '1=1';
    }
    if(info_type == 'entry'){
        var post_args = 'voucher_id=' + entry_voucher_id;
    }
    console.log(post_args);
    var voucher_xml = new XMLHttpRequest();
    var interface_dict = {
        'entry': '/getEntryData',
        'voucher': '/getVoucherData',
    }
    voucher_xml.open('POST', interface_dict[info_type], false);
    voucher_xml.setRequestHeader('content-type', 'application/x-www-form-urlencoded');
    voucher_xml.onreadystatechange = function() {
        if (voucher_xml.readyState == 4 && voucher_xml.status == 200) {
            voucher_data = JSON.parse(voucher_xml.responseText);
        } else {
            console.log('failed in loading voucher data');
        }
    }

    voucher_xml.send(post_args);
    return voucher_data;
}


function _create_voucher_view(voucher_json) {
    var voucher_info_dict = [8, 2, 12, 11, 13, 17, 18, 21, 22]
    var voucher_table = document.getElementById('voucher-table');
    if (voucher_json == null || voucher_json == undefined) {
        var no_record = document.getElementById('no_record');
        no_record.style.display = 'block';
        return 0;
    }
    for (i=0; i<voucher_json.length; i++) {
        var entry_row = document.createElement('div');
        entry_row.setAttribute('class', 'entry');
        entry_row.setAttribute('id', voucher_json[i][0]);
        for (j=0; j< voucher_info_dict.length; j++) {
            var entry_col = document.createElement('div');
            entry_col.setAttribute('class', 'col-voucher');
            entry_col.innerHTML = voucher_json[i][voucher_info_dict[j]];
            entry_row.appendChild(entry_col);
            if (j == 2) {
                entry_col.setAttribute('title', voucher_json[i][25]);
            } else if (j == 12) {
                entry_col.setAttribute('title', voucher_json[i][26]);
            }
        }
        voucher_table.appendChild(entry_row);
    }
}
function load_voucher_head(){
    var header = ['凭证号', '账套', '科目','摘要', '币别', '借方金额','贷方金额', '辅助项目', '辅助代码', '推送'];
    var voucher_table = document.getElementById('voucher-table');
    var voucher_head_line = document.createElement('div');
    voucher_head_line.setAttribute('class', 'voucher-head');
    voucher_table.appendChild(voucher_head_line);
    for (l=0; l<header.length; l++) {
        var head_col = document.createElement('div');
        head_col.setAttribute('class', 'col-header');
        head_col.innerHTML = header[l];
        voucher_head_line.appendChild(head_col);
    }
}

function load_voucher(voucher_json) {
    var voucher_info_dict = [
        'r_sys_voucher_number',
        'r_entity_chs_name',
        null,
        'r_abstract',
        null,
        'r_debit_total',
        'r_credit_total',
        null,
        null,
        'r_kd_voucher_number'
    ];
    var voucher_table = document.getElementById('voucher-table');
    if (voucher_json == null || voucher_json == undefined) {
        var no_record = document.getElementById('no_record');
        no_record.style.display = 'block';
        return 0;
    }
    for (i=0; i<voucher_json.length; i++) {
        var voucher_row = document.createElement('div');
        voucher_row.setAttribute('class', 'voucher');
        voucher_row.setAttribute('id', voucher_json[i]['r_id']);
        voucher_row.setAttribute('expended', 'no');
        voucher_row.setAttribute('onclick', 'load_entry(this)');
        for (j=0; j< voucher_info_dict.length; j++) {
            var voucher_col = document.createElement('div');
            voucher_col.setAttribute('class', 'col-voucher');
            if (voucher_info_dict[j] == null) {
                voucher_col.innerHTML = '&nbsp';
            }else if(voucher_info_dict[j] == 'r_kd_voucher_number'){
                if (voucher_json[i]['r_kd_voucher_number'] == null) {
                    voucher_col.innerHTML = '推送';
                    voucher_col.setAttribute('onclick', 'push_voucher(this.parentNode.id, voucher_task)')
                    voucher_col.setAttribute('class', 'col-voucher-desc-active')
                }else {
                    voucher_col.innerHTML = voucher_json[i]['r_kd_voucher_number'];
                    voucher_col.setAttribute('class', 'col-voucher-desc')
                }
            }else {
                voucher_col.innerHTML = voucher_json[i][voucher_info_dict[j]].toLocaleString();
            }
            voucher_row.appendChild(voucher_col);
            if (voucher_info_dict[j] == 'r_entity_chs_name') {
                voucher_col.setAttribute('title', voucher_json[i]['r_entity_code']);
            }
        }
        voucher_table.appendChild(voucher_row);
    }
}

function load_entry(voucher_element) {
    if (voucher_element.getAttribute('expended') == 'no') {
        var entry_data = get_voucher_info('entry', voucher_element.getAttribute('id'));
        var entry_elements = document.getElementsByClassName('entry');
        for (l=entry_elements.length-1; l>=0; l--) {
            entry_elements[l].remove();
        }
        var voucher_elements = document.getElementsByClassName('voucher');
        for (l=0; l<voucher_elements.length; l++) {
            voucher_elements[l].setAttribute('expended', 'no')
        }
            var entry_info_dict = [
                'r_voucherNumber',
                'r_entity_chs_name',
                'r_account_chs_name',
                'r_voucherAbstract',
                'r_currencyNumber',
                'r_debitAmount',
                'r_creditAmount',
                'r_asstActType1',
                'r_asstActNumber1',
            ];
            var curr_tail = voucher_element;
            for (i=0; i<entry_data.length; i++) {
                var entry_line = document.createElement('div');
                entry_line.setAttribute('class', 'entry');
                entry_line.setAttribute('id', entry_data[i]['r_id']);
                for (j=0; j<entry_info_dict.length; j++) {
                    var entry_col = document.createElement('div');
                    entry_col.setAttribute('class', 'col-voucher');
                    if (entry_info_dict[j] == 'r_entity_chs_name'){
                        entry_col.setAttribute('title', entry_data[i]['r_companyNumber']);
                    }else if (entry_info_dict[j] == 'r_account_chs_name') {
                        entry_col.setAttribute('title', entry_data[i]['r_accountNumber']);
                    }
                    if (entry_info_dict[j] == 'r_voucherNumber'){
                        entry_col.innerHTML = '&nbsp;';
                    }else if (entry_data[i][entry_info_dict[j]] != null) {
                        entry_col.innerHTML = entry_data[i][entry_info_dict[j]].toLocaleString();
                    }else{
                        entry_col.innerHTML = entry_data[i][entry_info_dict[j]];
                    }
                    entry_line.appendChild(entry_col);
                }
                insert_after(entry_line, curr_tail);
                curr_tail = entry_line;
            }
        voucher_element.setAttribute('expended', 'yes');
    } else {
        var entry_elements = document.getElementsByClassName('entry');
        for (l=entry_elements.length-1; l>=0; l--) {
            entry_elements[l].remove();
        }
    }
}

function push_voucher(voucher_id, task_list) {
    // if (voucher_id == null) {
    //     voucher_id = this.parentNode.getAttribute('id');
    // }
    console.log('正在推送' + voucher_id);
    var voucher_import_request = new XMLHttpRequest();
    var voucher_json_result;
    var push_voucher_args = 'voucher_id=' + voucher_id;
    voucher_import_request.open('POST', '/importVoucher', true);
    voucher_import_request.setRequestHeader('content-type', 'application/x-www-form-urlencoded');
    voucher_import_request.onreadystatechange = function () {
        if (voucher_import_request.readyState == 4 && voucher_import_request.status == 200) {
            voucher_json_result = JSON.parse(voucher_import_request.responseText);
            task_list.set_id_to_finished(voucher_id, voucher_json_result);
            var voucher_element = document.getElementById(voucher_id);
            var voucher_last_col = voucher_element.lastChild;
            if (voucher_json_result['result'] == '0000') {
                voucher_last_col.setAttribute('class', 'col-voucher-desc');
                voucher_last_col.setAttribute('onclick', 'javascript:void(0)');
                voucher_last_col.innerHTML = voucher_json_result['voucher_number'];
            }else {
                voucher_last_col.innerHTML = '重新推送'
            }
        }
    }
    task_list.set_id_to_processing(voucher_id);
    voucher_import_request.send(push_voucher_args);
}

function push_all_voucher(task_list) {
    var all_task = setInterval(function () {
        if(task_list.get_operating_id() == null) {
            clearInterval(all_task);
        }else if(task_list.get_operating_id() == -1) {
        }else {
            push_voucher(task_list.get_operating_id(), task_list);
        }
    }, 1000)
}

function export_voucher() {
    var export_args;
    if (get_query_value('workorder_id') != null) {
        export_args = '?workorder_id=' + get_query_value('workorder_id');
    }else{
        export_args = '?voucher_id=' + get_query_value('voucher_id');
    }
    return window.location.href = '/exportVoucher' + export_args;
}