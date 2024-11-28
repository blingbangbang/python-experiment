# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 11:01:06 2020

@author: hidaka
"""


#RT with AVS47 and 372U ver1.1 by Hidaka
import visa
import csv
import matplotlib.pyplot as plt
from time import sleep
import pandas as pd
from pandas import DataFrame
import numpy as np
import math
import time
 
#過去のcsvファイル読み込み
#df1 = pd.read_csv("D:\\eri\\Desktop\\Python\\test_T.csv", header=None)
#header=None: 一行目をヘッダーとして解釈させない
#df1 = df1.drop(0, axis=0) #行の削除　drop(行の番号, 行)　axis=1は列指定
#df1_col = df1.columns
#print(df1[df1_col[1]], df1[df1_col[2]]) #df[df_col[列(column)番号]]　 row=行　


#Data保存先設定 (適当なファイルパスを設定してください)
File_name = "C:\\Users\\hidak\\デスクトップ\\Python\\test.csv"


#GPIB Address設定
AVS47_Addr = "GPIB0::20"  #AVS47 for Temperature 
AC372U_Addr = "GPIB0::12"  #for Reistance AC Bridge 372U
Keithley2000_Addr = "GPIB0::6"  #DMM2000 for magnetic field


r = visa.ResourceManager()
AVS47 = r.open_resource(AVS47_Addr)
AC372U = r.open_resource(AC372U_Addr)
keithley2000 = r.open_resource(Keithley2000_Addr)

#Degital Filter (AVERage) and Rate (NPLCycles) Setting on Keithley2000 
keithley2000.write(":SENSe:VOLT:DC:AVERage:STATe ON")  #STATe n; n = OFF or ON
keithley2000.write(":SENSe:VOLT:DC:AVERage:TCONtrol MOVing")  #REPeat or MOVing
keithley2000.write(":SENSe:VOLT:DC:AVERage:COUNt 20")  #COUNt n; n = filter count
keithley2000.write(":SENSe:VOLT:DC:NPLCycles 10") #PLCycles n; 0.01 <= n <= 10; n = 0.1 FAST, 1 MID, 10 SLOW

#TRIGger Command on Keithley2000 （データをPLCで連続読み取りとるための設定）
keithley2000.write(":INITiate:CONTinuous ON") 


#データリスト準備
dataX = []  #Resistance on AVS47
dataT = []  #Temperature 
dataB = []  #Magnetic Field 
dataR = []  #Measure Resistance on 372U
dataI = []  #Data Number
dataTime = []  #Time


i = 0  #data number

#スタート時間
t0 = time.time()
#print(t0)


while 1:
    i += 1 #Data Number

    dX = AVS47.query("ADC;RES?") #query:質問
    
    #温度校正:CX158207 (1.9 < T < 318 K)  
    dX2 = dX[5:]  #[5:]左から５文字削除  

    if float(dX2) > 30.77843 and float(dX2) < 345.11408: 
        A0 = 2.67884
        A1 = -0.86254
        A2 = -0.11505
        A3 = 1.88094
        A4 = -5.71991
        A5 = 9.10954
        A6 = -8.94247
        A7 = 5.38457
        A8 = -1.81153
        A9 = 0.25905
        
        dXX = math.log(float(dX2)/25) 
        
        dXXX = A9*dXX**9 + A8*dXX**8 + A7*dXX**7 + A6*dXX**6 + A5*dXX**5 \
        + A4*dXX**4 + A3*dXX**3 + A2*dXX**2 + A1*dXX**1 + A0
    
        if float(dX2) >= 118.5 :      
            A0 = 1.6297
            A1 = -1.53992
            A2 = 3.22691
            A3 = -12.06279
            A4 = 24.0736
            A5 = -27.13274
            A6 = 17.21791
            A7 = -5.24912
            A8 = 0.19339
            A9 = 0.18529
            
            dXX = math.log(float(dX2)/90) 
    
            dXXX = A9*dXX**9 + A8*dXX**8 + A7*dXX**7 + A6*dXX**6 + A5*dXX**5 \
            + A4*dXX**4 + A3*dXX**3 + A2*dXX**2 + A1*dXX**1 + A0
    
        dT = 10**dXXX  
    
    else:
        dT= 00000 #校正外
    
    dataX.append(dX[5:]) #append:リスト末に要素を追加, [5:]左から５文字削除
    dataT.append(dT) #append:リスト末に要素を追加
    
    #Magnetic Field (PPMSからのAnalog output)
    dB = keithley2000.query(":SENS:DATA:FRES?")
    dBB = float(dB)*1.4 # unit = T; 
    dataB.append(dBB)  
        
    #Resistance [Ohm]
    dR = AC372U.query("RDGR? 1") #Ch1 -> "RDGR? 1", Ch2 -> "RDGR? 2", Ch3 -> "RDGR? 3"
    #dR = dR[:14] #[5:]左から５文字削除
    dRR = float(dR) 
    dataR.append(dRR)
    
    #Data Number
    dataI.append(i)
    
    #Elapsed time
    t1 = time.time()
    dt = t1-t0 #[sec]
    dataTime.append(dt)
       
    #data取得間隔
    n = 5 #[sec]だけど遅延ありなので注意
    #when n=1 -> ~1.64; n=2 -> ~2.81; n=5 -> ~?; n=10 -> ~?
    sleep(n) 

    print("Data: ", i, "Time: ", '{:1f}'.format(dt), "Temp: ", dT, "Mag Field: ", dBB, "R: ", dRR) #float:文字列を実数変換
    
    #ファイル名変更忘れ用データ保存先　(適当なファイルパスを設定してください:実際のデータファイル名や保存先は最初のところで設定しています)
    #mode = "x"は上書き禁止, "w"は上書き可, "a"はデータ追加、t:text形式出力 
    with open("C:\\Users\\hidak\\デスクトップ\\Python\\保存用X for RT", "at") as fx:
       fx.writelines(dX) 
    with open("C:\\Users\\hidak\\デスクトップ\\Python\\保存用T for RT", "at") as ft:
       ft.write(str(dT)+"\n") # \n:改行 
    with open("C:\\Users\\hidak\\デスクトップ\\Python\\保存用B for RT", "at") as fr:    
       fr.writelines(str(dBB)+"\n")   
    with open("C:\\Users\\hidak\\デスクトップ\\Python\\保存用R for RT", "at") as fr:    
       fr.writelines(str(dRR)+"\n")   
    with open("C:\\Users\\hidak\\デスクトップ\\Python\\保存用Time for RT", "at") as fr:    
       fr.writelines(str(dt)+"\n")   
    
    #読み込んだデータのリスト作成
    X = [float(f) for f in dataX]
    T = [float(f) for f in dataT]
    B = [float(f) for f in dataB]
    R = [float(f) for f in dataR]
    I = [float(f) for f in dataI]
    Time = [float(f) for f in dataTime]
    
    #グラフ    
    fig = plt.figure(figsize=(5,7), facecolor = "azure")
    plt.subplots_adjust(wspace = 0.4, hspace = 0.3)
    
    ax1 = fig.add_subplot(3, 1, 1) #(グラフの位置：2=2行, 1=1列, 1=左)   
    ax1.plot(Time, T, marker="o", color = "red", linestyle="-")
    #ax1.set_title("いっぬ")
    plt.xlabel("Time [sec]") #x軸のラベル
    plt.ylabel("Temperature [K]") #y軸のラベル
    #plt.xlim(i-14, i) #x軸の範囲
    #plt.xticks(np.arange(i-14, i, 5.0)) #x軸主目盛り設定
    #plt.ylim(dT-5, dT+5) #y軸の範囲
    plt.grid(True)
    
    ax2 = fig.add_subplot(3, 1, 2) #(グラフの位置：2=2行, 1=1列, 1=左)
    ax2.plot(Time, R, marker="o", color = "red", linestyle="-")
    #ax2.plot(J, R, "ro", df1[df1_col[2]], df1[df1_col[3]], "bo") #col：0 = X, 1 = T, 2 = Y)
    #ax2.set_title("ぬこ")
    plt.xlabel("Time [Sec]") #x軸のラベル
    plt.ylabel("Resistance [Ohm]") #y軸のラベル
    #plt.xlim(0, 300) #x軸の範囲
    #plt.ylim(-1, 1) #y軸の範囲
    plt.grid(True) #グリッド表示 
    
    ax3 = fig.add_subplot(3, 1, 3) #(グラフの位置：2=2行, 1=1列, 1=左)
    ax3.plot(T, R, marker="o", color = "red", linestyle="-")
    #ax3.plot(J, R, "ro", df1[df1_col[2]], df1[df1_col[3]], "bo") #col：0 = X, 1 = T, 2 = Y)
    #ax3.set_title("ぬこ")
    plt.xlabel("Temperature [K]") #x軸のラベル
    plt.ylabel("Resistance [Ohm]") #y軸のラベル
    #plt.xlim(0, 300) #x軸の範囲
    #plt.ylim(-1, 1) #y軸の範囲
    plt.grid(True) #グリッド表示
    
    plt.show()

    
    #csvファイルへの出力 (適当なファイルパスを設定してください:実際のデータファイル名や保存先は最初のところで設定しています)
    stock = [I, Time, X, T, B, R]   
    #column：0 = data No, 1 = Time, 2 = AVS raw, 3 = Temp, 4 = Current, 5 = Resistance
    with open("C:\\Users\\hidak\\デスクトップ\\Python\\temporary data.csv", "w", encoding="Shift_jis") as f: # 文字コードをShift_JISに指定
      writer = csv.writer(f, lineterminator="\n") # writerオブジェクトの作成 改行記号で行を区切る
      writer.writerows(stock) 
    
    df = pd.read_csv("C:\\Users\\hidak\\デスクトップ\\Python\\temporary data.csv") #上記csvを読み込み
    #print(df)
    dfT = df.T # csv fileの転置
    #print(df.T)
    #File name imput
    dfT.to_csv(File_name) #csvを転置て再保存
