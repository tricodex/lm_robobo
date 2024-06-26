import cv2
import matplotlib.pyplot as plt
import csv
from data_files import FIGRURES_DIR
from robobo_interface import (
    IRobobo,
    SimulationRobobo,
    HardwareRobobo,
)
from datetime import datetime
current_datetime = datetime.now().strftime("%Y%m%d-%H%M%S") 

def plot_sensor_data(irs, title):
    plt.figure()
    for sensor_index in range(len(irs[0])):
        sensor_values = [data[sensor_index] for data in irs]
        plt.plot(sensor_values, label=f'Sensor {sensor_index + 1}')
    plt.xlabel('Steps')
    plt.ylabel('IR Sensor Values')
    plt.title(title)
    plt.legend()
    plt.savefig(str(FIGRURES_DIR / f"{title}_sensor_plot{current_datetime}.png"))

def save_to_csv(sensor_readings, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['BackL', 'BackR', 'FrontL', 'FrontR', 'FrontC', 'FrontRR', 'BackC', 'FrontLL'])
        for data in sensor_readings:
            writer.writerow(data)

def task_example_1(rob: IRobobo, steps: int = 100):
    """Task: Go straight until an object is near, then turn right without touching it."""
    sensor_readings = []
    #rob.play_simulation()
    try:
        for step in range(steps):
            irs = rob.read_irs()
            sensor_readings.append(irs)
            if irs[4] > 40 or irs[5] > 40 or irs[7] > 40:  # All front sensors
                rob.move(0, 0, 0)  # Stop
                rob.sleep(0.1)
                rob.move(50, -50, 500)  # Turn right
                rob.sleep(0.1)
                rob.move(50, 50, 1000)
                rob.sleep(10)
                print(f"Steps run: {step + 1}")
                break
            else:
                rob.move(50, 50, 100)  # Go straight
            rob.sleep(0.1)
    finally:
        #rob.stop_simulation()
        pass
    plot_sensor_data(sensor_readings, "taske_1")
    save_to_csv(sensor_readings, str(FIGRURES_DIR / f"1_{current_datetime}.csv"))

def task_example_2(rob: IRobobo, steps: int = 100):
    """Task: Go straight until it touches the wall, then go backward."""
    sensor_readings = []
    turns = 0
    obstacle_sensor_threshold = 10
    wall_sensor_threshold = 50 
    #rob.play_simulation()
    try:
        for step in range(steps):
            irs = rob.read_irs()
            sensor_readings.append(irs)
            
            
            if irs[4] > 10 or irs[5] > 10 or irs[7] > 10:  
                rob.move(-50, -50, 150)  # Move backward
                # rob.sleep(0.3)
                # rob.move(0, 0, 0)  # Stop
                if irs[5] > 10:
                    rob.move(50, -50, 850) # turn right 90 degrees
                elif irs[7] > 10:
                    rob.move(-50, 50, 850)
                else:
                    rob.move(50, -50, 850)
                # rob.sleep(0.85)
                print("Obstacle Dodge")
            else:
                rob.move(75, 75, 250)  # Go straight
                # rob.sleep(0.250)

            # print(irs[4])
            # 'BackL', 'BackR', 'FrontL', 'FrontR', 'FrontC', 'FrontRR'5 'BackC', 'FrontLL'7
            
            if irs[4] > 40 or irs[2] > 70 or irs[3] > 70: 
                # if irs[4] > 60:
                #     rob.move(-50, -50, 1000)
                rob.move(-50, -50, 1000)  # Move backward
                # rob.sleep(1)
                rob.move(0, 0, 0)  # Stop
                rob.move(50, -50, 600) # turn right 90 degrees
                # rob.sleep(0.6)
                print("Wall Dodge")
                turns += 1 # Turn    
                print(f"Steps run: {step + 1} for turn: {turns}")

                
            else:
                rob.move(75, 75, 250)  # Go straight
                rob.sleep(0.25)

            if turns == 4:
                print("Done")
                break
    finally:
        #rob.stop_simulation()
        pass
    plot_sensor_data(sensor_readings, "task_2")
    save_to_csv(sensor_readings, str(FIGRURES_DIR / f"2_o{obstacle_sensor_threshold}_w{wall_sensor_threshold}_{current_datetime}.csv"))

def run_all_actions(rob: IRobobo):
    if isinstance(rob, SimulationRobobo):
        rob.play_simulation()
    # print("task 1")
    # task_example_1(rob, steps=1000)
    print("task 2")
    task_example_2(rob, steps=300)
    if isinstance(rob, SimulationRobobo):
        rob.stop_simulation()
