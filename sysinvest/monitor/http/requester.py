from sysinvest.common.plugin import MonitorPlugin, PluginResult
try:
    import requests

except:
    requests = None


def doRequest( plugin: MonitorPlugin, task_result, url, **kwargs ):
    r = requests.request( plugin.Attributes.get( 'method', 'GET' ).upper(), url, **kwargs )
    task_result.update( False, "Result code did not match" )
    if r.status_code == plugin.Attributes.get( 'status_code', 200 ):
        content = plugin.Attributes.get( 'content' )
        if content is not None:
            if r.content != content:
                task_result.update( False, "Result code did match, but content failed" )

            else:
                task_result.update( True, "Result code did match" )

        else:
            task_result.update( True, "Result code did match" )

    return