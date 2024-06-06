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

# Global wheel speed
WHEEL_SPEED = 50

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
    'FrontC': 30,
    'FrontRR': 20,
    'FrontLL': 20,
    'FrontL': 80,
    'FrontR': 80,
}

WALL_DODGE_THRESHOLDS = {
    'FrontC': 80,
    'FrontRR': 80,
    'FrontLL': 80,
}

def create_output_dirs(simulation):
    sim_or_hard = "_sim" if simulation else "_hard"
    grouped_data_dir = FIGRURES_DIR / "grouped_data" / f"{current_datetime}{sim_or_hard}"
    os.makedirs(grouped_data_dir, exist_ok=True)
    return grouped_data_dir

def plot_sensor_data(irs, title, grouped_data_dir):
    plt.figure()
    for sensor_index in range(len(irs[0])):
        sensor_values = [data[sensor_index] for data in irs]
        plt.plot(sensor_values, label=f'Sensor {sensor_index + 1}')
    plt.xlabel('Steps')
    plt.ylabel('IR Sensor Values')
    plt.title(title)
    plt.legend()
    plt.savefig(str(grouped_data_dir / f"{title}_sensor_plot_{current_datetime}.png"))

def save_to_csv(sensor_readings, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['BackL', 'BackR', 'FrontL', 'FrontR', 'FrontC', 'FrontRR', 'BackC', 'FrontLL', 'WallDodge', 'ObstacleDodge'])
        for data in sensor_readings:
            writer.writerow(data)

def save_meta_data(metadata, filename, grouped_data_dir):
    with open(grouped_data_dir / filename, 'w') as file:
        for key, value in metadata.items():
            file.write(f"{key}: {value}\n")

def task0_group_6(rob: IRobobo, steps: int = 100):
    """Task: Go straight until it touches the wall, then go backward."""
    sensor_readings = []
    obstacle_dodges = 0
    wall_dodges = 0
    total_steps = 0
    irs_logs = []
    if simulation:
        rob.play_simulation()
    try:
        for step in range(steps):
            total_steps += 1
            irs = rob.read_irs()
            is_obstacle_dodge = 0
            is_wall_dodge = 0

            if ( 
                irs[4] > WALL_DODGE_THRESHOLDS['FrontC'] or
                irs[5] > WALL_DODGE_THRESHOLDS['FrontRR'] or
                irs[7] > WALL_DODGE_THRESHOLDS['FrontLL']
            ):  
                print("'BackL', 'BackR', 'FrontL', 'FrontR', 'FrontC', 'FrontRR', 'BackC', 'FrontLL'")
                print(irs)
                irs_logs.append({'step': step, 'type': 'wall_dodge', 'values': irs})
                rob.move(-WHEEL_SPEED, -WHEEL_SPEED, 1000)  # Move backward
                rob.sleep(1)
                rob.move(0, 0, 0)  # Stop
                # rob.move(WHEEL_SPEED, -WHEEL_SPEED, 600)  # Turn right 90 degrees
                # rob.sleep(0.6)
                if irs[5] > WALL_DODGE_THRESHOLDS['FrontRR']:
                    rob.move(WHEEL_SPEED, -WHEEL_SPEED, 850)  # Turn right 90 degrees
                    # rob.sleep(0.1)
                elif irs[7] > WALL_DODGE_THRESHOLDS['FrontLL']:
                    rob.move(-WHEEL_SPEED, WHEEL_SPEED, 850)  # Turn left 90 degrees
                    # rob.sleep(0.1)
                else:
                    rob.move(WHEEL_SPEED, -WHEEL_SPEED, 850)  # Turn right 90 degrees
                    # rob.sleep(0.1)
                rob.sleep(0.85)
                print("Wall Dodge")
                wall_dodges += 1
                is_wall_dodge = 1
                print(f"Steps run: {step + 1} for wall_dodge: {wall_dodges}")
            
            elif (
                irs[4] > SENSOR_DODGE_THRESHOLDS['FrontC'] or
                irs[5] > SENSOR_DODGE_THRESHOLDS['FrontRR'] or
                irs[7] > SENSOR_DODGE_THRESHOLDS['FrontLL'] or
                irs[2] > SENSOR_DODGE_THRESHOLDS['FrontL'] or
                irs[3] > SENSOR_DODGE_THRESHOLDS['FrontR']
            ):
                print("'BackL', 'BackR', 'FrontL', 'FrontR', 'FrontC', 'FrontRR', 'BackC', 'FrontLL'")
                print(irs)
                irs_logs.append({'step': step, 'type': 'obstacle_dodge', 'values': irs})
                rob.move(0, 0, 0)  # Stop
                rob.sleep(0.1)
                if irs[5] > SENSOR_DODGE_THRESHOLDS['FrontRR']:
                    rob.move(WHEEL_SPEED, -WHEEL_SPEED, 850)  # Turn right 90 degrees
                    # rob.sleep(0.1)
                elif irs[7] > SENSOR_DODGE_THRESHOLDS['FrontLL']:
                    rob.move(-WHEEL_SPEED, WHEEL_SPEED, 850)  # Turn left 90 degrees
                    # rob.sleep(0.1)
                else:
                    rob.move(WHEEL_SPEED, -WHEEL_SPEED, 850)  # Turn right 90 degrees
                    # rob.sleep(0.1)
                rob.sleep(0.5)
                print("Obstacle Dodge")
                obstacle_dodges += 1
                is_obstacle_dodge = 1
                

            else:
                rob.move(100, 100, 350)
                rob.sleep(0.35)

            if wall_dodges == 4:
                print("Done")
                break

            sensor_readings.append(irs + [is_wall_dodge, is_obstacle_dodge])
    finally:
        if simulation:
            rob.stop_simulation()
        else:
            pass
    
    metadata = {
        'obstacle_dodges': obstacle_dodges,
        'wall_dodges': wall_dodges,
        'total_steps': total_steps,
        'irs_logs': irs_logs,
        'sensor_thresholds': SENSOR_THRESHOLDS,
        'sensor_dodge_thresholds': SENSOR_DODGE_THRESHOLDS,
        'wall_dodge_thresholds': WALL_DODGE_THRESHOLDS,
    }

    return sensor_readings, metadata

def run_all_actions(rob: IRobobo):
    grouped_data_dir = create_output_dirs(simulation)
    meta_data = {
        'date_time': current_datetime,
        'simulation': simulation,
        # 'sensor_thresholds': SENSOR_THRESHOLDS,
        'sensor_dodge_thresholds': SENSOR_DODGE_THRESHOLDS,
        'wall_dodge_thresholds': WALL_DODGE_THRESHOLDS
    }
    # save_meta_data(meta_data, 'meta_data.txt', grouped_data_dir)
    if isinstance(rob, SimulationRobobo) and simulation:
        rob.play_simulation()
    
    sensor_readings, task_metadata = task0_group_6(rob, steps=300)
    meta_data.update(task_metadata)
    save_meta_data(meta_data, 'meta_data_final.txt', grouped_data_dir)
    save_to_csv(sensor_readings, str(grouped_data_dir / f"2_o_{current_datetime}.csv"))
    plot_sensor_data(sensor_readings, 'Task0 Group6', grouped_data_dir)
    
    if isinstance(rob, SimulationRobobo) and simulation:
        rob.stop_simulation()
