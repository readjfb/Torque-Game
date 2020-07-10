# This works in python 3.6.3
# It must be started

from multiprocessing.connection import Client
from guizero import App, Text, Combo, PushButton, CheckBox, Box, TextBox


class remote:
    def remote_run(self):
        # Stores if a save signal should be sent when program mode is changed
        self.save_change = False

        program_modes = ["DEV_MODE", "ZERO", "MVT_L", "MVT_R", "CONST_ERROR_L", "CONST_ERROR_R", "BAR_TEST", "MAIN_GAME"]

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

            result.value = "Option " + text + " selected"
            conn.send(("MS", text))

        def toggle_save_change():
            self.save_change = save_on_change_checkbox.value

        def send_demographics():
            demographic_info = {
                "age": age_entry.value,
                "id": id_entry.value,
                "gender": gender_entry.value,
                "subject type": subject_type_entry.value,
                "diabetes": diabetes_entry.value,
                "dominant arm": dom_arm_entry.value,
                "arm length": arm_len_entry.value,
                "z offset": z_offset_entry.value,
                "years_from_stroke": stroke_distance_entry.value
            }
            conn.send(("DEMO",demographic_info))

        def send_mvt():
            return

        app = App(title="Torque Game Admin Control", layout="grid")
        upper_box = Box(app, layout="grid", grid=[0, 0], border=True, width="fill")

        result = Text(upper_box, text="Default selection", grid=[1, 0], align="top")

        combo = Combo(upper_box, options=program_modes, command=mode_select_command_parser, grid=[1, 1], align="top")

        save_button = PushButton(upper_box, command=send_save, text="Save Data", grid=[0, 2], align="top")

        start_button = PushButton(upper_box, command=send_start, text="Start Mode", grid=[0, 3], align="top")

        save_on_change_checkbox = CheckBox(upper_box, text="Save on change", command=toggle_save_change, grid=[1, 2])
        save_on_change_checkbox.value = 0

        quit_button = PushButton(upper_box, command=send_quit, text="Quit", grid=[2, 2], align="right")

        lower_box = Box(app, layout="grid", grid=[0, 1],border=True, width="fill", align="left")
        age_text = Text(lower_box, text="Age", grid=[0,0])
        age_entry = TextBox(lower_box, text="Age", grid=[1,0])

        id_text = Text(lower_box, text="Id", grid=[0, 1])
        id_entry = TextBox(lower_box, text="Id", grid=[1, 1])

        gender_text = Text(lower_box, text="Gender", grid=[0, 2])
        gender_entry = TextBox(lower_box, text="Gender", grid=[1, 2])

        subject_type_text = Text(lower_box, text="subject type", grid=[0, 3])
        subject_type_entry = TextBox(lower_box, text="subject type", grid=[1, 3])

        diabetes_text = Text(lower_box, text="diabetes", grid=[0, 4])
        diabetes_entry = TextBox(lower_box, text="diabetes", grid=[1, 4])

        dom_arm_text = Text(lower_box, text="dominant arm", grid=[0, 5])
        dom_arm_entry = TextBox(lower_box, text="dominant arm", grid=[1, 5])

        arm_len_text = Text(lower_box, text="arm length", grid=[0, 6])
        arm_len_entry = TextBox(lower_box, text="arm length", grid=[1, 6])

        z_offset_text = Text(lower_box, text="arm length", grid=[0, 7])
        z_offset_entry = TextBox(lower_box, text="arm length", grid=[1, 7])

        stroke_distance_text = Text(lower_box, text="years from stroke", grid=[0, 8])
        stroke_distance_entry = TextBox(lower_box, text="years from stroke", grid=[1, 8])

        send_demographics_button = PushButton(lower_box, command=send_demographics, text="send_demographics", grid=[0, 9])

        right_box = Box(app, layout="grid", grid=[1, 1],border=True, align="left")
        head = Text(right_box, text="Manually set MVT values. \nProgram will default to collected values \nnot be reflected by this value", height=3, grid=[0,0])

        mvtL_text = Text(right_box, text="MVT L", grid=[0, 1])
        mvtL_entry = TextBox(right_box, text="1", grid=[1, 1])

        mvtR_text = Text(right_box, text="MVT R", grid=[0, 2])
        mvtR_entry = TextBox(right_box, text="1", grid=[1, 2])

        send_demographics_button = PushButton(right_box, command=send_mvt, text="send", grid=[0, 3])

        app.display()


if __name__ == '__main__':
    address = ('localhost', 6006)
    conn = Client(address)

    r = remote()
    r.remote_run()

    conn.close()
