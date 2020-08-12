from multiprocessing.connection import Listener

from data_saver import data_saver
from mvt_viewer import mvt_viewer
from clear_screen import clearer
from zeroer import zeroer
from constant_error_test import error_test
from bar_game import bar_game

import pygame

import time
from time import strftime, localtime


program_modes = ["DEV_MODE", "ZERO", "MVT_L", "MVT_R", "CONST_ERROR_L", "CONST_ERROR_R", "MAIN_GAME"]


def zeroed(data):
    global zero_data

    return [data[0]-zero_data[0], data[1]-zero_data[1]]

def add_header():
    global demographic_info, saver

    header = "trial_num, total_num_trials, raw_torqueL, raw_torqueR, zeroed_torqueL, zeroed_torqueR, MVT_L, MVT_R, Time, program_state, "

    keys = demographic_info.keys()
    header += ", ".join(keys)

    saver.add_data(header)

# Handler methods control what happens each 'tick' in each separate mode
def handler_exit():
    print("Exiting gracefully")
    pygame.quit()
    data_conn.close()
    remote_conn.close()
    quit()


def handler_dev_mode():
    global clearer, program_mode
    return_val = clearer.run()

    if return_val == False: program_mode = "EXIT"


def handler_mvt_L():
    global mvt, program_mode, zeroed_last_data, saved_MVT_L
    return_val = mvt.process_data(zeroed_last_data[0])

    if return_val == "EXIT": program_mode = "EXIT"

    if "SAVE" in return_val:
        return_val = return_val.split(",")
        saved_MVT_L = float(return_val[1])

        saver.save_data(program_mode)
        saver.clear()
        add_header()


def handler_mvt_R():
    global mvt, program_mode, zeroed_last_data, saved_MVT_R
    return_val = mvt.process_data(zeroed_last_data[1])

    if return_val == "EXIT": program_mode = "EXIT"

    if "SAVE" in return_val:
        return_val = return_val.split(",")
        saved_MVT_R = float(return_val[1])

        saver.save_data(program_mode)
        saver.clear()
        add_header()


def handler_const_error_l():
    global program_mode, const_error_test, saved_MVT_L, saved_MVT_R, const_error_target_perc

    return_val = const_error_test.process_data(zeroed_last_data[0], saved_MVT_L, const_error_target_perc, zeroed_last_data[1], saved_MVT_R)

    if return_val == "False": program_mode = "EXIT"

    if return_val == "SAVE": 
        saver.save_data(program_mode)
        saver.clear()
        add_header()


def handler_const_error_r():
    global program_mode, const_error_test, saved_MVT_L, saved_MVT_R, const_error_target_perc

    return_val = const_error_test.process_data(zeroed_last_data[1], saved_MVT_R, const_error_target_perc, zeroed_last_data[0], saved_MVT_L)

    if return_val == "False": program_mode = "EXIT"

    if return_val == "SAVE":
        saver.save_data(program_mode)
        saver.clear()
        add_header()


def handler_main_game():
    global program_mode, main_game, zeroed_last_data
    return_val = main_game.process_data(zeroed_last_data[0], zeroed_last_data[1], saved_MVT_L, saved_MVT_R)

    if return_val == "False": program_mode = "EXIT"

    elif "SAVE" in return_val:
        saver.save_data(program_mode)
        saver.clear()
        add_header()


def handler_zero():
    global program_mode, zeroer, zero_data, saver
    return_val = zeroer.process_data(last_data)
    # Make sure to use the unzeroed, raw data!

    if return_val == "False": program_mode = "EXIT"

    if "DATA" in return_val:
        rv = return_val.split(",")
        zero_data = [float(rv[1]), float(rv[2])]
        print("zeroed, b=", zero_data)
        saver.save_data(program_mode)
        saver.clear()
        add_header()


