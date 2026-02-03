#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from pymeasure.instruments import Instrument
import nidaqmx

"""テトラアーク炉の真空状態を取得
NI USB-6001にTC600のREMOTEコネクタ、TPG261のcontrolコネクタから信号取得
ai0 TC600 15-10(GND) TMP回転数
ai1 TC600 13-14に直列の1kOhm抵抗の電圧 正常時 5 V, エラー時 0 V
ai2 未接続
ai3 TPG261 2-5(GND) 圧力値
5V  TC600 13-14 + 1kOhm
          13-14は正常時close, エラー時open
"""

class TetraArcVacuumSystem():
    def __init__(self):
        self.speed = 0 # TMP rotation speed (Hz)
        self.pressure = 0 # Pressure (Pa)
        self.gage_power = False # pressure gage power on (True) or off (False)
        self.system_power = False # pumping system power on (True) or off (False)
        self.error = False # pump error ?
        self.pumping = False # Pumping (True) or Standby (False)
    
    def get_values(self)
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan("Dev1/ai0") #TMP REMOTE 15-10(GND) TMP回転数 10 V = 1000 Hz
            task.ai_channels.add_ai_voltage_chan("Dev1/ai1") #TMP ERROR?
            task.ai_channels.add_ai_voltage_chan("Dev1/ai3") #圧力計　2-5(GND) 0 - 10 V
            data = task.read()
            self.speed = data[0]*100
            self.system_power = data[1]>4
                # TMPの電源On/Off判定 Bool
                # 電源On時5V，4V以上で電源On(True)と判断
            self.pressure = 10**(1.667*data[2]-9.333)
                # p=10^(1.667U-d)
                # p 圧力 [Pa]
                # U 測定信号 [V]
                # d = 9.333
            self.gage_power = data[2]>0.1
                #圧力計電源On/Off判定 Bool
                # 測定電圧0.1V以上で電源On(True)と判定
            self.pumping = (data[2]<8.5 and data[2]>1.82)


if __name__ == "__main__":
    tmp = TetraArcVacuumSystem()
    tmp.get_values()
    #speed = tmp.tmp_rotation_speed()
    print(f"Rotation Speed [Hz]: {tmp.speed:f}")
    print(f"Pressure [Pa]: {tmp.pressure:e}")
    print(f"PKR ON ? : {tmp.gage_power}")
    print(f"Pumping ? : {tmp.pumping}")
