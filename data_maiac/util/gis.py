import pyproj

sinu = pyproj.Proj("+proj=sinu +a=6371007.181 +b=6371007.181 +units=m")

if __name__ == '__main__':
    x = -104.43258313171
    y = 39.9999999964079
    e, n = sinu(x, y)
    UpperLeftPointMtrs = (-8895604.157333, 4447802.078667)
    assert int(e) == int(UpperLeftPointMtrs[0]) and int(n) == int(UpperLeftPointMtrs[1])
