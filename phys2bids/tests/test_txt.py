import os
from pkg_resources import resource_filename
from phys2bids.interfaces import txt
from pytest import raises
import sys
import io


def test_read_header_and_channels():
    test_filename = 'Test_belt_pulse_samefreq.txt'  # this file has a comment and extra tab
    test_path = resource_filename('phys2bids', 'tests/data')
    test_full_path = os.path.join(test_path, test_filename)
    chtrig = 2
    header, channels = txt.read_header_and_channels(test_full_path, chtrig)
    assert len(header) == 16  # check proper header lenght
    assert channels == 1336816  # check proper number of timepoints
    assert len(channels[6]) == 6  # check the comment has been eliminated
    assert len(header[-1]) == 6  # check extra line is deleted


def test_populate_phys_input():
    # testing error for files without header
    test_filename = 'Test_belt_pulse_samefreq_no_header.txt'
    test_path = resource_filename('phys2bids', 'tests/data')
    test_full_path = os.path.join(test_path, test_filename)
    chtrig = 2
    with raises(AttributeError) as errorinfo:
        txt.populate_phys_input(test_full_path, chtrig)
    assert 'not supported' in str(errorinfo.value)
    # testing for AcqKnoledge files
    test_filename = 'Test_belt_pulse_samefreq.txt'
    test_full_path = os.path.join(test_path, test_filename)
    stdout = sys.stdout
    sys.stdout = io.StringIO()
    txt.populate_phys_input(test_full_path, chtrig)
    # testing for labchart files
    test_filename = 'Test_2minRest_trig_multifreq_header_no_comment.txt'
    test_full_path = os.path.join(test_path, test_filename)
    txt.populate_phys_input(test_full_path, chtrig)
    output = sys.stdout.getvalue()
    sys.stdout = stdout
    # check the printing output according to each format
    output = output.split('\n')
    assert 'AcqKnowledge format' in output[0]
    assert 'Labchart format' in output[2]


def test_labchart_read():
    # test file without header
    test_path = resource_filename('phys2bids', 'tests/data')
    test_filename = 'Test_2minRest_trig_multifreq_header_no_comment.txt'
    test_full_path = os.path.join(test_path, test_filename)
    chtrig = 1
    header, channels = txt.read_header_and_channels(test_full_path, chtrig)
    with raises(AttributeError) as errorinfo:
        txt.labchart_read(channels, chtrig)
    assert 'not supported' in str(errorinfo.value)
    # test file with header and seconds as unit:
    phys_obj = txt.labchart_read(channels, chtrig, header)
    assert phys_obj.freq[0] == 100
    # test when units are min:
    header[0][1] = '0.001 min'
    phys_obj = txt.labchart_read(channels, chtrig, header)
    assert phys_obj.freq[0] == 16.666666666666668
    # test when units are hr:
    header[0][1] = '0.001 hr'
    phys_obj = txt.labchart_read(channels, chtrig, header)
    assert phys_obj.freq[0] == 0.2777777777777778
    # test when units are ms:
    header[0][1] = '1 ms'
    phys_obj = txt.labchart_read(channels, chtrig, header)
    assert phys_obj.freq[0] == 100
    # test when units are µs:
    header[0][1] = '1000 µs'
    phys_obj = txt.labchart_read(channels, chtrig, header)
    assert phys_obj.freq[0] == 100
    # test when units are not valid:
    header[0][1] = ' 1 gHz'
    with raises(AttributeError) as errorinfo:
        phys_obj = txt.labchart_read(channels, chtrig, header)
    assert 'not in a valid LabChart' in str(errorinfo.value)


def test_acq_read():
    # test file without header
    test_path = resource_filename('phys2bids', 'tests/data')
    test_filename = 'Test_belt_pulse_samefreq.txt'
    test_full_path = os.path.join(test_path, test_filename)
    chtrig = 1
    header, channels = txt.read_header_and_channels(test_full_path, chtrig)
    with raises(AttributeError) as errorinfo:
        txt.acq_read(channels, chtrig)
    assert 'not supported' in str(errorinfo.value)
    # test when units are msec:
    phys_obj = txt.acq_read(channels, chtrig, header)
    assert phys_obj.freq[0] == 10000
    # test when units are msec:
    header[1][0] = '0.01 sec/sample'
    phys_obj = txt.acq_read(channels, chtrig, header)
    assert phys_obj.freq[0] == 100
    # test when units are in µsec:
    header[1][0] = '1 µsec/sample'
    phys_obj = txt.acq_read(channels, chtrig, header)
    assert phys_obj.freq[0] == 1000000.0
    # test when units are in Hz:
    header[1][0] = '100 Hz'
    phys_obj = txt.acq_read(channels, chtrig, header)
    assert phys_obj.freq[0] == 100
    # test when units are in kHz:
    header[1][0] = '1 kHz'
    phys_obj = txt.acq_read(channels, chtrig, header)
    assert phys_obj.freq[0] == 1000
    # test when units are in MHz:
    header[1][0] = '1 MHz'
    phys_obj = txt.acq_read(channels, chtrig, header)
    assert phys_obj.freq[0] == 1000000
    # test when units are not valid:
    header[1][0] = '1 GHz'
    with raises(AttributeError) as errorinfo:
        phys_obj = txt.acq_read(channels, chtrig, header)
    assert 'not in a valid AcqKnowledge' in str(errorinfo.value)
