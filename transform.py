from pyproj import Transformer, CRS
from decimal import Decimal
import re

class CoordinateTransformer:
    def __init__(self, src_crs, dst_crs) -> None:
        self.src_crs = CRS(src_crs)
        self.dst_crs = CRS(dst_crs)
        self.transformer = Transformer.from_crs(self.src_crs, self.dst_crs)
    
    def transform(self, x, y):
        return self.transformer.transform(x, y)

def dec2dms(value):
    value = Decimal(value)
    degree, minutes = divmod(value, 1)
    minutes = abs(minutes * 60)
    minutes, seconds = divmod(minutes, 1)
    seconds = round(seconds*60, 4)
    return degree, minutes, seconds

def dms2dec(degree, minutes, seconds):
    return degree + minutes/60 + seconds/3600

def init_argparse():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.epilog = "Convert between different CRS. Input can be in decimal, or DD*MM'SS.ss'' format."
    parser.add_argument('x', help='x coordinate')
    parser.add_argument('y', help='y coordinate')
    parser.add_argument('--src', '-s', default='epsg:2178', help='source CRS')
    parser.add_argument('--dst', '-d', default='epsg:4258', help='destination CRS')
    parser.add_argument('--dst-dms', '-ddms', action=argparse.BooleanOptionalAction,
                        help='output CRS in degree, second, minute format if applicable')
    return parser

def splitdms(data):
    match = re.match(r"([+-]?\d{1,2})[°*](\d{1,2})'(\d{1,2}([,.]\d+)?)('')?", data)
    degree = Decimal(match.group(1))
    minutes = Decimal(match.group(2))
    seconds = Decimal(match.group(3).replace(',', '.'))
    return degree, minutes, seconds

def dms2string(degree, minutes, seconds):
    return f'{degree}°{minutes}\'{seconds}\'\''

if __name__ == '__main__':
    parser = init_argparse()
    args = parser.parse_args()

    transformer = CoordinateTransformer(args.src, args.dst)
    try:
        coordinates = transformer.transform(args.x, args.y)
    except TypeError:
        x = dms2dec(*splitdms(args.x))
        y = dms2dec(*splitdms(args.y))
        coordinates = transformer.transform(x, y)
    
    print(f'Transforming from "{transformer.src_crs.name}" to "{transformer.dst_crs.name}"'
          f' with accuracy of {transformer.transformer.accuracy}')
    
    if transformer.dst_crs.coordinate_system.name == 'ellipsoidal':
        if args.dst_dms:
            coordinates = list(map(lambda x: dms2string(*dec2dms(x)),
                coordinates))
            print(f'Coordinates: {coordinates[0]}, {coordinates[1]}')
        else:
            print(f'Coordinates: {coordinates[0]:.10f}, {coordinates[1]:.10f}')
    else:
        print(f'Coordinates: {coordinates[0]}, {coordinates[1]}')
