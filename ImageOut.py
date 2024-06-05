import sys
import time
import random
import numpy as np
import cv2

sys.path.append(".")

import RTC
import OpenRTM_aist

# このモジュールの仕様
imageout_spec = ["implementation_id", "ImageOut",
                 "type_name", "ImageOut",
                 "description", "ModuleDescription",
                 "version", "1.0.0",
                 "vendor", "TaigaKadoguchi",
                 "category", "Category",
                 "activity_type", "STATIC",
                 "max_instance", "1",
                 "language", "Python",
                 "lang_type", "SCRIPT",
                 ""]

class ImageOut(OpenRTM_aist.DataFlowComponentBase):

    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_ImageGenParams = OpenRTM_aist.instantiateDataType(RTC.TimedShortSeq)
        self._ImageGenParamsIn = OpenRTM_aist.InPort("ImageGenParams", self._d_ImageGenParams)

        self._d_ImagePlaceXY = OpenRTM_aist.instantiateDataType(RTC.TimedShortSeq)
        self._ImagePlaceXYIn = OpenRTM_aist.InPort("ImagePlaceXY", self._d_ImagePlaceXY)

        self._d_Nowvoice = OpenRTM_aist.instantiateDataType(RTC.TimedShort)
        self._NowvoiceIn = OpenRTM_aist.InPort("Nowvoice", self._d_Nowvoice)

        self.image_gen_params = []
        self.position_array_data = []
        self.now_radius = 0
        self.max_radius = 250
        self.expanding = False
        self.expansion_start_time = 0
        self.color_shift = 20
        self.color_shift_direction = 1
        self.count = 0

    def onInitialize(self):
        self.addInPort("ImageGenParams", self._ImageGenParamsIn)
        self.addInPort("ImagePlaceXY", self._ImagePlaceXYIn)
        self.addInPort("Nowvoice", self._NowvoiceIn)
        return RTC.RTC_OK

    def onExecute(self, ec_id):
        self.count += 1
        window_width = 1440
        window_height = 960
        white_window = np.full((window_height, window_width, 3), 255, dtype=np.uint8)

        # 新しいデータがある場合、ImageGenParamsを読み取る
        if self._ImageGenParamsIn.isNew():
            self.image_gen_params = self._ImageGenParamsIn.read().data
            print(f"画像生成パラメータを受信しました: {self.image_gen_params}")

        # 新しいデータがある場合、ImagePlaceXYを読み取る
        if self._ImagePlaceXYIn.isNew():
            self.position_array_data = []
            while self._ImagePlaceXYIn.isNew():
                time.sleep(0.005)
                xy_data = self._ImagePlaceXYIn.read().data
                self.position_array_data.append(xy_data)
            print(f"位置データを受信しました: {self.position_array_data}")

        # 新しいデータがある場合、Nowvoiceを読み取る
        if self._NowvoiceIn.isNew():
            new_radius = self._NowvoiceIn.read().data
            print(f"Nowvoiceからの半径値を受信しました: {new_radius}")
            if new_radius > 5000:
                self.expanding = True
                self.expansion_start_time = time.time()
            else:
                self.expanding = False

        # 拡大状態に基づいて半径を更新
        rate_of_change = 5 + 100 * np.sin(time.time() - self.expansion_start_time)
        if self.expanding:
            if self.now_radius < self.max_radius:
                self.now_radius += rate_of_change  # 半径を増加
            else:
                self.now_radius = self.max_radius
        else:
            if self.now_radius > 0:
                self.now_radius -= rate_of_change  # 半径を減少
            else:
                self.now_radius = 0  # 半径を0にリセット

        # パラメータに基づいて形状を描画
        for amplitude, position in zip(self.image_gen_params, self.position_array_data):
            x, y = position
            # 色を決定する
            blue = min(255, int((amplitude / 20000) * 255))
            green = amplitude % 255
            red = (amplitude + self.color_shift) % 256
            base = (amplitude % 6 + 3) * 15  # 基本半径の設定
            color = (blue, green, red)
            print(f"振幅: {amplitude}, X: {x}, Y: {y}, 色: {color}")
            
            if red >= 245:
                self.color_shift_direction = -1
            elif red <= 10:
                self.color_shift_direction = 1
            
            center = (int(x*2), int(y*1.6))
            radius = int(base + self.now_radius)  # 基本半径にnow_radiusを加算
            print(f"{center}に半径{radius}の形を描画")
            # 透明度
            alpha = 0.7
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

        cv2.imshow('window', white_window)
        cv2.waitKey(1)

        # 5カウントごとに色のシフトを調整
        if self.count % 5 == 0:
            #print("###################### 色の変化 ######################")
            if self.color_shift_direction == 1:
                self.color_shift += 1
            else:
                self.color_shift -= 1

        return RTC.RTC_OK

    def onActivated(self, ec_id):
        return RTC.RTC_OK

    def onDeactivated(self, ec_id):
        cv2.destroyAllWindows()
        self.count = 0
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
    argv = [i for i in sys.argv if "--instance_name=" not in i]
    mgr = OpenRTM_aist.Manager.init(argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager()

if __name__ == "__main__":
    main()