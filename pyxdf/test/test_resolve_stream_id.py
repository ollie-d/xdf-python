#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 10:53:49 2019

@author: rgugg
"""
from collections import OrderedDict, defaultdict
from pyxdf.resolve import parse_streams, match_streaminfo_with_parameters
# %%
fname = '/media/rgugg/tools/python3/example-files/minimal.xdf'

def test_minimal_loads():
    streams = parse_streams(fname)
    assert(
    streams == OrderedDict([(0,
             {'info': defaultdict(list,
                           {'name': ['SendDataC'],
                            'type': ['EEG'],
                            'channel_count': ['3'],
                            'nominal_srate': ['10'],
                            'channel_format': ['int16'],
                            'created_at': ['50942.723319709003'],
                            'desc': [None],
                            'uid': ['xdfwriter_11_int']})}),
             (46202862,
              {'info': defaultdict(list,
                           {'name': ['SendDataString'],
                            'type': ['StringMarker'],
                            'channel_count': ['1'],
                            'nominal_srate': ['10'],
                            'channel_format': ['string'],
                            'created_at': ['50942.723319709003'],
                            'desc': [None],
                            'uid': ['xdfwriter_11_int']})})])
        )
    
def test_selection_single():
        
    streams = parse_streams(fname)
    
    parameters = [{'name': 'SendDataC'}]
    sid = match_streaminfo_with_parameters(streams, parameters)
    assert sid ==[0]
    
    parameters = [{'name': 'SendDataString'}]
    sid = match_streaminfo_with_parameters(streams, parameters)
    assert sid == [ 46202862]
    
    parameters = [{'name': 'DoesnotWork'}]
    sid = match_streaminfo_with_parameters(streams, parameters)
    assert sid == []
    
    
def test_selection_multiple_returns():
   
    streams = parse_streams(fname)
    
    parameters = [{'name': 'SendDataC'}, {'name': 'SendDataString'}]
    sid = match_streaminfo_with_parameters(streams, parameters)
    assert sid ==[0, 46202862]
    
    parameters = [{'name': 'SendDataC'}, {'name': 'DoesnotWork'}, {'name': 'SendDataString'}]
    sid = match_streaminfo_with_parameters(streams, parameters)
    assert sid ==[0, 46202862]
    
def test_selection_multiple_parms():
    
    streams = parse_streams(fname)
    
    parameters = [{'name': 'SendDataC', 'type': 'EEG'}]
    sid = match_streaminfo_with_parameters(streams, parameters)
    assert sid ==[0]
    
    parameters = [{'name': 'SendDataC', 'type': 'Doesnotmatch'}]
    sid = match_streaminfo_with_parameters(streams, parameters)
    assert sid ==[]
    
    
    