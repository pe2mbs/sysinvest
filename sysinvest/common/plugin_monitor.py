from sysinvest.common import MonitorPluginAgent


class MonitorPluginCollector( MonitorPluginAgent ):
    def __init__( self, parent, config: dict ):
        super().__init__( parent, config )
        return

    @property
    def Template( self ):
        templateFile = self.Config.get( 'template_file' )
        if templateFile:
            self.log.info( f'Loading template file: {templateFile}' )
            with open( templateFile ) as stream:
                return stream.read()

        if hasattr( self, 'DEFAULT_TEMPLATE' ):
            default_templ = self.DEFAULT_TEMPLATE

        else:
            default_templ = "${name} => ${result} ${message}"

        return self.Config.get( 'template', default_templ ).replace( '\\n', '\n' )

