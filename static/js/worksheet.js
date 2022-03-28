function create_work_order_line(index, order_info) {
    let new_order = document.createElement('div');
    new_order.setAttribute('id', order_info['r_id']);
    new_order.setAttribute('class', 'work-order');
    new_order.setAttribute('onclick', 'jump_to_voucher(this)');
    let order_index = document.createElement('div');
    order_index.setAttribute('class', 'col');
    order_index.innerHTML = index;
    new_order.appendChild(order_index);
    let setting_attr = ['r_number', 'r_date', 'r_keyword', 'r_doc_status', 'r_creator'];
    for(i=0; i<setting_attr.length; i++) {
        let new_col = document.createElement('div');
        new_col.setAttribute('class', 'col');
        new_col.setAttribute('style', 'margin-left:0.4%;');
        if (setting_attr[i] == 'r_doc_status') {
            if (order_info[setting_attr[i]] == '0') {
                new_col.innerHTML = '已完成';
            }else if(order_info[setting_attr[i]] == '1'){
                new_col.innerHTML = '处理中';
            }
        }else {
            new_col.innerHTML = order_info[setting_attr[i]];
        }
        new_order.appendChild(new_col);
    }
    return new_order;
}

function jump_to_voucher(order_col_element) {
    var order_id = order_col_element.getAttribute('id');
    return window.open('/voucherView?workorder_id=' + order_id);
}

function get_current_module_prefix() {
    let current_url = window.loacation.href;
    let module_str = String(current_url).search(/(?<=http:\/\/.*?.\/).*?(?=\/.*)/);
    return module_str;
}

function load_work_order_list(module_prefix) {
    var module_name = get_current_module_prefix();
    var workorder_request = new XMLHttpRequest();
    var list_data;
    workorder_request.onreadystatechange = function() {
        if (workorder_request.readyState == 4 && workorder_request.status == 200) {
                list_data = JSON.parse(workorder_request.responseText);
        }
    }
    workorder_request.open('get', '/getWorkOrderData/?module=' + module_name, false);
    workorder_request.send();
    if (list_data != []) {
        document.getElementById('no_record').setAttribute('style', 'display: none;');
        let work_sheet= document.getElementById('worksheet');
        for(j=0; j<list_data.length; j++) {
            console.log(list_data[j]['r_id'])
            let new_order_line = create_work_order_line(j + 1, list_data[j]);
            work_sheet.appendChild(new_order_line);
        }
    }
    return 0;
}

function append_module_spec() {
    var navi_bar = document.getElementById('top-navi');
    if (get_current_module_prefix() == 'monthlyClosing') {
        var mc_func_navi = document.createElement('div');
        mc_func_navi.setAttribute('class', 'function-navi');
        mc_func_navi.setAttribute('unselectable', 'on');
        mc_func_navi.setAttribute('onselectstart', 'return false;');
        mc_func_navi.setAttribute('onclick', "jump_to_url('base')");
        mc_func_navi.innerHTML = '基础设置';
        navi_bar.insertBefore(mc_func_navi, document.getElementById('help'));
    }
}