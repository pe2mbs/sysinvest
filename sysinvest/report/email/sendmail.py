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
from typing import Union, Optional
import os
from html2text import html2text
from sysinvest.common.plugin import PluginResult, MonitorPlugin, ReportPlugin
import smtplib
from email.message import EmailMessage
# For guessing MIME type based on file name extension
import mimetypes


class SendMail( ReportPlugin ):
    def __init__( self, config: dict ):
        super().__init__( 'enail', config )
        self.__items = []
        return

    def notify( self, result: PluginResult ):
        self.__items.append( result )
        return

    def publish( self ):
        # publish the message



        # Clear the list
        self.__items = []
        return

    def _sendmail( self, group: str, message: str, subject: Optional[str] = None, attachments: Optional[list] = None ):
        server = self.__cfg.get( 'smtp', {} )
        if server.get( 'secure', False ):
            session = smtplib.SMTP_SSL( host = server.get( 'host', 'localhost' ),
                                        port = server.get( 'port', 465 ),
                                        keyfile = server.get( 'keyfile', None ),
                                        certfile = server.get( 'certfile', None ) )

        else:
            session = smtplib.SMTP( host = self.__cfg.get( 'host', 'localhost' ),
                                    port = self.__cfg.get( 'port', 25 ) )

        msg = EmailMessage()
        if isinstance( subject, str ):
            msg[ 'Subject' ] = subject

        else:
            msg[ 'Subject' ] = 'SysInvest infrastructor monitor'

        msg[ 'From' ] = self.__cfg.get( 'sender', 'no-reply@sysinvest.org' )
        admin = self.__cfg.get( 'groups', {} ).get( 'admin', [] )
        addressees = self.__cfg.get( 'groups', {} ).get( group, [] )
        if len( addressees ) == 0:
            addressees = admin

        msg[ 'To' ] = ', '.join( addressees )
        if isinstance( attachments, list ):
            for filename in attachments:
                if not os.path.isfile( filename ):
                    continue

                ctype, encoding = mimetypes.guess_type( filename )
                if ctype is None or encoding is not None:
                    # No guess could be made, or the file is encoded (compressed), so
                    # use a generic bag-of-bits type.
                    ctype = 'application/octet-stream'

                maintype, subtype = ctype.split('/', 1)
                with open(filename, 'rb') as fp:
                    msg.add_attachment( fp.read(),
                                        maintype = maintype,
                                        subtype = subtype,
                                        filename = filename )
        if "<html>" in message:
            text = html2text( message )
            html = message

        else:
            text = message
            html = f"<html><head></head><body>{ message }</body></html>"

        # Set the TEXT content
        msg.set_content( text )
        # Add the TEXT as a HTML as well
        msg.add_alternative( html, subtype='html' )
        session.sendmail( msg )
        session.quit()
        return
