# sysInvest system monitoring and investigation



## Setup the service

```bash
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install sysinvest-X.YY.ZZ-py3-none-any.whl
    $ sudo cp server/sysinvest-server.service /etc/systemd/system/
    $ sudo mkdir /var/cache/sysinvest /var/log/sysinvest    
```

### Server configuration
This the default configuration for the server

```yaml
DEBUG: True
ASSETS_ROOT: /static/assets
# Security
SESSION_COOKIE_HTTPONLY: True
REMEMBER_COOKIE_HTTPONLY: True
REMEMBER_COOKIE_DURATION: 3600
SQLALCHEMY_DATABASE_URI: sqlite:////var/cache/sysinvest/server.sqlite3
SECRET_KEY: 'e^E)8hucY~+7dN)"'
HOST:   0.0.0.0
PORT:   5001
LOGGING:
    version: 1
    formatters:
        short:
            format: '%(message)s'
        brief:
            format: '%(asctime)s %(levelname)-8s "%(name)-25s" %(message)s'
            datefmt: '%Y-%m-%d %H:%M:%S'
        precise:
            format: '%(asctime)s %(levelname)-8s %(name)-15s %(message)s'
            datefmt: '%Y-%m-%d %H:%M:%S'
    handlers:
        console:
            class: logging.StreamHandler
            formatter: brief
            level: DEBUG
            stream: ext://sys.stdout
        file:
            class: logging.handlers.RotatingFileHandler
            formatter: precise
            filename: /var/log/sysinvest/server.log
            maxBytes: 10240000
            level: DEBUG
            backupCount: 3
        wsgi-access:
            class: logging.handlers.RotatingFileHandler
            formatter: precise
            filename: /var/log/sysinvest/access-log.log
            maxBytes: 10240000
            level: DEBUG
            backupCount: 3
    loggers:
        home:
            level: DEBUG
        wsgi:
            level: DEBUG
            propagate: false
            handlers:
            -    wsgi-access
    root:
        level: DEBUG
        handlers:
        -   console
        -   file
```

## Start en enable the server in systemd
```bash
    $ sudo systemctl start sysinvest-server.service
    $ sudo systemctl enable sysinvest-server.service
```



## Setup the agent
```bash
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install sysinvest-X.YY.ZZ-py3-none-any.whl
    $ cp server/sysinvest-agent.service /etc/systemd/system/
```

### Configuration agent
```yaml
collector:
    url:                        http://scuzzy.pe2mbs.nl:5001/api/agent

objects:
-   name:                       I am alive
    module:                     iamalive
    enabled:                    true
    cron:                       '*/1 * * * *'

-   name:                       Check server loads
    module:                     serverloads
    enabled:                    true
    cron:                       '*/1 * * * *'

-   name:                       Ethernet adaptor 1
    module:                     network
    enabled:                    true
    cron:                       '*/1 * * * *'
    interfaces:
    -   interface:              eth0
        address:                192.168.110.241
        hostname:               scuzzy.pe2mbs.nl
        media:                  100Mib

logging:
    version: 1
    formatters:
        short:
            format: '%(message)s'
        brief:
            format: '%(asctime)s %(levelname)-8s "%(name)-25s" %(message)s'
            datefmt: '%Y-%m-%d %H:%M:%S'
        precise:
            format: '%(asctime)s %(levelname)-8s %(name)-15s %(message)s'
            datefmt: '%Y-%m-%d %H:%M:%S'
    handlers:
        console:
            class : logging.StreamHandler
            formatter: brief
            level   : ERROR
            stream  : ext://sys.stdout
        file:
            class : logging.handlers.RotatingFileHandler
            formatter: precise
            filename: /var/log/sysinvest/agent.log
            maxBytes: 10240000
            level   : DEBUG
            backupCount: 3
    loggers:
        monitor:
            level: DEBUG
        collector:
            level: INFO
        plugin:
            level: DEBUG
        agent:
            level: DEBUG
    root:
        level: DEBUG
        handlers:
            -   console
            -   file
```

## Start en enable the agent in systemd

```bash
    $ sudo systemctl start sysinvest-agent.service
    $ sudo systemctl enable sysinvest-agent.service
```





