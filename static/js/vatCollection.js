function change_cell_status(cell_element) {
    if (cell_element.getAttribute('checked') == '1') {
        cell_element.setAttribute('checked', '0');
        cell_element.innerHTML = '';
        //cell_element.setAttribute('style', 'background-color: #e7e7e7');
    } else {
        cell_element.setAttribute('checked', '1');
        cell_element.innerHTML = '&radic;';
        //cell_element.setAttribute('style', 'background-color: rgb(155, 155, 155)');
    }
}

function build_data_matrix() {
    let main_table = document.getElementById('main-table');
    let account_list = ['2221.01', '2221.02', '2221.03.01', '2221.03.02', '2221.08.01', '2221.12', '2221.08.03'];
    let entity_list = ['1.01.054.001', '1.01.055', '1.01.052.001', '1.01.052.002', '1.01.059', '1.01.057', '1.01.070', '1.01.060', '1.01.071', '1.01.051', '1.01.062', '1.01.074', '1.01.101.0001', '1.01.101.0057.001', '1.01.065', '1.01.076', '1.01.056', '1.01.064', '1.01.004'];
    let entity_name_list = ['资产管理一部', '债券投资总部', '公司投顾', '固定收益承销', '机构客户部', '信用业务部', '资金管理部', '自营投资三', '自营投资四', '投资总部', '场外市场投资', '融资融券', '经管总部', '机构业务部', '零售客户部', '投行总部', '中小融', '研究所', '北京办事处']
    // 构造表头，科目列
    let table_head = document.createElement('div');
    table_head.setAttribute('class', 'table-head-row');
    let table_head_col = document.createElement('div');
    table_head_col.setAttribute('class', 'table-head-col');
    table_head_col.setAttribute('onclick', 'select_all()');
    table_head.appendChild(table_head_col);
    for (i=0; i<account_list.length; i++) {
        let table_head_unit = document.createElement('div');
        table_head_unit.setAttribute('class', 'table-head-account');
        table_head_unit.setAttribute('onclick', 'account_all_select(this)');
        table_head_unit.innerHTML = account_list[i];
        table_head_unit.setAttribute('id', account_list[i]);
        table_head.appendChild(table_head_unit);
    }
    main_table.appendChild(table_head);
    // 构造主体
    for (j=0; j<entity_list.length; j++) {
        let row = document.createElement('div');
        row.setAttribute('class', 'table-row');
        row.setAttribute('id', 'row_' +entity_list[j]);
        let row_head = document.createElement('div');
        row_head.setAttribute('class', 'table-head-col');
        row_head.setAttribute('onclick', 'entity_all_select(this)');
        row_head.innerHTML = entity_name_list[j];
        row_head.setAttribute('title', entity_list[j]);
        row_head.setAttribute('id', entity_list[j]);
        row.appendChild(row_head);
        for (i=0; i<account_list.length; i++) {
            let cell = document.createElement('div');
            cell.setAttribute('class', 'table-cell');
            cell.setAttribute('checked', '1');
            cell.innerHTML = '&radic;';
            cell.setAttribute('onclick', "change_cell_status(this)");
            cell.setAttribute('onmouseover', "highlight_info(this)");
            cell.setAttribute('onmouseout', "unhighlight_info(this)");
            cell.setAttribute('id', entity_list[j] + '_' + account_list[i]);
            row.appendChild(cell);
        }
        main_table.appendChild(row);
    }

}


function set_default_period() {
    // 猜测当前期间
    let curr_date = new Date();
    let curr_year = curr_date.getFullYear();
    let curr_month = curr_date.getMonth() + 1;
    // if (curr_month == 1) {
    //     curr_month = 12;
    //     curr_year--;
    // }else {
    //     curr_month--;
    // }
        
    let year_selector = document.getElementById('select_year');
    for (i=2021; i<2026; i++) {
        let option_year = document.createElement('option');
        option_year.setAttribute('value', String(i));
        option_year.innerHTML = String(i);
        if (curr_year == i) {
            option_year.setAttribute('selected', 'selected');
        }
        year_selector.appendChild(option_year);
    }
    let month_selector = document.getElementById('select_month');
    for (i=1; i<13; i++) {
        let option_month = document.createElement('option');
        option_month.setAttribute('value', String(i));
        option_month.innerHTML = String(i);
        if (curr_month == i) {
            option_month.setAttribute('selected', 'selected');
        }
        month_selector.appendChild(option_month);
    }

}