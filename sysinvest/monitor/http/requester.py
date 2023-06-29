from sysinvest.common.plugin import MonitorPlugin, PluginResult
try:
    import requests

except:
    requests = None


def doRequest( plugin: MonitorPlugin, task_result, url, **kwargs ):
    r = requests.request( plugin.Attributes.get( 'method', 'GET' ).upper(), url, **kwargs )
    task_result.update( False, "Result code did not match" )
    result_code = plugin.Attributes.get( 'status_code', 200 )
    if r.status_code == result_code:
        content = plugin.Attributes.get( 'content' )
        plugin.log.info( r.content )
        if content is not None:
            if r.content != content:
                task_result.update( False, "Result code did match, but content failed" )

            else:
                task_result.update( True, "Result code did match and content" )

        else:
            task_result.update( True, "Result code did match" )

    else:
        task_result.update( True, f"Result code did match: {r.status_code} expected: {result_code}" )

    return