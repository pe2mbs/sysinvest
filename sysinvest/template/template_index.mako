<html>
    <head>
        <meta charset="utf-8">
        <title>SysInvest infrastructor monitor</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <!-- <meta http-equiv="refresh" content="10"> -->
        <style>
.width_100
{
    width: 100%;
}

.column_name
{
    width: 35%;
    text-align: left;
}

.column_status
{
    width: 80px;
    text-align: center;
}

.status_True
{
    color:  green;
}

.status_False
{
    color:  red;
}

.column_message
{
    width: 60%;
    text-align: left;
}

.column_extras
{
    width: 30%;
    text-align: left;
}

.center
{
    text-align: center;
}

table, th, td {
    border: 1px solid gray;
    padding-left: 5px;
    padding-right: 5px;
    padding-top: 5px;
    padding-bottom: 5px;
}

table
{
    border-collapse: collapse;
    padding-left: 10px;
    padding-right: 10px;
    width: calc( 100% - 20px );
}

.table-header
{
    background-color: #DCDCDC;
}

        </style>
        <script>
function autoRefresh() {
    window.location = window.location.href;
}
setInterval('autoRefresh()', ${interval} * 1000 );
        </script>
    </head>
    <body class="width_100">
        <h1 class="center">SysInvest infrastructor monitor - ${ computername.lower() }</h1>
        <table>
            <caption>Results updated: ${lastTime} - Update interval ${interval}</caption>
            <thead>
                <tr class="table-header">
                    <th class="column_name">Name</th>
                    <th class="column_status">Result</th>
                    <th class="column_message">Message</th>
<!--                    <th class="column_extras">Extras</th>       -->
                </tr>
            </thead>
            <tbody>
%for name, result in pluginResults.items():
                <tr>
                    <td>${ name }</td>
                    <td class="column_status">
                        <span class="status_${result.Result}">${"OK" if result.Result else "FAILED" }</span>
                    </td>
                    <td>${ result.buildMessage( [ ( '\n', '<br/>\n' ) ] ) }</td>
                    <!-- <td>${ result.Details }</td> -->
                </tr>
%endfor
            </tbody>
        </table>
    </body>
</html>
