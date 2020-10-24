# ARDIF v1 Specification

## General format
Messages are composed of ten fields. In order, they are: header, sender
callsign, recipient callsign, date, title, comment, height, width, image data,
and sender callsign (again). Fields are separated by a vertical pipe (`|`).
Vertical pipes are not permitted in any field.

## Header
The header is the string `ARDIF001`. Future versions of the format will
increment the number; the next version's header will be `ARDIF002`.
Implementations SHOULD attempt to decode other versions of ARDIF outside what
they are known to support.

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

    ABCDEFGHIJKLMNOPQR[TUVWXYZabcdefghijklmnopqr]tuvwxyz!@#$%^*()_+

`S` and `s` are replaced by `[` and `]`, respectively, to avoid having the
string `SOS` in the file.

### Compression (Run-length encoding)
Digits within an image data string are treated specially. They, as a decimal
number, represent the number of times the next character should be repeated.
Groups of adjacent digits are considered a single number.

#### Example

    3Ab12&dd4a

is equivalent to

    AAAb&&&&&&&&&&&&ddaaaa
