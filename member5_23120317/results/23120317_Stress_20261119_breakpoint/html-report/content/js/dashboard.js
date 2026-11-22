/*
   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
var showControllersOnly = false;
var seriesFilter = "";
var filtersOnlySampleSeries = true;

/*
 * Add header in statistics table to group metrics by category
 * format
 *
 */
function summaryTableHeader(header) {
    var newRow = header.insertRow(-1);
    newRow.className = "tablesorter-no-sort";
    var cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Requests";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 3;
    cell.innerHTML = "Executions";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 7;
    cell.innerHTML = "Response Times (ms)";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Throughput";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 2;
    cell.innerHTML = "Network (KB/sec)";
    newRow.appendChild(cell);
}

/*
 * Populates the table identified by id parameter with the specified data and
 * format
 *
 */
function createTable(table, info, formatter, defaultSorts, seriesIndex, headerCreator) {
    var tableRef = table[0];

    // Create header and populate it with data.titles array
    var header = tableRef.createTHead();

    // Call callback is available
    if(headerCreator) {
        headerCreator(header);
    }

    var newRow = header.insertRow(-1);
    for (var index = 0; index < info.titles.length; index++) {
        var cell = document.createElement('th');
        cell.innerHTML = info.titles[index];
        newRow.appendChild(cell);
    }

    var tBody;

    // Create overall body if defined
    if(info.overall){
        tBody = document.createElement('tbody');
        tBody.className = "tablesorter-no-sort";
        tableRef.appendChild(tBody);
        var newRow = tBody.insertRow(-1);
        var data = info.overall.data;
        for(var index=0;index < data.length; index++){
            var cell = newRow.insertCell(-1);
            cell.innerHTML = formatter ? formatter(index, data[index]): data[index];
        }
    }

    // Create regular body
    tBody = document.createElement('tbody');
    tableRef.appendChild(tBody);

    var regexp;
    if(seriesFilter) {
        regexp = new RegExp(seriesFilter, 'i');
    }
    // Populate body with data.items array
    for(var index=0; index < info.items.length; index++){
        var item = info.items[index];
        if((!regexp || filtersOnlySampleSeries && !info.supportsControllersDiscrimination || regexp.test(item.data[seriesIndex]))
                &&
                (!showControllersOnly || !info.supportsControllersDiscrimination || item.isController)){
            if(item.data.length > 0) {
                var newRow = tBody.insertRow(-1);
                for(var col=0; col < item.data.length; col++){
                    var cell = newRow.insertCell(-1);
                    cell.innerHTML = formatter ? formatter(col, item.data[col]) : item.data[col];
                }
            }
        }
    }

    // Add support of columns sort
    table.tablesorter({sortList : defaultSorts});
}

