from multiprocessing.connection import Listener
from data_saver import data_saver

from mvt_viewer import mvt_viewer
from data_saver import data_saver
from clear_screen import clearer
from main_game import game

import pygame
from pygame.locals import *

import time
from time import strftime, localtime

program_modes = ["DEV_MODE", "MVT_L", "MVT_R", "MAIN_GAME", "CALIBRATE"]

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
    global mvt, program_mode, last_data
    return_val = mvt.process_data(last_data[0])
            
    if return_val == "EXIT": program_mode = "EXIT"

    if str(type(return_val)) == "<class 'str'>" and "SAVE" in return_val:
        return_val = return_val.split(",")
        saved_MVT_L = float(return_val[1])

        saver.save_data(program_mode)

def handler_mvt_R():
    global mvt, program_mode, last_data
    return_val = mvt.process_data(last_data[1])
            
    if return_val == "EXIT": program_mode = "EXIT"

    if str(type(return_val)) == "<class 'str'>" and "SAVE" in return_val:
        return_val = return_val.split(",")
        saved_MVT_R = float(return_val[1])

        saver.save_data(program_mode)

def handler_main_game():
    global program_mode, main_game
    return_val = main_game.update_tick(last_data[0], last_data[1])
    
    if return_val == False: program_mode = "EXIT"

def handler_calibrate():
    global program_mode
    handler_dev_mode()
    # Just clear the screen for now; calibration module has not been implemented!


def main_handler():
    """
    Loops continuously, constantly getting called

    Does the handling of the remote connection, data streams

    Can be considered the 'main loop' of the system 

    Essentially just takes in the data, saves it, then routes the data to whateer visualization system
    is determined by the program_mode
    """
    global last_data, remote_conn, data_conn, program_start_time, program_mode, saved_MVT_L, saved_MVT_R

    # Parse commands first, to make sure that we're always in the proper state
    while remote_conn.poll():
        msg = remote_conn.recv()
        print(msg)
        if msg[0] == "EXIT":
            handler_exit()

        elif msg[0] == "MS":
            program_mode = msg[1]

        elif msg[0] == "CMD":
            if msg[1] == "SAVE":
                if program_mode == "MVT_L":
                    saved_MVT_L = mvt.get_max_value()
                elif program_mode == "MVT_R":
                    saved_MVT_R = mvt.get_max_value()

                saver.save_data(program_mode)
            elif msg[1] == "CLEAR":
                saver.clear()

            elif msg[1] == "START":
                if "MVT" in program_mode:
                    mvt.begin_automation()

    # Parse data commands (There may be many, but loop through and save all of them to ensure that we don't lose any)
    while data_conn.poll():
        msg = data_conn.recv()
        if msg[0] == "DATA":
            msg = msg[1]
            # Data comes in as TorqueL, TorqueR, Time
            # Save as TorqueL, TorqueR, MVT_L, MVT_R, Time
            saver.add_data(f"{msg[0]},{msg[1]},{saved_MVT_L},{saved_MVT_R},{float(msg[2]) - program_start_time}")
            last_data = [msg[0], msg[1]]


    # Run methods conditionally based on the mode, calling the above handlers
    switcher = {
        "DEV_MODE":handler_dev_mode,
        "MVT_L":handler_mvt_L,
        "MVT_R":handler_mvt_R,
        "MAIN_GAME":handler_main_game,
        "EXIT":handler_exit,
        "CALIBRATE":handler_calibrate
    }

    try:
        func = switcher[program_mode]
    except:
        print(f"Error with switcher in program_main. Program mode = {program_mode}")
        handler_exit()
     # Execute the switched into function
    func()


if __name__ == '__main__':
    # Socket ports. Ensure that these values are consistent with
    # values in data streaming areas
    remote_port, data_port = 6006, 6007

    """
        Create the sockets for data intake
    """
    print("Waiting for Remote")
    address0 = ('localhost', remote_port)
    listener_0 = Listener(address0)
    remote_conn = listener_0.accept()
    print("Established remote")

    print("Waiting for data stream")
    address = ('localhost', data_port)
    listener_1 = Listener(address)
    data_conn = listener_1.accept()
    print("connected to data stream")

    """
        Create data saver object
    """
    print("Creating data saver object")
    current_time = strftime(f"%b%d_%H%M", localtime())
    current_dir = current_time + "test"
    saver = data_saver(current_dir)
    print(f"Current time is {current_time}. Successfully created saver")

    program_mode = "DEV_MODE"

    """
        Initialize pygame and the other visual programs
    """
    # pygame.mixer.pre_init(44100, 16, 2, 4096)

    pygame.init()
    if pygame.mixer and not pygame.mixer.get_init():
        print ('Warning, no sound')
        pygame.mixer = None
        quit()
    
    width, height = 600, 600
    screen = pygame.display.set_mode((width, height))

    program_start_time = time.perf_counter()

    '''Initialize the sound cues
    '''
    audio_cues = {}
    effect = pygame.mixer.Sound('sound_effects/starttest.wav')
    audio_cues['starting'] = effect


    effect = pygame.mixer.Sound('sound_effects/relax.wav')
    audio_cues['relax'] = effect

    effect = pygame.mixer.Sound('sound_effects/pullhard.wav')
    audio_cues['pull hard'] = effect

    # Create MVT Object, to be used when needed
    mvt = mvt_viewer(width, height, screen, audio_cues)
    mvt.scale_max = 1.0

    # Create clearer object, that just serves to create a blank screen. This is
    # needed, as pygame gets into problems if you don't give it update commands
    # frequently enough 
    clearer = clearer(screen)

    main_game = game(screen, width, height, 19)

    # global variables to store data during the test
    saved_MVT_L, saved_MVT_R = 0, 0

    # Global variable to store last data as a buffer, in case there's an issue 
    # or a break in the data collection 
    last_data = [0, 0]

    # Forever loop that gets forcefully exited out of via the handler_exit
    while True:
        main_handler()
