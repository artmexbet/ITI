function colorizePlaces() {
    let tables = document.getElementsByClassName('js-table-color-place');
    for(let table of tables) {
        for(let row of table.rows) {
            let elem = row.cells[0];
            if (elem === undefined) continue;
            let cell = elem.innerText;
            switch (cell) {
                case '1': row.classList.add('p1'); break;
                case '2': row.classList.add('p2'); break;
                case '3': row.classList.add('p3'); break;
            }
        }
    }
}

function orderNumber(a, b) {
    return b - a;
}

function colorizePlacesCols(cols) {
    let tables = document.getElementsByClassName('js-table-color-place');
    for(let cur_table of tables) {
        let table = cur_table.getElementsByTagName('tbody')[0];
        for(let col of cols) {
            let res = new Set();
            for(let row of table.rows) {
                let cell = row.cells[col].innerText;
                res.add(cell);
            }
            let results = Array.from(res);
            results.sort(orderNumber);
            for(let row of table.rows) {
                let cell = row.cells[col].innerText;
                let place = results.indexOf(cell) + 1;
                if (1 <= place && place <= 3) row.cells[col].classList.add('p' + place);
            }
        }
    }
}

function getRatingTableElement() {
    return document.getElementById('sorted-table').getElementsByTagName('tbody')[0];
}

function clearRatingTableElement() {
    let table = document.getElementById('sorted-table');
    let tbody = table.getElementsByTagName('tbody')[0];
    let new_tbody = document.createElement('tbody');
    table.replaceChild(new_tbody, tbody);
}

function generateRatingTable(lines, result_col, colorize=true, clss=[]) {
    clearRatingTableElement();
    let place = 0, cnt = 1, lastResult = null, rating_table = getRatingTableElement();
    for (let line of lines) {
        let row = document.createElement('tr'), result = line[result_col];
        if (clss.length) for (let cls of clss) row.classList.add(cls);
        if (lastResult !== result) { place = cnt; lastResult = result; }
        ++cnt;
        line[0] = place;
        for (let info of line) {
            let cell = document.createElement('td');
            cell.innerHTML = info;
            row.appendChild(cell);
        }
        rating_table.appendChild(row);
    }
    if (colorize) colorizePlaces();
}

function filterResults(class_col, result_col, colorize=true, clss=[]) {
    if (tableData.length) {
        let n = tableData[0].length;
        if (class_col < 0) class_col += n;
        if (result_col < 0) result_col += n;
    }
    let classes = new Set();
    let checkboxes = document.getElementsByName('class_value');
    for (let checkbox of checkboxes) {
        if (checkbox.checked) classes.add(checkbox.value);
    }
    let new_lines = [];
    for (let line of tableData) {
        let cell = line[class_col];
        if (class_col === null || classes.has(cell)) new_lines.push(line);
    }
    generateRatingTable(new_lines, result_col, colorize, clss);
}

function setChecked(cls, newChecked) {
    let checkboxes = document.getElementsByName('class_value');
    for (let checkbox of checkboxes) {
        let value = checkbox.value;
        if (cls === null || value.includes(cls)) checkbox.checked = newChecked;
    }
}

function generateAllTable() {
    document.getElementById('filter-all').click();
    document.getElementById('filter-do').click();
}

// rating_students.html

function compareStudentsResults(a, b) {
    let n = a.length;
    if (a[n - 1] !== b[n - 1]) return b[n - 1] - a[n - 1];
    if (a[3] !== b[3]) return a[3].localeCompare(b[3]);
    if (a[1] !== b[1]) return a[1].localeCompare(b[1]);
    if (a[2] !== b[2]) return a[2].localeCompare(b[2]);
    return 0;
}

function generateStudentsTableData() {
    let lines = [];
    for (let student_id in students) {
        let line = [], sum = 0;
        let result = student_id in results ? results[student_id] : {};
        line.push(0);
        for (let data of students[student_id]) line.push(data);
        for (let subject_id in subjects) {
            if (subject_id in result) {
                let data = result[subject_id];
                line.push(`${data[0]}&nbsp;(${data[1]})`);
                sum += data[0];
            }
            else line.push('-');
        }
        line.push(sum);
        if (sum > 0) lines.push(line);
    }
    lines.sort(compareStudentsResults);
    return lines;
}

// rating_classes.html

function compareClassesResults(a, b) {
    if (a[2] !== b[2]) return b[2] - a[2];
    if (a[1] !== b[1]) return a[1].localeCompare(b[1]);
    if (a[3] !== b[3]) return a[3] - b[3];
    return 0;
}