$(document).ready(function() {

    // Customize table sorter default options
    $.extend( $.tablesorter.defaults, {
        theme: 'blue',
        cssInfoBlock: "tablesorter-no-sort",
        widthFixed: true,
        widgets: ['zebra']
    });

    var data = {"OkPercent": 29.539365486178873, "KoPercent": 70.46063451382112};
    var dataset = [
        {
            "label" : "FAIL",
            "data" : data.KoPercent,
            "color" : "#FF6347"
        },
        {
            "label" : "PASS",
            "data" : data.OkPercent,
            "color" : "#9ACD32"
        }];
    $.plot($("#flot-requests-summary"), dataset, {
        series : {
            pie : {
                show : true,
                radius : 1,
                label : {
                    show : true,
                    radius : 3 / 4,
                    formatter : function(label, series) {
                        return '<div style="font-size:8pt;text-align:center;padding:2px;color:white;">'
                            + label
                            + '<br/>'
                            + Math.round10(series.percent, -2)
                            + '%</div>';
                    },
                    background : {
                        opacity : 0.5,
                        color : '#000'
                    }
                }
            }
        },
        legend : {
            show : true
        }
    });

    // Creates APDEX table
    createTable($("#apdexTable"), {"supportsControllersDiscrimination": true, "overall": {"data": [0.1991702491473239, 500, 1500, "Total"], "isController": false}, "titles": ["Apdex", "T (Toleration threshold)", "F (Frustration threshold)", "Label"], "items": [{"data": [0.8863693309947381, 500, 1500, "07 View Cart"], "isController": false}, {"data": [0.6202892431120025, 500, 1500, "04 Search Products"], "isController": false}, {"data": [0.6178547470253857, 500, 1500, "05 Product Detail"], "isController": false}, {"data": [0.6215385168668632, 500, 1500, "08 Checkout"], "isController": false}, {"data": [0.6189027588377216, 500, 1500, "02 View Order History"], "isController": false}, {"data": [0.8791761041902605, 500, 1500, "06 Add to Cart"], "isController": false}, {"data": [0.02652921737047189, 500, 1500, "01 Login"], "isController": false}, {"data": [0.620603191302823, 500, 1500, "03 Browse Products"], "isController": false}]}, function(index, item){
        switch(index){
            case 0:
                item = item.toFixed(3);
                break;
            case 1:
            case 2:
                item = formatDuration(item);
                break;
        }
        return item;
    }, [[0, 0]], 3);

    // Create statistics table
    createTable($("#statisticsTable"), {"supportsControllersDiscrimination": true, "overall": {"data": ["Total", 765531, 539398, 70.46063451382112, 561.2231888715114, 0, 30512, 476.0, 605.0, 2298.0, 21173.82000000371, 1697.6940681800036, 4512.612433632802, 154.2533229338536], "isController": false}, "titles": ["Label", "#Samples", "FAIL", "Error %", "Average", "Min", "Max", "Median", "90th pct", "95th pct", "99th pct", "Transactions/s", "Received", "Sent"], "items": [{"data": ["07 View Cart", 27937, 130, 0.46533271288971617, 430.86329956688184, 0, 16633, 344.0, 1149.7000000000044, 2066.0, 4042.970000000005, 62.104855991961514, 361.6662386750393, 21.537551932120817], "isController": false}, {"data": ["04 Search Products", 28419, 29, 0.1020444069108695, 1275.7054435412917, 0, 14567, 989.0, 4486.0, 6505.850000000002, 11125.990000000002, 63.088002202163985, 28.640924498880047, 13.245164105060093], "isController": false}, {"data": ["05 Product Detail", 28323, 30, 0.10592098294672174, 1313.4067012675162, 0, 14661, 998.0, 4584.9000000000015, 6603.850000000002, 11545.920000000013, 62.898626681116426, 28.486735148935367, 12.455953885749595], "isController": false}, {"data": ["08 Checkout", 27806, 108, 0.38840538013378406, 1168.441235704528, 3, 14367, 980.0, 3178.9000000000015, 5573.950000000001, 10697.980000000003, 62.15242386853352, 19.736680346190298, 27.539130604246015], "isController": false}, {"data": ["02 View Order History", 28599, 16, 0.055946012098325115, 1282.5191090597548, 3, 14535, 998.0, 4418.800000000003, 6451.800000000003, 11204.950000000008, 63.46814497873965, 816.5458521194608, 22.844201286634163], "isController": false}, {"data": ["06 Add to Cart", 28256, 275, 0.9732446206115515, 450.6078708946779, 0, 22989, 352.0, 1299.0, 2242.0, 3974.9900000000016, 62.7349284973679, 19.433256161704072, 27.056279581147326], "isController": false}, {"data": ["01 Login", 567676, 538783, 94.91030094631445, 398.191110774459, 0, 30512, 476.0, 589.0, 618.0, 18879.0, 1258.9172454781735, 3163.2628420511273, 17.520534918301088], "isController": false}, {"data": ["03 Browse Products", 28515, 27, 0.09468700683850605, 1269.4538313168541, 0, 14564, 987.0, 4433.800000000003, 6387.0, 11189.990000000002, 63.288189311919886, 76.60034109787198, 12.411016589429108], "isController": false}]}, function(index, item){
        switch(index){
            // Errors pct
            case 3:
                item = item.toFixed(2) + '%';
                break;
            // Mean
            case 4:
            // Mean
            case 7:
            // Median
            case 8:
            // Percentile 1
            case 9:
            // Percentile 2
            case 10:
            // Percentile 3
            case 11:
            // Throughput
            case 12:
            // Kbytes/s
            case 13:
            // Sent Kbytes/s
                item = item.toFixed(2);
                break;
        }
        return item;
    }, [[0, 0]], 0, summaryTableHeader);

    // Create error table
    createTable($("#errorsTable"), {"supportsControllersDiscrimination": false, "titles": ["Type of error", "Number of errors", "% in errors", "% in all samples"], "items": [{"data": ["Non HTTP response code: java.net.SocketException/Non HTTP response message: Connection reset", 110, 0.02039310490583947, 0.014369111113723677], "isController": false}, {"data": ["Non HTTP response code: java.net.BindException/Non HTTP response message: Address already in use: getsockopt", 3999, 0.741382059258655, 0.5223825031252817], "isController": false}, {"data": ["Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to localhost:3000 [localhost/127.0.0.1, localhost/0:0:0:0:0:0:0:1] failed: Connection refused: getsockopt", 535091, 99.201517247005, 69.89801849957742], "isController": false}, {"data": ["Non HTTP response code: java.net.SocketTimeoutException/Non HTTP response message: Read timed out", 198, 0.03670758883051105, 0.02586440000470262], "isController": false}]}, function(index, item){
        switch(index){
            case 2:
            case 3:
                item = item.toFixed(2) + '%';
                break;
        }
        return item;
    }, [[1, 1]]);

        // Create top5 errors by sampler
    createTable($("#top5ErrorsBySamplerTable"), {"supportsControllersDiscrimination": false, "overall": {"data": ["Total", 765531, 539398, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to localhost:3000 [localhost/127.0.0.1, localhost/0:0:0:0:0:0:0:1] failed: Connection refused: getsockopt", 535091, "Non HTTP response code: java.net.BindException/Non HTTP response message: Address already in use: getsockopt", 3999, "Non HTTP response code: java.net.SocketTimeoutException/Non HTTP response message: Read timed out", 198, "Non HTTP response code: java.net.SocketException/Non HTTP response message: Connection reset", 110, "", ""], "isController": false}, "titles": ["Sample", "#Samples", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors"], "items": [{"data": ["07 View Cart", 27937, 130, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to localhost:3000 [localhost/127.0.0.1, localhost/0:0:0:0:0:0:0:1] failed: Connection refused: getsockopt", 122, "Non HTTP response code: java.net.SocketException/Non HTTP response message: Connection reset", 8, "", "", "", "", "", ""], "isController": false}, {"data": ["04 Search Products", 28419, 29, "Non HTTP response code: java.net.SocketException/Non HTTP response message: Connection reset", 29, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["05 Product Detail", 28323, 30, "Non HTTP response code: java.net.SocketException/Non HTTP response message: Connection reset", 30, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["08 Checkout", 27806, 108, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to localhost:3000 [localhost/127.0.0.1, localhost/0:0:0:0:0:0:0:1] failed: Connection refused: getsockopt", 108, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["02 View Order History", 28599, 16, "Non HTTP response code: java.net.SocketException/Non HTTP response message: Connection reset", 16, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["06 Add to Cart", 28256, 275, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to localhost:3000 [localhost/127.0.0.1, localhost/0:0:0:0:0:0:0:1] failed: Connection refused: getsockopt", 275, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["01 Login", 567676, 538783, "Non HTTP response code: org.apache.http.conn.HttpHostConnectException/Non HTTP response message: Connect to localhost:3000 [localhost/127.0.0.1, localhost/0:0:0:0:0:0:0:1] failed: Connection refused: getsockopt", 534586, "Non HTTP response code: java.net.BindException/Non HTTP response message: Address already in use: getsockopt", 3999, "Non HTTP response code: java.net.SocketTimeoutException/Non HTTP response message: Read timed out", 198, "", "", "", ""], "isController": false}, {"data": ["03 Browse Products", 28515, 27, "Non HTTP response code: java.net.SocketException/Non HTTP response message: Connection reset", 27, "", "", "", "", "", "", "", ""], "isController": false}]}, function(index, item){
        return item;
    }, [[0, 0]], 0);

});
