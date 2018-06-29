#!/usr/local/bin/python3
#
# Usage: parse.py WATCH_FILE
# Generates watch face image from passed watch file and saves it to 
# 'index.html'.

import ast
from math import sin, cos, pi, asin
from numbers import Number
import operator as op
import os
import re
import sys
from enum import Enum
from collections import namedtuple


BASE = 0.75
HEAD = f'<html>\n<svg height=300px width=300px>\n<g transform="translate(150,' \
       f' 150), scale({BASE})")>\n'
TAIL = "\n</g>\n</svg>\n</html>"
ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IIII', 5: 'V', 6: 'VI', 7: 'VII',
         8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII'}
WATCHES_DIR = 'watches/'
BORDER_FACTOR = 0.1

# class Shape(Enum):
#     line = get_line
#     rounded_line = get_rounded_line
#     two_lines = get_two_lines
#     circle = get_circle
#     number = get_number
#     triangle = get_triangle

Shape = Enum('Shape', ['line', 'rounded_line', 'two_lines', 'circle', 
                       'triangle', 'number'])

GrpRanges = namedtuple('GrpRanges', ['r', 'ranges'])
ObjParams = namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])

def main():
    if len(sys.argv) < 2:
        print('Missing watch file argument.', file=sys.stderr)
        sys.exit(1)
    watch_file = WATCHES_DIR + sys.argv[1]
    if not os.path.isfile(watch_file):
        print(f'File "{watch_file}" does not exist.', file=sys.stderr)
        sys.exit(2)
    watch_str = ''.join(read_file(watch_file))
    svg = get_svg(watch_str)
    write_to_file('index.html', HEAD + svg + TAIL)


def get_svg(watch_str):
    out = []
    dictionary, elements = ast.literal_eval(watch_str)
    elements = replace_matched_items(elements, dictionary)
    offset = 0
    rs = get_rs(elements)
    ranges = []
    for r, element in zip(reversed(rs), reversed(elements)):
        group = get_group(r, element[1:], ranges)
        out.extend(group)
    return ''.join(out)


def get_rs(elements):
    out = []
    r = 100
    offsets = [a[0] for a in elements]
    for offset in offsets:
        r -= offset
        out.append(r)
    return out


def get_group(r, elements, ranges):
    if not elements:
        return
    out = []
    ranges.append(GrpRanges(r, []))
    for element in elements:
        if len(element) < 3:
            out.append(get_circular_border(element, 100 - r))
            continue

        pos, shape, args = element
        shape = Shape[shape]
        fis = get_fis(pos)
        objects = get_objects(ranges, fis, shape, args, r)
        out.extend(objects)

        # width = get_angular_width(shape, args, r)
        # pos = get_positions(pos, width)
        # filtered_pos = filter_positions(pos, ranges[-1].ranges)
        # ranges[-1].ranges.extend(filtered_pos)
        # out += get_shapes(filtered_pos, shape, args, r)

    return out


def get_objects(ranges, fis, shape, args, r):
    out = (get_object(ranges, ObjParams(shape, r, fi, args)) \
                for fi in fis)
    return [a for a in out if a]


def get_object(ranges, prms):
    height = get_height(prms)
    max_height = get_max_height(ranges, prms)
    if height > max_height:
        update_height(prms.shape, prms.args, max_height)
    return None if range_ocupied(ranges, prms) else get_svg_el(prms, ranges)


