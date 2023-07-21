from datetime import datetime
from flask import Flask
from mako.template import Template

app = Flask( __name__ )


TASKS = [
    {
        'name':     'Hello',
        'status':   'OK',
        'message':  'All ok'
    },
    {
        'name':     'World',
        'status':   'FAILED',
        'message':  'Something Failed'
    },
    {
        'name':     'Program scheduler',
        'status':   'WARNING',
        'message':  'Wrong state'
    }
]

PAGE_TEMPLATE = """<html>
    <head>
        <meta charset="utf-8">
        <title>SysInvest infrastructor monitor</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
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

.status_green
{
    color:  green;
}

.status_yellow
{
    color:  DarkOrange;
}

.status_red
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
    background-color: WhiteSmoke;
}

.table-header
{
    background-color: Silver;
}

        </style>
        <script>
function autoRefresh() {
    window.location = window.location.href;
}
setInterval('autoRefresh()', ${interval} * 1000 );
        </script>
    </head>
    <body>
        <h1 class="center">SysInvest infrastructor monitor - ${ computername.lower() }</h1>
        <table class="width_100">
            <caption>Results updated: ${lastTime} - Update interval ${interval}</caption>
            <thead class="table-header">
                <tr class="table-header">
                    <td class="column_name">Component</td>
                    <td class="column_status">Status</td>
                    <td class="column_message">Message</td>
                </tr>
            </thead>
            <tbody>
%for task in tasks:
                <tr class="status_${task.get('color')}">
                    <td class="column_name">${task.get('name')}</td>
                    <td class="column_status">${task.get('status')}</td>
                    <td class="column_message">${task.get('message')}</td>
                </tr>
%endfor     
            <tbody>   
        </table>    
        <center>
            Configuration ${ configIndex } of ${ configDateTime }
        </center>
    </body>
</html>"""

@app.route("/")
def hello_world():
    COLORS = {
        'OK': 'green',
        'FAILED': 'red',
        'WARNING': 'yellow'
    }
    for task in TASKS:
        task[ 'color' ] = COLORS[ task[ 'status' ] ]

    return Template( PAGE_TEMPLATE ).render( tasks = TASKS,
                                             interval = 60,
                                             computername = 'TEST',
                                             lastTime = datetime.now(),
                                             configIndex = 1,
                                             configDateTime = datetime.now(),
    )


