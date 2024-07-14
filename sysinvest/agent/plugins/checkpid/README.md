# Check PID plugin
This is a plugin reports the status of a process based of the PID file of the process. Optional executable 
and command-line may be provided.

## Process
Open the filename and read the PID number, and check if the PID number exist in the process list of the system.
When executable is defined, check if the executable names match.
When commandline is defined, check that the paramaters match in order. 

## Parameters
* filename: this is the filename of the PID file, that contains the PID value.
* executable: [Optional] the name of the executable, this is a string
* commandline: [Optional] the command line parameters, can only be used when execurable is defined. This may be a string or a list.
  * For string all parameter seperated with one space character
  * For a list, each parameter as a seperate item in the list 

## Attributes
On success the following parameters shall be present;
* since:             When the Monitor task was started
* lasttime:          last time the process reported status
* tasks:             number of running tasks
* hits:              number of failure hits  
* percent:           process CPU usage
* cpu:               process on the CPU
* affinity:          list with CPU numbers available to the process
* user:              percent user CPU usage of the process
* system:            percent system CPU usage of the process
* name:              the process name full command line
* username:          username under the process runs
* status:            status of the process ("running","")
* created:           datetime with the process was created
* ctx_switches:      list with context switch info
* no_threads:        number of threads used by the process
* read_cnt:          number of read operations
* write_cnt:         number of write operations  
* read_bytes         number of bytes read by the process
* write_bytes:       number of bytes written by the process 
* rss:               “Resident Set Size”, this is the non-swapped physical memory a process has used. On UNIX it matches “top“‘s RES column). On Windows this is an alias for wset field and it matches “Mem Usage” column of taskmgr.exe.   
* vms:               “Virtual Memory Size”, this is the total amount of virtual memory used by the process. On UNIX it matches “top“‘s VIRT column. On Windows this is an alias for pagefile field and it matches “Mem Usage” “VM Size” column of taskmgr.exe.
* shared:            shared memory size (Linux) memory that could be potentially shared with other processes. This matches “top“‘s SHR column).
* page_faults:       The number of page faults (Windows). 

On failure the following fields may be present
* exception:         The exception occurred 
* stacktrack:        The stack trace of the exception. 


# Configuration
For the attributes **name**, **module**, **group**, **enabled** and **cron** see the main documentation.      

## Example

```yaml
objects:
-   name:           Check the process for the webserver
    module:         checkpid
    group:          system
    enabled:        true
    cron:           '*/1 * * * *'
    filename:       C:\var\run\webserver.pid
    executable:     flask.exe
    commandline:    serve PRODUCTION
```


 