def get_height(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    return prms.args[0]


def get_max_height(ranges, prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    return 100


def update_height(shape, args, height):
    return args


def range_ocupied(ranges, prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    return False


def get_svg_el(prms, occupied_ranges):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    DRAWERS = {Shape.line: get_line, Shape.rounded_line: get_rounded_line,
               Shape.two_lines: get_two_lines, Shape.circle: get_circle,
               Shape.number: get_number, Shape.triangle: get_triangle}
    fun = DRAWERS[prms.shape]
    ranges, svg = fun(prms)
    occupied_ranges[-1].ranges.extend(ranges)
    return svg


    # def get_shapes(pos, shape, args, offset):
    # length, width = args
    # ri = 100 - offset
    # ro = 100 - offset - length
    # args = ri, ro, width
    # return get_elements(pos, fun, args)


    # def get_elements(positions, drawer, args):
    #     """args = ri, ro, width"""
    #     out = ""
    #     position = position[0]
    #     deg = position * 2 * pi - pi / 2
    #     out += drawer([deg] + args)
    #     return out


    # def get_line(args):
    #     deg, ri, ro, width = args
    #     x1 = cos(deg) * ri
    #     x2 = cos(deg) * ro
    #     y1 = sin(deg) * ri
    #     y2 = sin(deg) * ro
    #     return _get_line(x1, y1, x2, y2, width)


    # def _get_line(x1, y1, x2, y2, width):
    #     return f'<line x1={x1} y1={y1} x2={x2} y2={y2} style="stroke-width:' \
    #            f'{width}; stroke:#000000"></line>'


##################


def get_line(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height, width = prms.args
    rad = prms.fi * 2 * pi - pi / 2
    x1 = cos(rad) * prms.r
    x2 = cos(rad) * (prms.r - height)
    y1 = sin(rad) * prms.r
    y2 = sin(rad) * (prms.r - height)
    ranges = get_ranges(prms.fi, compute_angular_width(width, 100 - prms.r))
    return ranges, _get_line(x1, y1, x2, y2, width)


def get_rounded_line(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height, width = prms.args
    rad = prms.fi * 2 * pi - pi / 2
    rot = (rad - pi / 2) / pi * 180

    ranges = get_ranges(prms.fi, compute_angular_width(width, 100 - prms.r))
    svg = f'<rect rx="{width/2}" y="{prms.r}" x="-{width/2}" ry="{width/2}" ' \
          f'transform="rotate({rot})" height="{height}" width="{width}">' \
          '</rect>'
    return ranges, svg


def get_two_lines(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    height, width, sep = prms.args
    rad = prms.fi * 2 * pi - pi / 2
    x1 = cos(rad) * ri
    x2 = cos(rad) * ro
    y1 = sin(rad) * ri
    y2 = sin(rad) * ro
    factor = width / 2 * (1 + sep)
    dx = sin(rad) * factor
    dy = cos(rad) * factor
    ranges = get_ranges(prms.fi, compute_angular_width(2*width+widht*sep, 100 - prms.r))
    svg = _get_line(x1 + dx, y1 + dy, x2 + dx, y2 + dy, width) + \
          _get_line(x1 - dx, y1 - dy, x2 - dx, y2 - dy, width)
    return ranges, svg


def get_circle(prms):
    diameter = prms.args[0]
    rad = prms.fi * 2 * pi - pi / 2
    cx = cos(rad) * (prms.r - diameter / 2)
    cy = sin(rad) * (prms.r - diameter / 2)
    ranges = get_ranges(prms.fi, compute_angular_width(diameter, 100 - prms.r))
    svg = f'<circle cx={cx} cy={cy} r={diameter / 2} style="stroke-width: 0; fill: rgb(0, 0, ' \
          '0);"></circle>'
    return ranges, svg


def get_triangle(prms):
    height, width = prms.args
    rad = prms.fi * 2 * pi - pi / 2
    x1 = (cos(rad) * prms.r) - (sin(rad) * width / 2)
    y1 = (sin(rad) * prms.r) + (cos(rad) * width / 2)
    x2 = (cos(rad) * prms.r) + (sin(rad) * width / 2)
    y2 = (sin(rad) * prms.r) - (cos(rad) * width / 2)
    x3 = cos(rad) * prms.r - height
    y3 = sin(rad) * prms.r - height
    ranges = get_ranges(prms.fi, compute_angular_width(width, 100 - prms.r))
    svg = f'<polygon points="{x1},{y1} {x2},{y2} {x3},{y3}" />'
    return ranges, svg


def get_number(prms):
    """namedtuple('ObjParams', ['shape', 'r', 'fi', 'args'])"""
    font = ''
    if len(prms.args) == 3:
        size, kind, orient = prms.args
    else:
        size, kind, orient, font = prms.args
    rad = prms.fi * 2 * pi - pi / 2
    x = cos(rad) * (prms.r - size / 2)
    y = sin(rad) * (prms.r - size / 2)
    i = get_num_str(kind, rad)
    rad = prms.fi * 2 * pi - pi / 2
    rot = get_num_rotation(orient, rad)
    ranges = get_ranges(prms.fi, compute_angular_width(size, 100 - prms.r))
    svg = f'<g transform="translate({x}, {y})"><text transform="rotate({rot}' \
          f')" class="title" fill="#111111" fill-opacity="0.9" font-size=' \
          f'"{size}" font-weight="bold" font-family="{font}" ' \
          f'alignment-baseline="middle" text-anchor="middle">{i}</text></g>'
    return ranges, svg


##################


def get_fis(pos):
    if isinstance(pos, set):
        return pos
    elif isinstance(pos, Number):
        return [i / pos for i in range(pos)]
    elif isinstance(pos, list):
        n = pos[0]
        start = 0
        if len(pos) == 2:
            end = pos[1]
        else:
            start = pos[1]
            end = pos[2]
        return [i/n for i in range(n) if start <= i/n <= end]


def get_positions(pos, width):
    if isinstance(pos, set):
        return get_positions_set(pos, width)
    elif isinstance(pos, Number):
        return get_positions_num(pos, width)
    elif isinstance(pos, list):
        return get_positions_list(pos, width)


def get_circular_border(element, ver_pos):
    stroke_width = element[1][0]
    return f'<circle cx=0 cy=0 r={100-ver_pos} style=" stroke-width: ' \
           f'{stroke_width}; stroke: rgb(0,0,0); fill: rgba(0,0,0,0)' \
           ';"></circle>'


def filter_positions(positions, filled_pos):
    out = []
    filled_ranges = [get_ranges(pos, width) for pos, width in filled_pos]
    filled_ranges = [item for sublist in filled_ranges for item in sublist]
    for a_pos in positions:
        pos, width = a_pos

        if all(not rng_intersects(rng, filled_ranges) for rng in
               get_ranges(pos, width)):
            out.append(a_pos)
    return out


def rng_intersects(rng, filled_ranges):
    start, end = rng
    for fil_range in filled_ranges:
        f_start, f_end = fil_range
        if (f_start < start < f_end) or (f_start < end < f_end) or \
            (start < f_start and end > f_end):
            return True
    return False


def get_ranges(pos, width):
    border = width * BORDER_FACTOR
    start = (pos - width / 2) - border
    end = (pos + width / 2) + border
    if start < 0:
        return [[start + 1, 1], [0, end]]
    if end > 1:
        return [[start, 1], [0, end - 1]]
    return [[start, end]]


def get_angular_width(shape, args, offset):
    if shape == Shape.line:
        _, width = args
        return compute_angular_width(width, offset)
    if shape == Shape.rounded_line:
        _, width = args
        return compute_angular_width(width, offset)
    elif shape == Shape.two_lines:
        _, width, factor = args
        return compute_angular_width(2 * width + width * factor, offset)
    elif shape == Shape.circle:
        diameter = args[0]
        return compute_angular_width(diameter, offset)
    elif shape == Shape.number:
        size = args[0]
        return compute_angular_width(size, offset)
    elif shape == Shape.triangle:
        _, width = args
        return compute_angular_width(width, offset)
    return ""


def compute_angular_width(width, offset):
    r = 100 - offset
    a_sin = width / r
    # print(width, offset, r, a_sin)
    return asin(a_sin) / (2 * pi)


def get_positions_num(n, width):
    return get_positions_set([i / n for i in range(n)], width)


def get_positions_list(args, width):
    n = args[0]
    start = 0
    if len(args) == 2:
        end = args[1]
    else:
        start = args[1]
        end = args[2]
    positions = [i/n for i in range(n) if start <= i/n <= end]
    return get_positions_set(positions, width)


def get_positions_set(positions, width):
    return [[pos, width] for pos in positions]


# class Line:
#     def __init__(s, pos, offset, args):
#         s.pos = pos
#         s.offset = offset
#         s.args = args
#     def get_width(s):
#         pass
#     def get_height(s):
#         pass
#     def get_range(s):
#         pass
#     def __str__(s):
#         pass


def get_shapes(pos, shape, args, offset):
    if shape == Shape.line:
        length, width = args
        return get_elements(pos, get_line,
                            [100 - offset, 100 - offset - length, width])
    if shape == Shape.rounded_line:
        length, width = args
        return get_elements(pos, get_rounded_line,
                            [100 - offset, 100 - offset - length, width])
    elif shape == Shape.two_lines:
        length, width, factor = args
        return get_elements(pos, get_two_lines,
                            [100 - offset, 100 - offset - length, width,
                             factor])
    elif shape == Shape.circle:
        diameter = args[0]
        return get_elements(pos, get_circle, [100 - offset, diameter])
    elif shape == Shape.number:
        # diameter = args[0]
        # kind = args[1]
        # orient = args[2]
        return get_elements(pos, get_number, [100 - offset] + args)
    elif shape == Shape.triangle:
        length, width = args
        return get_elements(pos, get_triangle,
                            [100 - offset, 100 - offset - length, width])
    return ""


def get_elements(positions, drawer, args):
    out = ""
    for position in positions:
        position = position[0]
        deg = position * 2 * pi - pi / 2
        out += drawer([deg] + args)
    return out


# def get_number(args):
#     font = ''
#     if len(args) == 5:
#         deg, ro, diameter, kind, orient = args
#     else:
#         deg, ro, diameter, kind, orient, font = args
#     x = cos(deg) * (ro - diameter / 2)
#     y = sin(deg) * (ro - diameter / 2)
#     i = get_num_str(kind, deg)
#     rot = get_num_rotation(orient, deg)
#     return f'<g transform="translate({x}, {y})"><text transform="rotate({rot}' \
#            f')" class="title" fill="#111111" fill-opacity="0.9" font-size=' \
#            f'"{diameter}" font-weight="bold" font-family="{font}" ' \
#            f'alignment-baseline="middle" text-anchor="middle">{i}</text></g>'


def get_num_str(kind, deg):
    if kind == 'minute':
        return get_minute(deg)
    if kind == 'roman':
        hour = get_hour(deg)
        return ROMAN[hour]
    else:
        return get_hour(deg)


def get_num_rotation(orient, deg):
    if orient == "horizontal":
        return 0
    elif orient == "rotating":
        return (deg + pi / 2) / pi * 180
    else:
        delta = pi if 0 < deg < pi else 0
        return (deg + pi / 2 + delta) / pi * 180


def get_hour(deg):
    return deg_to_time(deg, 12)


def get_minute(deg):
    return deg_to_time(deg, 60)


def deg_to_time(deg, factor):
    i = (deg + pi / 2) / (2 * pi) * factor
    i = round(i)
    if i == 0:
        i = factor
    return i


# def get_circle(args):
#     deg, ro, diameter = args
#     cx = cos(deg) * (ro - diameter / 2)
#     cy = sin(deg) * (ro - diameter / 2)
#     return '<circle cx={} cy={} r={} style="stroke-width: 0; fill: rgb(0, 0, ' \
#            '0);"></circle>'.format(cx, cy, diameter / 2)


# def get_line(args):
#     deg, ri, ro, width = args
#     x1 = cos(deg) * ri
#     x2 = cos(deg) * ro
#     y1 = sin(deg) * ri
#     y2 = sin(deg) * ro
#     return _get_line(x1, y1, x2, y2, width)


# def get_rounded_line(args):
#     deg, ri, ro, width = args
#     deg = (deg - pi / 2) / pi * 180
#     return f'<rect rx="{width/2}" y="{ro}" x="-{width/2}" ry="{width/2}" ' \
#            f'transform="rotate({deg})" height="{ri-ro}" width="{width}"></rect>'


# def get_two_lines(args):
#     deg, ri, ro, width, sep = args
#     x1 = cos(deg) * ri
#     x2 = cos(deg) * ro
#     y1 = sin(deg) * ri
#     y2 = sin(deg) * ro
#     factor = width / 2 * (1 + sep)
#     dx = sin(deg) * factor
#     dy = cos(deg) * factor
#     return _get_line(x1 + dx, y1 + dy, x2 + dx, y2 + dy, width) + \
#         _get_line(x1 - dx, y1 - dy, x2 - dx, y2 - dy, width)


def _get_line(x1, y1, x2, y2, width):
    return f'<line x1={x1} y1={y1} x2={x2} y2={y2} style="stroke-width:' \
           f'{width}; stroke:#000000"></line>'


# def get_triangle(args):
#     deg, ro, ri, width = args
#     x1 = (cos(deg) * ro) - (sin(deg) * width / 2)
#     y1 = (sin(deg) * ro) + (cos(deg) * width / 2)
#     x2 = (cos(deg) * ro) + (sin(deg) * width / 2)
#     y2 = (sin(deg) * ro) - (cos(deg) * width / 2)
#     x3 = cos(deg) * ri
#     y3 = sin(deg) * ri
#     return '<polygon points="{},{} {},{} {},{}" />'.format(x1, y1, x2, y2, x3,
#                                                            y3)


###
##  DICT SUB
#

def replace_matched_items(elements, dictionary):
    out = []
    for element in elements:
        if type(element) is set:
            out.append(replace_in_set(element, dictionary))
        elif type(element) is list:
            out.append(replace_matched_items(element, dictionary))
        else:
            out.append(get_value_of_exp(element, dictionary))
    return out


def replace_in_set(elements, dictionary):
    return {get_value_of_exp(element, dictionary) for element in elements}


def get_value_of_exp(exp, dictionary):
    if isinstance(exp, Number):
        return exp
    for key, value in dictionary.items():
        exp = exp.replace(key, str(value))
    if re.search('[a-zA-Z]', exp):
        return exp
    return eval_expr(exp)



# class Shape(Enum):
#     line = get_line
#     rounded_line = get_rounded_line
#     two_lines = get_two_lines
#     circle = get_circle
#     number = get_number
#     triangle = get_triangle

# class Shape(Enum):
#     line = 1
#     rounded_line = 2
#     two_lines = 3
#     circle = 4
#     number = 5
#     triangle = 6

###
##  EVAL
#

operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}


def eval_expr(expr):
    return eval_(ast.parse(expr, mode='eval').body)


def eval_(node):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp):
        return operators[type(node.op)](eval_(node.operand))
    else:
        raise TypeError(node)


###
##  UTIL
#

def read_file(filename):
    with open(filename, encoding='utf-8') as file:
        return file.readlines()


def write_to_file(filename, text):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)


if __name__ == '__main__':
    main()
