"""テトラアーク炉の真空状態を取得
NI USB-6001にTC600のREMOTEコネクタ、TPG261のcontrolコネクタから信号取得
ai0 TC600 15-10(GND) TMP回転数
ai1 TC600 13-14に直列の1kOhm抵抗の電圧 正常時 5 V, エラー時 0 V
ai2 未接続
ai3 TPG261 2-5(GND) 圧力値
5V  TC600 13-14 + 1kOhm
          13-14は正常時close, エラー時open
"""

import nidaqmx

#TMP回転数を返す関数
#入力 電圧[V]
#出力 回転数 [Hz]
def tmp_rotation_speed(voltage):
    #voltage TMP REMOTE 15-10(GND) TMP回転数 10 V = 1000 Hz
    return voltage*100


#圧力計PKR261の圧力値を返す関数
#入力 電圧[V]
#出力 圧力[Pa]
#圧力計　2-5(GND) 0 - 10 V
def pressure_pkr251(voltage):
    # p=10^(1.667U-d)
    # p 圧力 [Pa]
    # U 測定信号 [V]
    # d = 9.333
    d=9.333
    return 10**(1.667*voltage-d)

with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("Dev1/ai0") #TMP REMOTE 15-10(GND) TMP回転数 10 V = 1000 Hz
    task.ai_channels.add_ai_voltage_chan("Dev1/ai1") #TMP ERROR?
    task.ai_channels.add_ai_voltage_chan("Dev1/ai3") #圧力計　2-5(GND) 0 - 10 V
    data = task.read()
    #[0.017540853936225176, 5.003844041377306, 8.577811934053898]動作時
    # Rotation Speed [Hz]: 1.754085
    # Acquired data: 5.003844
    # Pressure [Pa]: 9.251507e+04
    #[-0.02365762321278453, -0.0030583846382796764, -0.022370170801877975]電源オフ
    #電源オフ時、エラー時に ai1= 0, 正常時 ai1=5

    print(data)
    rotation=tmp_rotation_speed(data[0])
    pressure=pressure_pkr251(data[2])
    gage_power_on=data[2]>0.1 #圧力計power on
    pumping=data[2]<8.5 and data[2]>1.82 #真空引き中の判断 8.5->68kPa, 1.82->有効範囲下限値
    error_alert=data[1]<4 and pumping
    system_power_on=data[1]>4
    print(f"Rotation Speed [Hz]: {rotation:f}")
    print(f"Acquired data: {data[1]:f}")
    print(f"Pressure [Pa]: {pressure:e}")
    print(system_power_on)
    print(gage_power_on)
    print(pumping)
    print(error_alert)
