# Am I alive plugin
This is a plugin that report the status if the SysInvest Infrastructure monitor.

## Attributes
The following attributes are always present;

* uptime: datetime object   Number of days and hours the monitor is running.       
* since: deltatime object   When the monitor was started.
* passes: int               Number of times the checks are executed.
* tasks: int                Number of configured tasks

## Default template
The following Mako template is used as a default;

```python
SysInvest infrastructure monitor daemon is alive, running since ${since}
Uptime ${uptime} with no. ${passes} passes
```
