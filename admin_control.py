# This works in python 3.6.3
# It must be started 

from multiprocessing.connection import Client
import random
from guizero import *

class remote:
	def remote_run(self):
		# Stores if a save signal should be sent when program mode is changed
		self.save_change = False

		program_modes = ["DEV_MODE", "CALIBRATE", "MVT_L", "MVT_R", "CONST_ERROR_L", "CONST_ERROR_R", "MAIN_GAME"]

		def send_quit():
			if self.save_change:
				send_save()

			conn.send(("EXIT", "EXIT"))
			conn.close()
			quit()

		def send_save():
			conn.send(("CMD", "SAVE"))
			conn.send(("CMD", "CLEAR"))

		def send_start():
			conn.send(("CMD", "CLEAR"))
			conn.send(("CMD", "START"))

		def mode_select_command_parser(text):
			if self.save_change:
				send_save()
			else:
				conn.send(("CMD", "CLEAR"))

			result.value = "Option "+ text + " selected"
			conn.send(("MS", text))

		def toggle_save_change():
			self.save_change = save_on_change_checkbox.value

		app = App(title="Hey", layout="grid")
		result = Text(app, text="Default selection", grid=[1,0], align="top")

		combo = Combo(app, options=program_modes, command=mode_select_command_parser, grid=[1, 1], align="top")
		
		save_button = PushButton(app, command=send_save, text="Save Data", grid=[0,2], align="top")

		start_button = PushButton(app, command=send_start, text="Start Mode", grid=[0,3], align="top")

		save_on_change_checkbox = CheckBox(app, text="Save on change", command=toggle_save_change, grid=[1,2])
		save_on_change_checkbox.value = 0

		quit_button = PushButton(app, command=send_quit, text="Quit", grid=[2,2], align="right")

		app.display()


if __name__ == '__main__':
	address = ('localhost', 6006)
	conn = Client(address)

	r = remote()
	r.remote_run()

	conn.close()

