import os
from pathlib import Path
from .pyxdf import _xml2dict, _scan_forward, _read_varlen_int
import gzip
import struct
import logging
from collections import OrderedDict
import xml.etree.ElementTree as ET
from typing import List

__all__ = ['resolve_streams']

logger = logging.getLogger(__name__)
# %%
def resolve_streamids(filename:str, parameters:List[dict,]) -> List[int,]:
    streams = parse_streams(filename)
    sids = match_streaminfo_with_parameters(streams, parameters)
    return sids

def parse_streams(filename):    
    # number of bytes in the file for fault tolerance
    filesize = os.path.getsize(filename)

    # read file contents ([SomeText] below refers to items in the XDF Spec)
    filename = Path(filename)  # convert to pathlib object
    if filename.suffix == '.xdfz' or filename.suffixes == ['.xdf', '.gz']:
        f_open = gzip.open
    else:
        f_open = open
        
    streams = OrderedDict()
 #   fileheader = None
    with f_open(filename, 'rb') as f:
        # read [MagicCode]
        if f.read(4) != b'XDF:':
            raise Exception('not a valid XDF file: %s' % filename)

        # for each chunk...
        StreamId = None
        while True:

            # noinspection PyBroadException
            try:
                # read [NumLengthBytes], [Length]
                chunklen = _read_varlen_int(f)
            except Exception:
                if f.tell() < filesize - 1024:
                    logger.warn('got zero-length chunk, scanning forward to '
                                'next boundary chunk.')
                    _scan_forward(f)
                    continue
                else:
                    logger.info('  reached end of file.')
                    break

            # read [Tag]
            tag = struct.unpack('<H', f.read(2))[0]
            log_str = ' Read tag: {} at {} bytes, length={}'.format(tag, f.tell(), chunklen)
            if tag in [2, 3, 4, 6]:
                StreamId = struct.unpack('<I', f.read(4))[0]
                log_str += ', StreamId={}'.format(StreamId)

            logger.debug(log_str)

            # read the chunk's [Content]...
            if tag == 1:
                # read [FileHeader] chunk
                xml_string = f.read(chunklen - 2)
             #   fileheader = _xml2dict(ET.fromstring(xml_string))
            elif tag == 2:
                # read [StreamHeader] chunk...
                # read [Content]
                xml_string = f.read(chunklen - 6)
                decoded_string = xml_string.decode('utf-8', 'replace')
                hdr = _xml2dict(ET.fromstring(decoded_string))
                streams[StreamId] = hdr
                logger.debug('  found stream ' + hdr['info']['name'][0])
                # initialize per-stream temp data
                #temp[StreamId] = StreamData(hdr)
                
        return streams

def match_streaminfo_with_parameters(streams, parameters:List[dict]=None):    
    matches = []    
    for request in parameters:          
        for sid, val in streams.items():
            info = val['info']
            for key in request.keys():
                ismatch = info[key] == [request[key]]
                if not ismatch:
                    break
            if ismatch:
                matches.append(sid)          
            
    return list(set(matches)) #return unique values
        
        