function generateClassesTableData() {
    let lines = [];
    for (let res of results) {
        let line = [0];
        for (let data of res) line.push(data);
        lines.push(line);
    }
    lines.sort(compareClassesResults);
    return lines;
}

// rating_teams.html

function compareTeamsResults(a, b) {
    let n = a.length;
    if (a[n - 1] !== b[n - 1]) return b[n - 1] - a[n - 1];
    if (a[1] !== b[1]) return a[1].localeCompare(b[1]);
    return 0;
}

function generateTeamsTableData() {
    let lines = [];
    for (let team_id in results) {
        let line = [0, teams[team_id]], sum = 0;
        for (let subject in subjects) {
            if (subject in results[team_id]) {
                line.push(results[team_id][subject]);
                sum += results[team_id][subject];
            } else line.push('-');
        }
        line.push(sum);
        lines.push(line);
    }
    lines.sort(compareTeamsResults);
    return lines;
}

// rating.html

function compareSuperChampionResults(a, b) {
    let n = a.length;
    return b[n - 1] - a[n - 1];
}

function generateSuperChampionTableData() {
    let lines = [];
    for (let student_id in results) {
        let line = [0], sum = 0;
        for (let data of students[student_id]) line.push(data);
        for (let data of results[student_id]) {
            sum = sum * 10 + data;
            line.push(data);
        }
        line.push(sum);
        lines.push(line);
    }
    lines.sort(compareSuperChampionResults);
    return lines.slice(0, 20);
}

// for many pages

function preparePageForConvert() {
    for (let elem of document.getElementsByClassName('js-table-for-excel-head-main')) {
        elem.setAttribute('style', 'display:none');
        for (let cell of elem.cells) {
            cell.setAttribute('data-f-sz', '20');
            cell.setAttribute('data-f-bold', 'true');
            cell.setAttribute('data-a-h', 'center');
        }
    }
    for (let elem of document.getElementsByClassName('js-table-for-excel-head-sub')) {
        for (let cell of elem.cells) {
            cell.setAttribute('data-b-a-s', 'thin');
            cell.setAttribute('data-f-sz', '14');
            cell.setAttribute('data-a-wrap', 'true');
            cell.setAttribute('data-f-bold', 'true');
        }
    }
    for (let elem of document.getElementsByClassName('js-table-for-excel-body')) {
        let color = null;
        if (elem.classList.contains("p1")) color = 'ffffd70';
        if (elem.classList.contains("p2")) color = 'ffc0c0c0';
        if (elem.classList.contains("p3")) color = 'ffefa540';
        for (let cell of elem.cells) {
            cell.setAttribute('data-b-a-s', 'thin');
            cell.setAttribute('data-f-sz', '14');
            if (color !== null) cell.setAttribute('data-fill-color', color);
        }
    }
}

TableToExcel.convert_many = function(file_name, data=[]) {
    let opts = {
        name: file_name + ".xlsx",
        autoStyle: false,
        sheet: {
            name: "default name"
        }
    };
    let wb = TableToExcel.initWorkBook();
    for (let page of data) {
        let name = page[0], table = page[1];
        opts.sheet.name = name;
        wb = TableToExcel.tableToSheet(wb, table, opts);
    }
    TableToExcel.save(wb, opts.name);
};

// subject_ind.html

function getSubjectExcel(year, subject) {
    let data = [], file_name = 'ИТИ ' + year + '. ' + subject;
    for (let cls of classes) {
        data.push([cls + ' класс', document.getElementById('table-c' + cls)]);
    }
    TableToExcel.convert_many(file_name, data);
}

// rating_classes.html

function getClassTable() {
    preparePageForConvert();
    return document.getElementById('sorted-table').cloneNode(true);
}

function getClassesExcel(year) {
    let data = [], file_name = 'ИТИ ' + year + '. Результаты классов';
    let filter_all = document.getElementById("filter-all"), filter_none = document.getElementById("filter-none"),
        filter_do = document.getElementById("filter-do"), table_name = document.getElementById('table-head-content');
    filter_all.click();
    filter_do.click();
    table_name.innerHTML = 'Общий';
    data.push(['Общий', getClassTable()]);
    for (let cls of classes) {
        let name = cls + ' класс';
        table_name.innerHTML = name;
        filter_none.click();
        setChecked(cls, true);
        filter_do.click();
        data.push([name, getClassTable()]);
    }
    filter_all.click();
    filter_do.click();
    TableToExcel.convert_many(file_name, data);
}
