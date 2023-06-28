# File exists plugin
This plugin checks if a file exists 


## Configuration
The following attributes must/may be present in the **attributes** section of the configuration:

Mandatory
* filename: string          /var/backup/backup-database.sql
  
Optional:  
* expire: string            a time string in format hh:mm:ss containing the hours, minutes, seconds how old the file may be. 
* minimal_size: integer     number of bytes the file at least must contain.


## Attributes
The following attributes are always present;
* exists: bool      True when the file exists, otherwise False
* expired: bool     True when the file exceed to the configured **expire** attribute from the configuration
                    When **expire** attribute is not configured the value shall be False
* size_valid: bool  False when the size of the file is less then the **minimal_size** attribute, otherwise True 
    
The following attributes are only present when the file exists;
* mode: int         Inode protection mode.  
* ino: int          Inode number.
* dev: int          Device inode resides on.
* nlink: int        Number of links to the inode.
* uid: int          User id of the owner.
* gid: int          Group id of the owner.          
* size: int         Size in bytes of a plain file; amount of data waiting on some special files.         
* atime: float      Time of last access.
* mtime: float      Time of last modification.
* ctime: float      The “ctime” as reported by the operating system. On some systems (like Unix) is the time of the last metadata change, and, on others (like Windows), is the creation time (see platform documentation for details).
* blocks: int       Number of blocks used on the device by the file.


## Default template
The following Mako template is used as a default;

```python
%if expired and exists:
The database file ${filename} is too old ${ datetime.fromtimestamp( ctime ).strftime( "%Y-%m-%d %H:%M:%S" ) }, must be less than 24 hours.
%elif exists:
The database file ${filename} exist and is valid.    
%else:
The database file ${filename} doesn t exist.
%endif
```