def main_handler():
    """
    Loops continuously, constantly getting called

    Does the handling of the remote connection, data streams

    Can be considered the 'main loop' of the system

    Essentially just takes in the data, saves it, then routes the data to
    visualization system is determined by the program_mode
    """
    # i really, need to refactor this to stop using the global vars
    global last_data, test_data, mvt, zeroed_last_data, remote_conn, data_conn, program_start_time, program_mode, saved_MVT_L, saved_MVT_R, demographic_info, const_error_target_perc, const_error_test

    # Parse commands first, to make sure that we're always in the proper program_state
    while remote_conn.poll():
        msg = remote_conn.recv()
        if msg[0] == "EXIT":
            handler_exit()

        elif msg[0] == "MS":
            program_mode = msg[1]
            program_state[0] = msg[1]

        elif msg[0] == "CMD":
            if msg[1] == "SAVE":
                if program_mode == "MVT_L":
                    saved_MVT_L = mvt.get_max_value()
                elif program_mode == "MVT_R":
                    saved_MVT_R = mvt.get_max_value()

                saver.save_data(program_mode)
            elif msg[1] == "CLEAR":
                saver.clear()
                add_header()

            elif msg[1] == "START":
                program_state[0] = "WAITING"
                if "MVT" in program_mode:
                    mvt.begin_automation()

                elif "ZERO" in program_mode:
                    zeroer.begin_zeroing()

                elif "CONST_ERROR" in program_mode:
                    const_error_test.begin_automation()
                
                elif "MAIN_GAME" in program_mode:
                    main_game.begin_automation()

        elif msg[0] == "DEMO":
            demographic_info = msg[1].copy()

        elif msg[0] == "MVT":
            saved_MVT_L, saved_MVT_R = msg[1]

        elif msg[0] == "TARGET_MVT":
            mvt.scale_max = msg[1]

        elif msg[0] == "ERRORPERC":
            const_error_target_perc = msg[1]

        elif msg[0] == "CONTINUE":
            test_data['continue'] = msg[1]

        elif msg[0] == "TRIALNUM":
            test_data['test_number'] = msg[1]
            test_data['number_of_tests'] = msg[2]

        elif msg[0] == "MATCH":
            const_error_test.match = True

    # Parse data commands (There may be many, but loop through and save all of them to ensure that we don't lose any)
    while data_conn.poll():
        msg = data_conn.recv()
        if msg[0] == "DATA":
            msg = msg[1]
            # Data comes in as TorqueL, TorqueR, Time
            # Save as trial_num, total_num_trials, raw_torqueL, raw_torqueR, zeroed_torqueL, zeroed_torqueR, MVT_L, MVT_R, Time, program_state,  then the various demographic info
            if msg[0] == None or msg[1] == None:
                continue

            last_data = [float(msg[0]), float(msg[1])]
            zeroed_last_data = zeroed(last_data)

            save_str =  f"{test_data['test_number']}, {test_data['number_of_tests']}, "
            save_str += f"{last_data[0]}, {last_data[1]}, "
            save_str += f"{zeroed_last_data[0]}, {zeroed_last_data[1]}, "
            save_str += f"{saved_MVT_L}, {saved_MVT_R}, "
            save_str += f"{float(msg[2]) - program_start_time}, "
            save_str += f"{program_state[0]}, "

            vals = demographic_info.values()
            vals = [str(x) for x in vals]

            save_str += ", ".join(vals)

            saver.add_data(save_str)


    # Send the mvt data repeatedly
    try:
        remote_conn.send(("MVT", saved_MVT_L, saved_MVT_R))
        remote_conn.send(("TARGET_MVT", mvt.scale_max))
        remote_conn.send(("CONTINUE", test_data['continue']))
        remote_conn.send(("TRIALDATA", test_data['continue'], test_data['test_number'], test_data['number_of_tests']))
    except EOFError:
        handler_exit()

    # Run methods conditionally based on the mode, calling the above handlers
    # ["DEV_MODE", "ZERO", "MVT_L", "MVT_R", "CONST_ERROR_L", "CONST_ERROR_R", "MAIN_GAME"]
    switcher = {
        "DEV_MODE":     handler_dev_mode,
        "ZERO":         handler_zero,
        "MVT_L":        handler_mvt_L,
        "MVT_R":        handler_mvt_R,
        "CONST_ERROR_L":handler_const_error_l,
        "CONST_ERROR_R":handler_const_error_r,
        "MAIN_GAME":    handler_main_game,
        "EXIT":         handler_exit
    }

    try:
        func = switcher[program_mode]
    except:
        print(f"Error with switcher in program_main. Program mode = {program_mode}")
        handler_exit()
    # Execute the switched into function
    func()


