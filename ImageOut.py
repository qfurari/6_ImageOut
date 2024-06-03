#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

# <rtc-template block="description">
"""
 @file ImageOut.py
 @brief ModuleDescription
 @date $Date$
"""
# </rtc-template>

import sys
import time
import numpy as np
import cv2
import random

sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

# This module's specification
imageout_spec = ["implementation_id", "ImageOut", 
         "type_name",         "ImageOut", 
         "description",       "ModuleDescription", 
         "version",           "1.0.0", 
         "vendor",            "TaigaKadoguchi", 
         "category",          "Category", 
         "activity_type",     "STATIC", 
         "max_instance",      "1", 
         "language",          "Python", 
         "lang_type",         "SCRIPT",
         ""]

class ImageOut(OpenRTM_aist.DataFlowComponentBase):
    
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_ImageGenParams = OpenRTM_aist.instantiateDataType(RTC.TimedShortSeq)
        self._ImageGenParamsIn = OpenRTM_aist.InPort("ImageGenParams", self._d_ImageGenParams)
        self._d_ImagePlaceXY = OpenRTM_aist.instantiateDataType(RTC.TimedShortSeq)
        self._ImagePlaceXYIn = OpenRTM_aist.InPort("ImagePlaceXY", self._d_ImagePlaceXY)

        # 画像生成用の数値配列を保存するリスト
        self.image_gen_params = []
        
    def onInitialize(self):
        self.addInPort("ImageGenParams", self._ImageGenParamsIn)
        self.addInPort("ImagePlaceXY", self._ImagePlaceXYIn)
        return RTC.RTC_OK

    def onExecute(self, ec_id):
        # 固定のウィンドウサイズを設定
        window_width = 1440
        window_height = 960

        # 白い画像を生成
        white_window = np.full((window_height, window_width, 3), 255, dtype=np.uint8)

        # 画像生成用の数値配列と座標配列を初期化
        position_array_data = []

        # 画像生成用の数値配列を受け取る(今まで受け取ったのは保存してそれに上書き)
        if self._ImageGenParamsIn.isNew():
            self.image_gen_params = self._ImageGenParamsIn.read().data
            print(f"Received image generation parameters: {self.image_gen_params}")

        # 座標データを一組ずつ受け取ってリストに格納する
        if self._ImagePlaceXYIn.isNew():
            while self._ImagePlaceXYIn.isNew():
                time.sleep(0.005)
                xy_data = self._ImagePlaceXYIn.read().data
                position_array_data.append(xy_data)
            print(f"Received position data: {position_array_data}")

            for amplitude, (x, y) in zip(self.image_gen_params, position_array_data):
                # 色を決定する
                num = amplitude % 3
                blue = min(255, int((amplitude / 20000) * 255))
                green = amplitude % 255
                red = random.randint(50 * (num + 1), 255)
                color = (blue, green, red)

                center = (int(x*2), int(y*1.5))
                radius = (amplitude % 6 + 3) * 15
                alpha = 0.7  # 透明度

                # 新しいウィンドウに図形を描画
                overlay = white_window.copy()
               
                shape_index = (amplitude - 1) // 500
                num_sides = max(min(shape_index + 3, 100), 3)
                angle_step = 2 * np.pi / num_sides
                angles = np.arange(num_sides) * angle_step
                x_points = (center[0] + radius * np.cos(angles)).astype(int)
                y_points = (center[1] + radius * np.sin(angles)).astype(int)
                points = np.column_stack((x_points, y_points))
                

                cv2.fillPoly(overlay, [points], color)
                # 透過合成
                cv2.addWeighted(overlay, alpha, white_window, 1 - alpha, 0, white_window)

            cv2.imshow('Display Image', white_window)
            cv2.waitKey(1)
        if self.image_gen_params == []:
            cv2.imshow('Display Image', white_window)
            cv2.waitKey(1)
            
             
        return RTC.RTC_OK

    def onActivated(self, ec_id):
        return RTC.RTC_OK

    def onDeactivated(self, ec_id):
        return RTC.RTC_OK

def ImageOutInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=imageout_spec)
    manager.registerFactory(profile, ImageOut, OpenRTM_aist.Delete)

def MyModuleInit(manager):
    ImageOutInit(manager)
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
    comp = manager.createComponent("ImageOut" + args)

def main():
    argv = [i for i in sys.argv if not "--instance_name=" in i]
    mgr = OpenRTM_aist.Manager.init(argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager()

if __name__ == "__main__":
    main()
