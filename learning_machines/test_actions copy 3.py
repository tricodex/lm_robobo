import cv2
import matplotlib.pyplot as plt
import csv
from data_files import FIGRURES_DIR
from robobo_interface import (
    IRobobo,
    SimulationRobobo,
    HardwareRobobo,
)
import os
from datetime import datetime

current_datetime = datetime.now().strftime("%Y%m%d-%H%M%S") 

simulation = False

# Sensor thresholds (adjustable)
SENSOR_THRESHOLDS = {
    'BackL': 10,
    'BackR': 10,
    'FrontL': 10,
    'FrontR': 10,
    'FrontC': 10,
    'FrontRR': 10,
    'BackC': 10,
    'FrontLL': 10,
}

# Thresholds specific to task_example_2
SENSOR_DODGE_THRESHOLDS = {
    'FrontC': 10,
    'FrontRR': 10,
    'FrontLL': 10,
    'FrontL': 80,
    'FrontR': 80,
}

WALL_DODGE_THRESHOLDS = {
    'FrontC': 40
}

def create_output_dirs(simulation):
    sim_or_hard = "_sim" if simulation else "_hard"
    grouped_data_dir = FIGRURES_DIR / "grouped_data" / f"{current_datetime}{sim_or_hard}"
    os.makedirs(grouped_data_dir, exist_ok=True)
    return grouped_data_dir

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

def save_meta_data(metadata, filename, grouped_data_dir):
    with open(grouped_data_dir / filename, 'w') as file:
        for key, value in metadata.items():
            file.write(f"{key}: {value}\n")

def task_example_1(rob: IRobobo, steps: int = 100):
    """Task: Go straight until an object is near, then turn right without touching it."""
    sensor_readings = []
    if simulation:
        rob.play_simulation()
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
        if simulation:
            rob.stop_simulation()
    plot_sensor_data(sensor_readings, "task_1")
    save_to_csv(sensor_readings, str(FIGRURES_DIR / f"1_{current_datetime}.csv"))

def task_example_2(rob: IRobobo, steps: int = 100):
    """Task: Go straight until it touches the wall, then go backward."""
    sensor_readings = []
    turns = 0
    obstacle_dodges = 0
    wall_dodges = 0
    if simulation:
        rob.play_simulation()
    try:
        for step in range(steps):
            irs = rob.read_irs()
            sensor_readings.append(irs)
            
            # irs = 'BackL', 'BackR', 'FrontL', 'FrontR', 'FrontC', 'FrontRR', 'BackC', 'FrontLL'
            if (
                irs[4] > SENSOR_DODGE_THRESHOLDS['FrontC'] or
                irs[5] > SENSOR_DODGE_THRESHOLDS['FrontRR'] or
                irs[7] > SENSOR_DODGE_THRESHOLDS['FrontLL'] or
                irs[2] > SENSOR_DODGE_THRESHOLDS['FrontL'] or
                irs[3] > SENSOR_DODGE_THRESHOLDS['FrontR']
            ):
                rob.move(-50, -50, 150)  # Move backward
                rob.sleep(0.3)
                if irs[5] > SENSOR_DODGE_THRESHOLDS['FrontRR']:
                    rob.move(50, -50, 850)  # Turn right 90 degrees
                elif irs[7] > SENSOR_DODGE_THRESHOLDS['FrontLL']:
                    rob.move(-50, 50, 850)  # Turn left 90 degrees
                else:
                    rob.move(50, -50, 850)  # Turn right 90 degrees
                rob.sleep(0.85)
                print("Obstacle Dodge")
                obstacle_dodges += 1
                
            else:
                rob.move(75, 75, 250)  # Go straight
            
            if irs[4] > WALL_DODGE_THRESHOLDS['FrontC']:  
                rob.move(-50, -50, 1000)  # Move backward
                rob.sleep(1)
                rob.move(0, 0, 0)  # Stop
                rob.move(50, -50, 600)  # Turn right 90 degrees
                rob.sleep(0.6)
                print("Wall Dodge")
                turns += 1
                wall_dodges += 1
                print(f"Steps run: {step + 1} for turn: {turns}")

            if turns == 4:
                print("Done")
                break
    finally:
        if simulation:
            rob.stop_simulation()
    plot_sensor_data(sensor_readings, "task_2")
    save_to_csv(sensor_readings, str(FIGRURES_DIR / f"2_o_{current_datetime}.csv"))

def run_all_actions(rob: IRobobo):
    grouped_data_dir = create_output_dirs(simulation)
    meta_data = {
        'date_time': current_datetime,
        'simulation': simulation,
        'sensor_thresholds': SENSOR_THRESHOLDS,
        'sensor_dodge_thresholds': SENSOR_DODGE_THRESHOLDS,
        'wall_dodge_thresholds': WALL_DODGE_THRESHOLDS
    }
    save_meta_data(meta_data, 'meta_data.txt', grouped_data_dir)
    if isinstance(rob, SimulationRobobo) and simulation:
        rob.play_simulation()
    # task_example_1(rob, steps=1000)
    task_example_2(rob, steps=300)
    if isinstance(rob, SimulationRobobo) and simulation:
        rob.stop_simulation()

