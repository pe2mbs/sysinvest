import sensors
import traceback
from sysinvest.common.interfaces import ProcessData, TaskStatus, ExceptionData, SensorData, SensorsData
from sysinvest.common.plugin_agent import MonitorPluginAgent


class LinuxSensorsAgent( MonitorPluginAgent ):
    def __init__( self, parent, obj: dict ):
        super().__init__( parent, obj )
        return

    def print_feature( self, chip, feature ):
        sfs = list( sensors.SubFeatureIterator( chip, feature ) )  # get a list of all subfeatures

        label = sensors.get_label( chip, feature )

        skipname = len( feature.name ) + 1  # skip common prefix
        skipname = 0
        vals = [ sensors.get_value( chip, sf.number ) for sf in sfs ]

        if feature.type == sensors.feature.INTRUSION:
            # short path for INTRUSION to demonstrate type usage
            status = "alarm" if int( vals[ 0 ] ) == 1 else "normal"
            print( "\t" + label + "\t" + status )
            return

        names = [ sf.name[ skipname: ].decode( "utf-8" ) for sf in sfs ]
        data = list( zip( names, vals ) )

        str_data = ", ".join( [ e[ 0 ] + ": " + str( e[ 1 ] ) for e in data ] )
        print( "\t" + label + "\t" + str_data )
        return

    def makeSensor( self, chip, feature ) -> SensorData:
        sfs = list( sensors.SubFeatureIterator( chip, feature ) )  # get a list of all subfeatures
        label = sensors.get_label( chip, feature )
        vals = [ sensors.get_value( chip, sf.number ) for sf in sfs ]
        names = [ sf.name.decode( "utf-8" ) for sf in sfs ]
        data = list( zip( names, vals ) )
        kwargs = {}
        for name, value in data:
            #print( name, value )
            _, name = name.split( '_',1 )
            kwargs[ name ] = value

        return SensorData( package = sensors.get_adapter_name( chip.bus ),
                           sensor = label, **kwargs )

    def execute( self ) -> TaskStatus:
        super().execute()
        self.log.info( "Updating" )
        try:
            sensors.init()
            sensorList = SensorsData( features = [] )
            messages = []
            self.Status = TaskStatus.OK
            for chip in sensors.ChipIterator():
                # print( sensors.chip_snprintf_name( chip ) + " (" + sensors.get_adapter_name( chip.bus ) + ")" )
                for feature in sensors.FeatureIterator( chip ):
                    # self.print_feature( chip, feature )
                    sensor = self.makeSensor( chip, feature )
                    sensorList.features.append( sensor )
                    if type( sensor.crit ) == type( sensor.input ) and sensor.input > sensor.crit:
                        messages.append( f"sensor {sensor.package}.{sensor.sensor} = {sensor.input} \u2103 ** CRITICAL **" )
                        self.Status = TaskStatus.FAILED

                    else:
                        messages.append( f"sensor {sensor.package}.{sensor.sensor} = {sensor.input} \u2103" )

            self.Message = '\n'.join( messages )
            self.setServerData( sensorList )

        except Exception as exc:
            self.log.exception( "During lookup process" )
            self.Message = str( exc )
            self.Status = TaskStatus.FAILED
            self.setExceptionData( exc, traceback.extract_stack() )

        finally:
            sensors.cleanup()

        return self.Status
