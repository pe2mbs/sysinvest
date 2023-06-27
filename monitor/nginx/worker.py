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
from common.osplatform import platform_select


service_name = platform_select(
    default = 'nginx',
    osx = 'org.macports.nginx',
)

hosts_available_dir = platform_select(
    debian='/etc/nginx/sites-available',
    centos='/etc/nginx/conf.d',
    mageia='/etc/nginx/conf.d',
    freebsd='/usr/local/etc/nginx/conf.d',
    arch='/etc/nginx/sites-available',
    osx='/opt/local/etc/nginx',
)

hosts_enabled_dir = platform_select(
    windows = 'C:/bin/nginx/conf/sites-enabled',
    default = '/etc/nginx/sites-enabled' )

supports_host_activation = platform_select(
    debian=True,
    arch=True,
    default=False,
)

configurable = True

main_conf_files = platform_select(
    debian = [ '/etc/nginx/nginx.conf', '/etc/nginx/proxy_params', '/etc/nginx/fastcgi_params',
               '/etc/nginx/scgi_params', '/etc/nginx/uwsgi_params'],
    centos = [ '/etc/nginx/nginx.conf', '/etc/nginx/fastcgi_params', '/etc/nginx/scgi_params',
               '/etc/nginx/uwsgi_params' ],
    windows = [ 'C:/bin/nginx/conf/nginx.conf', 'C:/bin/nginx/conf/proxy_params',
                'C:/bin/nginx/conf/fastcgi_params', 'C:/bin/nginx/conf/scgi_params',
                'C:/bin/nginx/conf/uwsgi_params' ],
    default=[],
)

