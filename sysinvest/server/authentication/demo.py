

sts20041 = [
    {
        "caption": "Check server loads",
        "status": "OK",
        "info": """Server loads normal
Memory usage: 54.7%
CPU usage 1 min: 10.54% / 5 min: 8.58% / 15 min: 15.44%"""
    },
    {
        "caption": "Disk usage C:",
        "status": "OK",
        "info": """Disk usage C: => True Filesystem OK:
C: freespace 10.6GiB
C: total disk space 64.1GiB"""
    }, 
    {
        "caption": "Disk usage D:",
        "status": "OK",
        "info": """Disk usage D: => True Filesystem OK:
D: freespace 98.5GiB
D: total disk space 268.4GiB"""
    }, 
    {
        "caption": "Disk usage E:",
        "status": "OK",
        "info": """Disk usage E: => True Filesystem OK:
E: freespace 1.1TiB
E: total disk space 3.3TiB"""
    }, 
    {
        "caption": "file exists TESTTOOL_PROD.sql not older than 24 hours",
        "status": "OK",
        "info": """The database file E:\var\backup\mariadb\TESTTOOL_PROD\TESTTOOL_PROD.zip exist and is valid.
The file size is valid, file has 109890458."""
    }, 
    {
        "caption": "Check REDIS serer trbtsas101.internal.zone",
        "status": "OK",
        "info": """Redis redis://********************@trbtsas101.internal.zone:6379/0 counter 10981 on token SYSINVEST-ac67ac3fcce549a4a216022cc3941dcd"""
    }, 
    {
        "caption": "Check HTTPS NGINX Development reverse proxy server",
        "status": "OK",
        "info": """Check HTTPS NGINX Development reverse proxy server => True Result code did match: 502 expected: 200"""
    }, 
    {
        "caption": "Check HTTPS NGINX Production reverse proxy server",
        "status": "OK",
        "info": """Check HTTPS NGINX Production reverse proxy server => True Result code did match"""
    }, 
    {
        "caption": "Check HTTP Production Flask server",
        "status": "OK",
        "info": """Check HTTP Production Flask server => True Result code did match"""
    }, 
    {
        "caption": "Production Testrun-web application",
        "status": "OK",
        "info": """Executable C:\Python38\Scripts\flask.exe with command line 'serve production' exist"""
    }, 
    {
        "caption": "Production scheduler",
        "status": "OK",
        "info": """Executable C:\Python38\python.exe with command line 'D:\srv\testrun-web\scheduler.py PRODUCTION' exist"""
    }, 
    {
        "caption": "Production mail reader process",
        "status": "OK",
        "info": """Executable C:\Python38\python.exe with command line 'D:\srv\testrun-web\mailreader.py' exist"""
    }, 
    {
        "caption": "Production mail process",
        "status": "OK",
        "info": """Executable C:\Python38\python.exe with command line 'D:\srv\testrun-web\mailprocess.py' exist"""
    }, 
    {
        "caption": "Production mail writer process",
        "status": "OK",
        "info": """Executable C:\Python38\python.exe with command line 'D:\srv\testrun-web\mailwriter.py' exist"""
    }, 
    {
        "caption": "Check production mail sent database",
        "status": "OK",
        "info": """Check production mail sent database => True"""
    }, 
    {
        "caption": "Check production answering machines",
        "status": "OK",
        "info": """Check production answering machines => True"""
    }, 
    {
        "caption": "Check production scheduler database",
        "status": "OK",
        "info": """Check production scheduler database => True"""
    }, 
    {
        "caption": "Check HTTP Development Flask server",
        "status": "FAILED",
        "info": """Check HTTP Development Flask server => False HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: / (Caused by NewConnectionError(': Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it'))"""
    }, 
    {
        "caption": "Developemnt Testrun-web application",
        "status": "FAILED",
        "info": """Executable C:\Python38\Scripts\flask.exe with command line 'serve staged' doesn't exist"""
    }
]

sts20044 = [
        {
        "caption": "Check server loads",
        "status": "OK",
        "info": """Server loads normal
Memory usage: 54.7%
CPU usage 1 min: 10.54% / 5 min: 8.58% / 15 min: 15.44%"""
    },
    {
        "caption": "Disk usage C:",
        "status": "OK",
        "info": """Disk usage C: => True Filesystem OK:
C: freespace 10.6GiB total disk space 64.1GiB"""
    }, 
    {
        "caption": "Disk usage D:",
        "status": "OK",
        "info": """Disk usage D: => True Filesystem OK:
D: freespace 273.5GiB total disk space 372.1GiB"""
    }, 
    {
        "caption": "Disk usage E:",
        "status": "OK",
        "info": """Disk usage E: => True Filesystem OK:
E: freespace 1.1TiB total disk space 3.3TiB"""
    }, 
]

sts10061 = [
    {
    "caption": "Check server loads",
    "status": "OK",
    "info": """Server loads normal
Memory usage: 54.7%
CPU usage 1 min: 10.54% / 5 min: 8.58% / 15 min: 15.44%"""
    },
    {
        "caption": "Disk usage C:",
        "status": "OK",
        "info": """Disk usage C: => True Filesystem OK:
C: freespace 10.6GiB total disk space 64.1GiB"""
    }, 
    {
        "caption": "Disk usage D:",
        "status": "OK",
        "info": """Disk usage D: => True Filesystem OK:
D: freespace 259.2GiB total disk space 372.1GiB"""
    }, 
    {
        "caption": "Disk usage E:",
        "status": "OK",
        "info": """Disk usage E: => True Filesystem OK:
E: freespace 1.1TiB
E: total disk space 3.3TiB"""
    }
    
]



HOSTS = {
    "sts20041.internal.zone": sts20041,
    "sts20044.internal.zone": sts20044,
    "sts10061.internal.zone": sts10061,
}