if __name__ == '__main__':
    # Socket ports. Ensure that these values are consistent with values in data streaming areas
    remote_port, data_port, plotter_port = 6006, 6007, 6008

    # Using a list so that I can give a ref to it
    program_state = ["DEV_MODE"]

    """
        Create the sockets for data intake
    """
    print("Waiting for Remote")
    address0 = ('localhost', remote_port)
    listener_0 = Listener(address0)
    remote_conn = listener_0.accept()
    print("Established remote")

    print("Waiting for data stream")
    address1 = ('localhost', data_port)
    listener_1 = Listener(address1)
    data_conn = listener_1.accept()
    print("connected to data stream")

    # print("Waiting for real time plotter")
    # address2 = ('localhost', plotter_port)
    # listener_2 = Listener(address2)
    # plotter_conn = listener_2.accept()
    # print("Connected to plotter")

    """
        Create data saver object
    """
    print("Creating data saver object")
    current_time = strftime(f"%b%d_%H%M", localtime())
    current_dir = current_time + "test"
    saver = data_saver(current_dir, program_state)
    print(f"Current time is {current_time}. Successfully created saver")

    program_mode = "DEV_MODE"

    """
        Initialize pygame and the other visual programs
    """
    pygame.init()
    if pygame.mixer and not pygame.mixer.get_init():
        print('Warning, no sound')
        pygame.mixer = None
        quit()

    width, height = 600, 600
    screen = pygame.display.set_mode((width, height))

    program_start_time = time.perf_counter()

    '''
    Initialize the sound cues
    '''
    audio_cues = {}
    audio_cues['starting'] = pygame.mixer.Sound('sound_effects/starttest.wav')

    audio_cues['relax'] = pygame.mixer.Sound('sound_effects/relax.wav')

    audio_cues['pull hard'] = pygame.mixer.Sound('sound_effects/pullhard.wav')

    audio_cues['beginning zero'] = pygame.mixer.Sound('sound_effects/beginningCalibration.wav')

    audio_cues['end zero'] = pygame.mixer.Sound('sound_effects/endCalibration.wav')

    audio_cues['pull to line'] = pygame.mixer.Sound('sound_effects/pullLine.wav')

    audio_cues['match forces'] = pygame.mixer.Sound('sound_effects/matchForces.wav')

    # Create MVT Object, to be used when needed
    mvt = mvt_viewer(screen, audio_cues, program_state)
    mvt.scale_max = 1.0

    test_data = {
        "test_number": 0,
        "number_of_tests": 100,
        "continue": False
    }

    """
    Create clearer object, that just serves to create a blank screen. This is
    needed, as pygame gets into problems if you don't give it update commands
    frequently enough
    """
    clearer = clearer(screen)

    main_game = bar_game(screen, test_data, audio_cues, program_state)

    const_error_test = error_test(screen, audio_cues, program_state, 30)

    zeroer = zeroer(screen, audio_cues, program_state)

    # global variables to store data during the test
    saved_MVT_L, saved_MVT_R = 1.0, 1.0

    # Array containing the zero matrix
    zero_data = [0, 0]

    const_error_target_perc = .25

    # Global variable to store last data as a buffer, in case there's an issue
    # or a break in the data collection
    last_data = [0, 0]
    zeroed_last_data = [0.0, 0.0]

    demographic_info = {
        "age": 0,
        "id": "NULL",
        "gender": "NULL",
        "subject type": "NULL",
        "diabetes": "NULL",
        "dominant arm": "NULL",
        "arm length": 0,
        "z offset": 0,
        "years_from_stroke": 0
    }

    # Forever loop that gets forcefully exited out of via the handler_exit
    while True:
        main_handler()
