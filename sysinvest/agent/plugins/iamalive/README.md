# I'm alive plugin
This is a plugin reports the status if the SysInvest Infrastructure agent.

## Parameters
No parameters are defined.

## Attributes
The following attributes are always present;

* since              When the Monitor task was started
* lasttime           last time the process reported status
* tasks              number of running tasks
* hits               number of hits  
* percent            process CPU usage
* cpu                process on the CPU
* affinity           list with CPU numbers available to the process
* user               percent user CPU usage of the process
* system             percent system CPU usage of the process
* name               the process name full command line
* username           username under the process runs
* status             status of the process ("running","")
* created            datetime with the process was created
* ctx_switches       list with context switch info
* no_threads         number of threads used by the process
* read_cnt           number of read operations
* write_cnt          number of write operations  
* read_bytes         number of bytes read by the process
* write_bytes        number of bytes written by the process 
* rss                “Resident Set Size”, this is the non-swapped physical memory a process has used. On UNIX it matches “top“‘s RES column). On Windows this is an alias for wset field and it matches “Mem Usage” column of taskmgr.exe.   
* vms                “Virtual Memory Size”, this is the total amount of virtual memory used by the process. On UNIX it matches “top“‘s VIRT column. On Windows this is an alias for pagefile field and it matches “Mem Usage” “VM Size” column of taskmgr.exe.
* shared             shared memory size (Linux) memory that could be potentially shared with other processes. This matches “top“‘s SHR column).
* page_faults        The number of page faults (Windows). 
