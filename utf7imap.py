

# Python 3
# http://d.hatena.ne.jp/itasuke/20120126/p1

import base64

def fix_base64(s):
    pad = b'=' * (((~len(s)) + 1) & 3)
    return s + pad

def modified_unbase64(s):
    s = fix_base64(s)
    return base64.b64decode(s, b'+,').decode('utf_16_be')

def modified_base64(s):
    enc = base64.b64encode(s.encode('utf_16_be'), b'+,')
    return enc.rstrip(b'=')

def decoder(s, errors=None):
    assert isinstance(s, bytes) or isinstance(s, memoryview)

    r = []
    decode = []

    for i in bytes(s):
        if i == ord(b'&') and not decode:
            decode.append(i)
        elif i == ord(b'-') and decode:
            if len(decode) == 1:
                r.append('&')
            else:
                r.append(modified_unbase64(bytes(decode[1:])))
            del decode[:]
        elif decode:
            decode.append(i)
        else:
            r.append(chr(i))

    if decode:
        r.append(modified_unbase64(bytes(r[1:])))
    return ''.join(r), len(s)

def encoder(s, erros=None):
    ret = bytearray()
    _in = []
    
    for c in s:
        if '\x20' <= c <= '\x7E':
            if _in:
                ret.extend(b'&' + modified_base64(''.join(_in)) + b'-')
                del _in[:]
            if c == '&':
                ret += b'&-'
            else:
                ret += c.encode()
        else:
            _in.append(c)

    if _in:
        ret.extend(b'&' + modified_base64(''.join(_in)) + b'-')

    return bytes(ret), len(ret)

