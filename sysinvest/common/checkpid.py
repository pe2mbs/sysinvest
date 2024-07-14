#
#   sysinvest - Python system monitor and investigation utility
#   Copyright (C) 2022-2023 Marc Bertens-Nguyen m.bertens@pe2mbs.nl
#
#   This library is free software; you can redistribute it and/or modify
#   it under the terms of the GNU Library General Public License GPL-2.0-only
#   as published by the Free Software Foundation; only version 2 of the
#   License.
#
#   This library is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#   Library General Public License for more details.
#
#   You should have received a copy of the GNU Library General Public
#   License GPL-2.0-only along with this library; if not, write to the
#   Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301 USA
#
import os
from datetime import datetime, timezone
import platform
import psutil
from sysinvest.common.interfaces import ProcessData


def checkPid( pid: int ):
    return psutil.pid_exists( pid )


def checkPidFilename( filename: str ):
    with open( filename ) as stream:
        pid_data = stream.read()

    pid = int( pid_data.strip( '\r\n ' ) )
    return checkPid( pid ), pid


def updateProcessData( process, data: ProcessData ):
    linux = platform.system() == 'Linux'
    windows = platform.system() == 'Windows'

    cpu_times = process.cpu_times()
    data.percent = process.cpu_percent()
    data.cpu = process.cpu_num()
    data.affinity = process.cpu_affinity()
    data.user = cpu_times.user
    data.system = cpu_times.system
    # data.idle': cpu_times.idle
    data.name = f"{' '.join( process.cmdline() )}"
    data.username = process.username()
    data.status = psutil.STATUS_RUNNING if windows else process.status()
    data.created = datetime.fromtimestamp( process.create_time(), tz = timezone.utc )
    data.ctx_switches = [ int( v ) for v in process.num_ctx_switches() ]  # to avoid pydantic warnings
    data.no_threads = process.num_threads()
    # On linux access to another users process is not allowed when running is user space
    if linux and os.getuid() == 0 or windows:
        try:
            io_cnt = process.io_counters()
            data.read_cnt = io_cnt.read_count
            data.write_cnt = io_cnt.write_count
            data.read_bytes = io_cnt.read_bytes
            data.write_bytes = io_cnt.write_bytes

        except PermissionError:
            pass

        except Exception:
            raise

        mem_info = process.memory_full_info() if linux else process.memory_info()
        data.rss = mem_info.rss
        data.vms = mem_info.vms
        if linux:
            data.shared = mem_info.shared

        elif windows:
            data.pfaults = mem_info.num_page_faults

    return
