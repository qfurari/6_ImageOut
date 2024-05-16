﻿#!/usr/bin/env python
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
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist


# Import Service implementation class
# <rtc-template block="service_impl">

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
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
# </rtc-template>

# <rtc-template block="component_description">
##
# @class ImageOut
# @brief ModuleDescription
# 
# 受け取った座標に受け取ったimageをプロジェクターを通して出力するコンポーネント
# 
# 
# </rtc-template>
class ImageOut(OpenRTM_aist.DataFlowComponentBase):
	
    ##
    # @brief constructor
    # @param manager Maneger Object
    # 
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_ImageIn = OpenRTM_aist.instantiateDataType(RTC.TimedOctetSeq)
        """
        """
        self._ImageInIn = OpenRTM_aist.InPort("ImageIn", self._d_ImageIn)
        self._d_ImagePlaceXY = OpenRTM_aist.instantiateDataType(RTC.TimedShortSeq)
        """
        """
        self._ImagePlaceXYIn = OpenRTM_aist.InPort("ImagePlaceXY", self._d_ImagePlaceXY)


		


        # initialize of configuration-data.
        # <rtc-template block="init_conf_param">
		
        # </rtc-template>


		 
    ##
    #
    # The initialize action (on CREATED->ALIVE transition)
    # 
    # @return RTC::ReturnCode_t
    # 
    #
    def onInitialize(self):
        # Bind variables and configuration variable
		
        # Set InPort buffers
        self.addInPort("ImageIn",self._ImageInIn)
        self.addInPort("ImagePlaceXY",self._ImagePlaceXYIn)
		
        # Set OutPort buffers
		
        # Set service provider to Ports
		
        # Set service consumers to Ports
		
        # Set CORBA Service Ports
		
        return RTC.RTC_OK
	
    ###
    ## 
    ## The finalize action (on ALIVE->END transition)
    ## 
    ## @return RTC::ReturnCode_t
    #
    ## 
    #def onFinalize(self):
    #

    #    return RTC.RTC_OK
	
    ###
    ##
    ## The startup action when ExecutionContext startup
    ## 
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onStartup(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The shutdown action when ExecutionContext stop
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onShutdown(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ##
    #
    # The activated action (Active state entry action)
    #
    # @param ec_id target ExecutionContext Id
    # 
    # @return RTC::ReturnCode_t
    #
    #
    def onActivated(self, ec_id):
    
        return RTC.RTC_OK
	
    ##
    #
    # The deactivated action (Active state exit action)
    #
    # @param ec_id target ExecutionContext Id
    #
    # @return RTC::ReturnCode_t
    #
    #
    def onDeactivated(self, ec_id):
    
        return RTC.RTC_OK
	
    ##
    #
    # The execution action that is invoked periodically
    #
    # @param ec_id target ExecutionContext Id
    #
    # @return RTC::ReturnCode_t
    #
    #
    def onExecute(self, ec_id):
        import numpy as np
        import cv2

        # 画像を受け取る
        if self._ImageInIn.isNew():
            image_data = self._ImageInIn.read().data
        else:
            print("not image")
            return RTC.RTC_OK
        
        # 座標を受け取る
        if self._ImagePlaceXYIn.isNew():
            xy_data = self._ImagePlaceXYIn.read().data
        else:
            print("not Place")
            return RTC.RTC_OK

        # 画像データをOpenCVの画像に変換
        image = cv2.imdecode(np.frombuffer(image_data, dtype=np.uint8), cv2.IMREAD_COLOR)

        # 座標データから座標を取得
        x = xy_data[0]  # X座標
        y = xy_data[1]  # Y座標
        width = xy_data[2]  # 幅
        height = xy_data[3]  # 高さ

        # 指定した座標に画像を表示する
        # ディスプレイに画像を表示
        display_image = np.zeros((height, width, 3), np.uint8)
        display_image[:image.shape[0], :image.shape[1]] = image

        cv2.imshow('Display Image', display_image)
        cv2.moveWindow('Display Image', x, y)
        cv2.waitKey(1000)  # 1秒後に終了
        cv2.destroyAllWindows()

        return RTC.RTC_OK

	
    ###
    ##
    ## The aborting action when main logic error occurred.
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onAborting(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The error action in ERROR state
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onError(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The reset action that is invoked resetting
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onReset(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The state update action that is invoked after onExecute() action
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##

    ##
    #def onStateUpdate(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The action that is invoked when execution context's rate is changed
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onRateChanged(self, ec_id):
    #
    #    return RTC.RTC_OK
	



def ImageOutInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=imageout_spec)
    manager.registerFactory(profile,
                            ImageOut,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    ImageOutInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("ImageOut" + args)

def main():
    # remove --instance_name= option
    argv = [i for i in sys.argv if not "--instance_name=" in i]
    # Initialize manager
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager()

if __name__ == "__main__":
    main()

