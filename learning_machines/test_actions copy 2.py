# .\scripts\start_coppelia_sim.ps1 .\scenes\Robobo_Scene.ttt
# .\scripts\run.ps1 --simulation

import cv2
import matplotlib.pyplot as plt

from data_files import FIGRURES_DIR
from robobo_interface import (
    IRobobo,
    Emotion,
    LedId,
    LedColor,
    SoundEmotion,
    SimulationRobobo,
    HardwareRobobo,
)

def test_emotions(rob: IRobobo):
    rob.set_emotion(Emotion.HAPPY)
    rob.talk("Hello")
    rob.play_emotion_sound(SoundEmotion.PURR)
    rob.set_led(LedId.FRONTCENTER, LedColor.GREEN)

def test_move_and_wheel_reset(rob: IRobobo):
    rob.move_blocking(100, 100, 1000)
    print("before reset: ", rob.read_wheels())
    rob.reset_wheels()
    rob.sleep(1)
    print("after reset: ", rob.read_wheels())

def test_sensors(rob: IRobobo):
    print("IRS data: ", rob.read_irs())
    image = rob.get_image_front()
    cv2.imwrite(str(FIGRURES_DIR / "photo.png"), image)
    print("Phone pan: ", rob.read_phone_pan())
    print("Phone tilt: ", rob.read_phone_tilt())
    print("Current acceleration: ", rob.read_accel())
    print("Current orientation: ", rob.read_orientation())

def test_phone_movement(rob: IRobobo):
    rob.set_phone_pan_blocking(20, 100)
    print("Phone pan after move to 20: ", rob.read_phone_pan())
    rob.set_phone_tilt_blocking(50, 100)
    print("Phone tilt after move to 50: ", rob.read_phone_tilt())

def test_sim(rob: SimulationRobobo):
    print(rob.get_sim_time())
    print(rob.is_running())
    rob.stop_simulation()
    print(rob.get_sim_time())
    print(rob.is_running())
    rob.play_simulation()
    print(rob.get_sim_time())
    print(rob.get_position())

def test_hardware(rob: HardwareRobobo):
    print("Phone battery level: ", rob.read_phone_battery())
    print("Robot battery level: ", rob.read_robot_battery())


# Task 1: Go straight until an object is near, then turn 180 degrees and continue until hitting a wall
def task1(rob: IRobobo, repetitions: int):
    ir_data = []
    for _ in range(repetitions):
        while True:
            irs = rob.read_irs()
            ir_data.append(irs)
            print(f"Task 1 IR Sensor Data: {irs[4]}")

            rob.move(50, 50, 100)  # Move straight
            rob.sleep(0.1)
            if irs[4] > 10:  # FrontC sensor detects an object
                # Perform 180-degree turn
                rob.move(-50, 50, 1000)  # Rotate right in place for 1 second
                rob.sleep(1)  # Allow time to complete the turn
                break

        while True:
            irs = rob.read_irs()
            ir_data.append(irs)
            print(f"Task 1 IR Sensor Data: {irs[4]}")

            rob.move(50, 50, 100)  # Move straight
            rob.sleep(0.1)
            if irs[4] > 10:  # FrontC sensor detects an object
                break

    return ir_data





# Task 2: Go straight until it touches a wall, then go backward
def task2(rob: IRobobo, repetitions: int):
    ir_data = []

    for _ in range(repetitions):
        while True:
            irs = rob.read_irs()
            ir_data.append(irs)
            if min(irs) < 10:  # Threshold for touching the wall
                rob.move(-50, -50, 1000)  # Move backward for 5 seconds
                rob.sleep(5)  # Allow some time to move back
                break
            rob.move(50, 50, 100)  # Move straight for 0.1 seconds
            rob.sleep(0.1)

    return ir_data


def plot_sensor_data(ir_data, title):
    plt.figure()
    for sensor_index in range(len(ir_data[0])):
        sensor_values = [data[sensor_index] for data in ir_data]
        plt.plot(sensor_values, label=f'Sensor {sensor_index + 1}')
    plt.xlabel('Time Steps')
    plt.ylabel('IR Sensor Values')
    plt.title(title)
    plt.legend()
    plt.savefig(str(FIGRURES_DIR / f"{title}_sensor_plot.png"))

def run_all_actions(rob: IRobobo):
    repetitions = 50  # Define the number of repetitions for each task
    
    if isinstance(rob, SimulationRobobo):
        rob.play_simulation()
    
    # Example Task 1
    print("Running Task 1")
    ir_data_task1 = task1(rob, repetitions)
    plot_sensor_data(ir_data_task1, 'Task 1')
    
    print("Running Task 2")
    # Example Task 2
    ir_data_task2 = task2(rob, repetitions)
    plot_sensor_data(ir_data_task2, 'Task 2')
    
    print("All tasks completed")
    
    # print("Running all tests")

    # # The following lines are optional to perform other tests
    # test_emotions(rob)
    # test_sensors(rob)
    # test_move_and_wheel_reset(rob)

    # if isinstance(rob, SimulationRobobo):
    #     test_sim(rob)

    # if isinstance(rob, HardwareRobobo):
    #     test_hardware(rob)

    # test_phone_movement(rob)

    # if isinstance(rob, SimulationRobobo):
    #     rob.stop_simulation()
        
    # print("All tests completed")

