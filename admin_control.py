'''
    This is a very basic tKinter GUI created with GUIZero. In the future, this should probably be recreated with a more
    'established' gui framework, such as raw tkinter or else. I just used GUIZero because it's quick and (very) easy

    It runs in a standalone thread, and communicates to 'program_main.py' via a socket.
'''

from multiprocessing.connection import Client
from guizero import App, Window, Text, Combo, PushButton, CheckBox, Box, TextBox


class remote:
    def remote_run(self):
        # Stores if a save signal should be sent when program mode is changed
        self.save_change = False

        program_modes = ["DEV_MODE", "ZERO", "MVT_L", "MVT_R", "baseline_error_L", "baseline_error_R", "MAIN_GAME"]

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

        def open_mvt():
            mvt_input.show()

        def close_mvt():
            mvt_input.hide()

        def open_demo():
            demographic_input.show()

        def close_demo():
            demographic_input.hide()

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
            data = (float(mvtL_entry.value), float(mvtR_entry.value))
            conn.send(("MVT", data))

        def send_error_perc():
            conn.send(("ERRORPERC", float(target_perc_entry.value)))

        def get_connection_data():
            while conn.poll():
                try:
                    msg = conn.recv()
                except EOFError:
                    send_quit()

                if msg[0] == "MVT":
                    if not mvt_input.visible:
                        mvtL_entry.value = msg[1]
                        mvtR_entry.value = msg[2]
                    else:
                        if str(msg[1]) not in mvtL_text.value:
                            mvtL_text.value = "MVT_L" + str(msg[1])
                        if str(msg[2]) not in mvtR_text.value: 
                            mvtR_text.value = "MVT_R" + str(msg[2])
               
                elif msg[0] == "TARGET_MVT":
                    if str(msg[1]) not in mvt_target_force_text.value and mvt_target_force_text.visible:
                        mvt_target_force_text.value = "Target MVT: " + str(msg[1])
                
                elif msg[0] == "CONTINUE":
                    if msg[1]: #If the current mode is to continue
                        t = "Pause"
                        color = (0,255,0)
                    else:
                        t = "Continue"
                        color = (255, 0, 0)

                    if toggle_button.text != t:
                        toggle_button.text = t
                        toggle_button.bg = color

                elif msg[0] == "TRIALDATA":
                    t = "Pause" if msg[1] else "Continue"
                    #If the current mode is to continue

                    if toggle_button.text != t:
                        toggle_button.text = t

                    if str(msg[2]) != trial_num_c_text.value:
                        trial_num_c_text.value = str(msg[2])

                    if str(msg[3]) != total_trial_num_c_text.value:
                        total_trial_num_c_text.value = str(msg[3])


        def send_target_mvt():
            data = float(mvt_target_force_entry.value)
            conn.send(("TARGET_MVT", data))

        def send_match():
            conn.send(("MATCH", ""))

        def send_trial_num():
            conn.send(("TRIALNUM", float(trial_num_entry.value), float(total_trial_num_entry.value)))

        # CONTINUE
        # PAUSE
        def toggle_automation():
            if toggle_button.text == "Continue":
                conn.send(("CONTINUE", True))
            else:
                conn.send(("CONTINUE", False))

        app = App(title="Torque Game Admin Control", layout="grid")
        upper_box = Box(app, layout="grid", grid=[0, 0], border=True, width="fill")

        result = Text(upper_box, text="Default selection", grid=[1, 0], align="top")
        # Schedule a command to listen to data

        combo = Combo(upper_box, options=program_modes, command=mode_select_command_parser, grid=[1, 1], align="top")

        save_button = PushButton(upper_box, command=send_save, text="Save Data", grid=[0, 2], align="top")

        start_button = PushButton(upper_box, command=send_start, text="Start Mode", grid=[0, 3], align="top")

        save_on_change_checkbox = CheckBox(upper_box, text="Save on change", command=toggle_save_change, grid=[1, 2])
        save_on_change_checkbox.value = 0

        quit_button = PushButton(upper_box, command=send_quit, text="Quit", grid=[2, 2], align="right")

        open_mvt_button = PushButton(upper_box, command=open_mvt, text="Enter MVT", grid=[2,3], align="right")

        open_demo_button = PushButton(upper_box, command=open_demo, text="Enter Demographics", grid=[2,4], align="right")

    
        """
        Secondary control box
        """
        mid_box = Box(app, layout="grid", grid=[0, 1], border=True, width="fill")
        target_perc_text = Text(mid_box, text="Target Baseliine Error Percentage", grid=[0, 0])
        target_perc_entry = TextBox(mid_box, text=".25", grid=[1,0])
        enter_target_perc = PushButton(mid_box, command=send_error_perc, text="Enter", grid=[2,0])

        match_button = PushButton(mid_box, command=send_match, text="Match", grid=[2,1])


        """
        Bottom automation control box
        """
        automation_box = Box(app, layout="grid", grid=[0, 2], border=True, width="fill")
        trial_num_s_text = Text(automation_box, text="Test #", grid=[0, 0])
        trial_num_c_text = Text(automation_box, text="0", grid=[1, 0])
        trial_num_entry = TextBox(automation_box, text="0", grid=[2, 0])
        trial_num_enter = PushButton(automation_box, text="Set Trial #s", command=send_trial_num, grid=[3, 0])


        total_trial_num_s_text = Text(automation_box, text="Test #", grid=[0, 1])
        total_trial_num_c_text = Text(automation_box, text="100", grid=[1, 1])
        total_trial_num_entry = TextBox(automation_box, text="100", grid=[2, 1])

        toggle_button = PushButton(automation_box, command=toggle_automation, text="Pause", grid=[3, 1])

        """
        Demographic inputs
        """
        demographic_input = Window(app, layout="grid", title="Demographic Inputs", visible=False)

        age_text = Text(demographic_input, text="Age", grid=[0,0])
        age_entry = TextBox(demographic_input, text="Age", grid=[1,0])

        id_text = Text(demographic_input, text="Id", grid=[0, 1])
        id_entry = TextBox(demographic_input, text="Id", grid=[1, 1])

        gender_text = Text(demographic_input, text="Gender", grid=[0, 2])
        gender_entry = TextBox(demographic_input, text="Gender", grid=[1, 2])

        subject_type_text = Text(demographic_input, text="subject type", grid=[0, 3])
        subject_type_entry = TextBox(demographic_input, text="subject type", grid=[1, 3])

        diabetes_text = Text(demographic_input, text="diabetes", grid=[0, 4])
        diabetes_entry = TextBox(demographic_input, text="diabetes", grid=[1, 4])

        dom_arm_text = Text(demographic_input, text="dominant arm", grid=[0, 5])
        dom_arm_entry = TextBox(demographic_input, text="dominant arm", grid=[1, 5])

        arm_len_text = Text(demographic_input, text="arm length", grid=[0, 6])
        arm_len_entry = TextBox(demographic_input, text="arm length", grid=[1, 6])

        z_offset_text = Text(demographic_input, text="arm length", grid=[0, 7])
        z_offset_entry = TextBox(demographic_input, text="arm length", grid=[1, 7])

        stroke_distance_text = Text(demographic_input, text="years from stroke", grid=[0, 8])
        stroke_distance_entry = TextBox(demographic_input, text="years from stroke", grid=[1, 8])

        send_demographics_button = PushButton(demographic_input, command=send_demographics, text="send_demographics", grid=[0, 9])

        """
        MVT window
        """
        mvt_input = Window(app, layout="grid", title="MVT_Window", visible=False)
        
        head = Text(mvt_input, text="Manually set MVT values.\nCurrent value is in left collumn", height=3, grid=[0,0])

        mvtL_text = Text(mvt_input, text="MVT L", grid=[0, 1])
        mvtL_entry = TextBox(mvt_input, text="1", grid=[1, 1])

        mvtR_text = Text(mvt_input, text="MVT R", grid=[0, 2])
        mvtR_entry = TextBox(mvt_input, text="1", grid=[1, 2])

        send_mvt_inputs_button = PushButton(mvt_input, command=send_mvt, text="send", grid=[0, 3])

        mvt_target_force_text = Text(mvt_input, text="Target MVT Force", grid=[3, 1])
        mvt_target_force_entry = TextBox(mvt_input, text="1", grid=[3,2]) 
        enter_mvt_target_force = PushButton(mvt_input, command=send_target_mvt, text="Enter", grid=[3,3])

        result.repeat(10, get_connection_data)

        app.display()


if __name__ == '__main__':
    address = ('localhost', 6006)
    conn = Client(address)

    r = remote()
    r.remote_run()

    conn.close()
