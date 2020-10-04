# ARDIF v1 Specification

## General format
Messages are composed of nine fields. In order, they are: header, sender
callsign, recipient callsign, date, title, comment, height, width, and image
data. Fields are separated by a vertical pipe (|), and a vertical pipe is
appended at the end. There is no support for vertical pipes within any field.

## Date
Date is always UTC and is formatted as YYYY-MM-DD HH:MM:SS, using 24-hour
time.

## Image data
The image data section, almost always the longest, contains the encoded image
data. It is compressed using run-length encoding (RLE), as described below.

### Basic encoding
In its basic form, without compression, the image data is an ASCII string
with each character representing one pixel. The data is represented as all
rows concatenated. Each pixel has a shade of gray, represented by a number
from 0 to 63, inclusive; 0 is black and 63 is white. The following characters,
in sequence, are used to represent numbers 0 through 63:

    ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^*()_+

### Compression (Run-length encoding)
Digits within an image data string are treated specially. The, as a decimal
number, represent the number of times the next character should be repeated.
Groups of adjacent digits are considered a single number.

#### Example

    3Ab12&dd4a

is equivalent to

    AAAb&&&&&&&&&&&&ddaaaa
