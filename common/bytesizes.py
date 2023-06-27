

def sizeof2shorthand( num: int, suffix: str = "B" ):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs( num ) < 1000.0:
            return f"{num:3.1f}{unit}{suffix}"

        num /= 1000.0

    return f"{num:.1f}Yi{suffix}"

def shorthand2sizeof( num: str, suffix: str = "B" ):
    number = 0.0
    sizedesc = ''
    for idx, ch in enumerate( num ):
        if not ch.isdigit() and ch not in (',', '.'):
            number = float( num[:idx].replace( ',', '.' ) )
            sizedesc = num[idx:]
            break

    if sizedesc == '':
        return int( number )


    for unit in ("Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        number *= 1000.0
        if sizedesc.startswith( unit ):
            break

    return int( number )


if __name__ == '__main__':
    short = sizeof2shorthand( 2957351410 )
    print( short )
    result = shorthand2sizeof( short )
    print( result )






