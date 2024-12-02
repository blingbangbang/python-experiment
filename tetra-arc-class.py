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
# Import necessary packages
from pymeasure.instruments.keithley import Keithley2400
from pymeasure.experiment import Procedure, Results, Worker
from pymeasure.experiment import IntegerParameter, FloatParameter
from time import sleep
import numpy as np

from pymeasure.log import log, console_log

class IVProcedure(Procedure):

    data_points = IntegerParameter('Data points', default=20)
    averages = IntegerParameter('Averages', default=8)
    max_current = FloatParameter('Maximum Current', units='A', default=0.001)
    min_current = FloatParameter('Minimum Current', units='A', default=-0.001)

    DATA_COLUMNS = ['Current (A)', 'Voltage (V)', 'Voltage Std (V)']

    def startup(self):
        log.info("Connecting and configuring the instrument")
        self.sourcemeter = Keithley2400("GPIB::24")
        self.sourcemeter.reset()
        self.sourcemeter.use_front_terminals()
        self.sourcemeter.apply_current(100e-3, 10.0)  # current_range = 100e-3, compliance_voltage = 10.0
        self.sourcemeter.measure_voltage(0.01, 1.0)  # nplc = 0.01, voltage_range = 1.0
        sleep(0.1)  # wait here to give the instrument time to react
        self.sourcemeter.stop_buffer()
        self.sourcemeter.disable_buffer()

    def execute(self):
        currents = np.linspace(
            self.min_current,
            self.max_current,
            num=self.data_points
        )
        self.sourcemeter.enable_source()
        # Loop through each current point, measure and record the voltage
        for current in currents:
            self.sourcemeter.config_buffer(IVProcedure.averages.value)
            log.info("Setting the current to %g A" % current)
            self.sourcemeter.source_current = current
            self.sourcemeter.start_buffer()
            log.info("Waiting for the buffer to fill with measurements")
            self.sourcemeter.wait_for_buffer()
            data = {
                'Current (A)': current,
                'Voltage (V)': self.sourcemeter.means[0],
                'Voltage Std (V)': self.sourcemeter.standard_devs[0]
            }
            self.emit('results', data)
            sleep(0.01)
            if self.should_stop():
                log.info("User aborted the procedure")
                break

    def shutdown(self):
        self.sourcemeter.shutdown()
        log.info("Finished measuring")


if __name__ == "__main__":
    console_log(log)

    log.info("Constructing an IVProcedure")
    procedure = IVProcedure()
    procedure.data_points = 20
    procedure.averages = 8
    procedure.max_current = -0.001
    procedure.min_current = 0.001

    data_filename = 'example.csv'
    log.info("Constructing the Results with a data file: %s" % data_filename)
    results = Results(procedure, data_filename)

    log.info("Constructing the Worker")
    worker = Worker(results)
    worker.start()
    log.info("Started the Worker")

    log.info("Joining with the worker in at most 1 hr")
    worker.join(timeout=3600)  # wait at most 1 hr (3600 sec)
    log.info("Finished the measurement")




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
