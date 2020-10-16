#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Read anolog encoder value and convert them to rad.

Steps:
1. Call get_daq_device_inventory() to get the list of available DAQ devices
2. Create a DaqDevice object
3. Call daq_device.get_ai_device() to get the ai_device object for the AI
   subsystem
4. Verify the ai_device object is valid
5. Call daq_device.connect() to establish a UL connection to the DAQ device
6. Call ai_device.a_in() to read a value from an A/D input channel
7. Display the data for each channel
8. Call daq_device.disconnect() and daq_device.release() before exiting the
   process.
"""
from __future__ import print_function
from time import sleep
from os import system
from sys import stdout
import math

from uldaq import (get_daq_device_inventory, DaqDevice, InterfaceType,
                   AiInputMode, AInFlag)


def main():
    """Analog input example."""
    daq_device = None

    range_index = 0
    interface_type = InterfaceType.ANY
    low_channel = 0
    high_channel = 7

    try:
        # Get descriptors for all of the available DAQ devices.
        devices = get_daq_device_inventory(interface_type)
        number_of_devices = len(devices)
        if number_of_devices == 0:
            raise RuntimeError('Error: No DAQ devices found')

        print('Found', number_of_devices, 'DAQ device(s):')
        for i in range(number_of_devices):
            print('  [', i, '] ', devices[i].product_name, ' (',
                  devices[i].unique_id, ')', sep='')

        descriptor_index = input('\nPlease select a DAQ device, enter a number'
                                 + ' between 0 and '
                                 + str(number_of_devices - 1) + ': ')
        descriptor_index = int(descriptor_index)
        if descriptor_index not in range(number_of_devices):
            raise RuntimeError('Error: Invalid descriptor index')

        # Create the DAQ device from the descriptor at the specified index.
        daq_device = DaqDevice(devices[descriptor_index])

        # Get the AiDevice object and verify that it is valid.
        ai_device = daq_device.get_ai_device()
        if ai_device is None:
            raise RuntimeError('Error: The DAQ device does not support '
                               'analog input')

        # Establish a connection to the DAQ device.
        descriptor = daq_device.get_descriptor()
        print('\nConnecting to', descriptor.dev_string, '- please wait...')
        # For Ethernet devices using a connection_code other than the default
        # value of zero, change the line below to enter the desired code.
        daq_device.connect(connection_code=0)

        ai_info = ai_device.get_info()

        # The default input mode is SINGLE_ENDED.
        input_mode = AiInputMode.SINGLE_ENDED
        # If SINGLE_ENDED input mode is not supported, set to DIFFERENTIAL.
        if ai_info.get_num_chans_by_mode(AiInputMode.SINGLE_ENDED) <= 0:
            input_mode = AiInputMode.DIFFERENTIAL

        # Get the number of channels and validate the high channel number.
        number_of_channels = ai_info.get_num_chans_by_mode(input_mode)
        if high_channel >= number_of_channels:
            high_channel = number_of_channels - 1

        # Get a list of supported ranges and validate the range index.
        ranges = ai_info.get_ranges(input_mode)
        if range_index >= len(ranges):
            range_index = len(ranges) - 1

        print('\n', descriptor.dev_string, ' ready', sep='')
        print('    Function demonstrated: ai_device.a_in()')
        print('    Channels: ', low_channel, '-', high_channel)
        print('    Input mode: ', input_mode.name)
        print('    Range: ', ranges[range_index].name)
        try:
            input('\nHit ENTER to continue\n')
        except (NameError, SyntaxError):
            pass

        system('clear')

        try:
            # input intitiallization
            data_vol_pre = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            data_vol_incr = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            tolerance_ratio = 0.9
            for channel in range(low_channel, high_channel + 1):
                data_vol_pre[channel] = ai_device.a_in(channel, input_mode,
                                                       ranges[range_index],
                                                       AInFlag.DEFAULT)

            while True:
                try:
                    reset_cursor()
                    print('Please enter CTRL + C to terminate the process\n')
                    print('Active DAQ device: ', descriptor.dev_string, ' (',
                          descriptor.unique_id, ')\n', sep='')
                    data_vol_max = ai_device.a_in(0, input_mode,
                                                  ranges[range_index],
                                                  AInFlag.DEFAULT)
                    tolerance = data_vol_max * tolerance_ratio

                    # Display data for the specified analog input channels.
                    for channel in range(low_channel + 1, high_channel + 1):
                        data_vol = ai_device.a_in(channel, input_mode,
                                                  ranges[range_index],
                                                  AInFlag.DEFAULT)
                        if data_vol - data_vol_pre[channel] > tolerance:
                            data_vol_incr[channel] += data_vol - data_vol_pre[channel] - data_vol_max
                        elif data_vol - data_vol_pre[channel] < -1.0 * tolerance:
                            data_vol_incr[channel] += data_vol - data_vol_pre[channel] + data_vol_max
                        else:
                            data_vol_incr[channel] += data_vol - data_vol_pre[channel]
                        data_rad = data_vol_incr[channel] / data_vol_max * 2 * math.pi
                        data_vol_pre[channel] = data_vol
                        print('Channel(', channel, ') Data: ',
                              '{:.6f}'.format(data_rad), sep='')

                    sleep(0.001)
                except (ValueError, NameError, SyntaxError):
                    break
        except KeyboardInterrupt:
            pass

    except RuntimeError as error:
        print('\n', error)

    finally:
        if daq_device:
            if daq_device.is_connected():
                daq_device.disconnect()
            daq_device.release()


def reset_cursor():
    """Reset the cursor in the terminal window."""
    stdout.write('\033[1;1H')

def absolute_relative_convertor():
    print('\n')

if __name__ == '__main__':
    main()
