"""Example of analog input voltage acquisition.

This example demonstrates how to acquire a voltage measurement using software timing.
"""

import nidaqmx

with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("Dev1/ai0") #TMP REMOTE 15-10(GND) TMP回転数 10 V = 1000 Hz
    task.ai_channels.add_ai_voltage_chan("Dev1/ai2") #TMP REMOTE 9-10(GND) エラー時　Low, 正常時 High (24 V)
    task.ai_channels.add_ai_voltage_chan("Dev1/ai1") #圧力計　2-5(GND) 0 - 10 V
    task.ai_channels.add_ai_voltage_chan("Dev1/ai3") #圧力計　4-5(GND) ゲージON <0.8VDC ゲージOFF >2.0VDC または入力開放状態

    data = task.read()
    print(data)
    print(f"Acquired data: {data:f}")

#TMP回転数を返す
def tmp_rotation_speed(voltage):
    #voltage TMP REMOTE 15-10(GND) TMP回転数 10 V = 1000 Hz
    return voltage*100


#圧力計　2-5(GND) 0 - 10 V
def pressure_pkr251(voltage):
    # p=10^(1.667U-d)
    # p 圧力 [Pa]
    # U 測定信号 [V]
    # d = 9.333
    d=9.333
    return 10^(1.667*voltage-d)
