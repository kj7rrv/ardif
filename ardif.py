import cv2
import re
import numpy as np
import datetime

def _gs(pixel):
    return 0.229*pixel[2] + 0.587*pixel[1] + 0.114*pixel[0]

valcodes = { number: letter for number, letter in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+') }
numbers = {value:key for key, value in valcodes.items()}

def create_message(image, callsign, recipient, title, comment, color_divisor=1):
    if isinstance(image, str):
        image = cv2.imread(image)
    return f'ARDIF001|{callsign}|{recipient}|{datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}|{title}|{comment}|{_create_image(image, color_divisor)}|{callsign}'

def _create_image(image, color_divisor):
    height = image.shape[0]
    width = image.shape[1]
    output = ''
    for a in range(height):
        for b in range(width):
            output += valcodes[round(_gs(image[a,b])/(4*color_divisor))*color_divisor]
    return f'{height}|{width}|{_rle_encode(output)}'

def parse_message(text):
    header, sender, recipient, date, title, comment, height, width, image_data, _ = text.split('|')
    height = int(height)
    width = int(width)
    image_data = _rle_decode(image_data)
    image = np.zeros((height, width, 3, ), np.uint8)
    i = 0
    for a in range(height):
        for b in range(width):
            image[a, b] = ( numbers[image_data[i]]*4, ) * 3
            i += 1
    return {'sender': sender, 'recipient':recipient, 'date': date, 'title': title, 'comment': comment, 'image': image, }

def _rle_encode(text):
    strings = [[text[0], 1]]
    for color in text[1:]:
        if color == strings[-1][0]:
            strings[-1][1] += 1
        else:
            strings.append([color, 1])
    output = ''
    for string in strings:
        if string[1] <= 2:
            output += string[0] * string[1]
        else:
            output += str(string[1]) + string[0]
    return output

def _rle_decode(text):
    lexed = [int(text[0]) if text[0] in '0123456789' else text[0]]
    for char in text[1:]:
        if isinstance(lexed[-1], int) and char in '0123456789':
            lexed[-1] = int(str(lexed[-1]) + char)
        else:
            lexed.append(int(char) if char in '0123456789' else char)
    output = ''
    while len(lexed) != 0:
        item = lexed.pop(0)
        if isinstance(item, int):
            output += lexed.pop(0)*item
        else:
            output += item
    return output
