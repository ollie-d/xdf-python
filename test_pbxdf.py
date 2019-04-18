import pbxdf
import struct
import numpy as np
data = b'\x00\x12\x10\x24\x00' + \
    b'\x01' + struct.pack('<d',12.5) + b'\x13\x10\x25\x00' + \
    b'\x00\x14\x10\x26\x00'
ts = np.zeros(3)
vals = np.zeros((3,2), dtype=np.int16)
pbxdf.read_tag3_h(data, len(data), ts, vals, 5, 1)
assert np.allclose(ts, [6., 12.5, 13.5])
assert np.all(np.equal(vals, [[4114, 36], [4115, 37], [4116, 38]])) 
