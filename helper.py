import math as m

DOK_LIST = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09',
        'B10', 'B11', 'B12', 'B13', 'B14', 'B15', 'B16', 'B17', 'B18',
        'B19', 'B20', 'B21', 'B22', 'B23', 'B24', 'B25', 'B26', 'B27',
        'B28', 'B29', 'B30', 'B31', 'B32', 'B33', 'B34', 'B35', 'B36',
        'B37', 'B38', 'B39', 'B40', 'B41', 'B42', 'B43', 'Z15', 'Z42',
        'Z51', 'Z52', 'Z61', 'DC', 'DVB', 'YLB']

def Loc2LatLon(loc):
    lon = (ord(loc[0]) - ord('A')) * 20 - 180 + \
            (ord(loc[2]) - ord('0')) * 2 + \
            (ord(loc[4]) - ord('A') + 0.5) / 12

    lat = (ord(loc[1]) - ord('A')) * 10 - 90 + \
            (ord(loc[3]) - ord('0')) + \
            (ord(loc[5]) - ord('A') + 0.5) / 24

    return (lat, lon)

def Loc2LatLonRad(loc):
    return tuple([x * m.pi / 180 for x in Loc2LatLon(loc)])

def DistanceBetweenLocs(loc1, loc2):
    c1 = Loc2LatLonRad(loc1)
    c2 = Loc2LatLonRad(loc2)

    cse = m.sin(c1[0]) * m.sin(c2[0]) + m.cos(c1[0]) * m.cos(c2[0]) * m.cos(c1[1] - c2[1])

    return (m.acos(cse) * 180 / m.pi) * 111.1


if __name__ == "__main__":
    print(DistanceBetweenLocs("JN58QR", "JN59MO"))
    print(DistanceBetweenLocs("JN59NS", "JN59MO"))

def DOKCountsAsMulti(dok):
    return dok in DOK_LIST