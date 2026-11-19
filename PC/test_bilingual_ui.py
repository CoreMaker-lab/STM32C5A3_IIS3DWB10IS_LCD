import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import unittest
from PySide6 import QtWidgets
from app import Window
from i18n import set_language

class BilingualUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_main_and_calibration_dialog_switch_languages_without_rebuild(self):
        set_language("zh")
        win = Window()
        win.timer.stop()
        try:
            self.assertEqual(win.connect_button.text(), "连接")
            self.assertEqual(win.learn.text(), "学习正常状态（30秒）")
            self.assertEqual(win.cal_dialog.begin.text(), "开始新校准")

            win.language_combo.setCurrentIndex(1)
            self.assertEqual(win.connect_button.text(), "Connect")
            self.assertEqual(win.learn.text(), "Learn Normal State (30 s)")
            self.assertEqual(win.cal_dialog.begin.text(), "Start New Calibration")
            self.assertEqual(win.cal_dialog.table.horizontalHeaderItem(0).text(), "Face Up")

            # Dynamic updates after the switch must remain in English.
            win.learning_note.setText("串口未连接，学习指令未发送。")
            self.assertEqual(win.learning_note.text(), "Serial port is not connected. The learning command was not sent.")

            win.language_combo.setCurrentIndex(0)
            self.assertEqual(win.connect_button.text(), "连接")
            self.assertEqual(win.cal_dialog.begin.text(), "开始新校准")
            self.assertEqual(win.cal_dialog.table.horizontalHeaderItem(0).text(), "朝上方向")
        finally:
            win.worker = None
            win.close()
            set_language("zh")
            self.app.processEvents()

if __name__ == "__main__":
    unittest.main()
