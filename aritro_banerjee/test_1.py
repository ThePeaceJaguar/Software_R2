"""Example usage of drone simulator."""
import json
import time
import sys
import os
import math

drone_simulator_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'drone_simulator'))
sys.path.append(drone_simulator_path)

from drone import DroneSimulator

def calculate_tilt_angle(gyro):
    return math.sqrt(sum(g**2 for g in gyro))

def main():
    """Run the drone simulator example."""
    drone = DroneSimulator()

    base_speed = 4
    
    altitude_ref = {
        'GREEN':  175,
        'YELLOW': 3,
        'RED': 3
    }

    speed = base_speed
    altitude = altitude_ref['GREEN']
    dir = "fwd"
    total_altitude = 0

    alternate = True

    dt = 0.1
    x_angle = 0
    y_angle = 0
    z_angle = 0

    critical_wind = 30 #found from trial error, wind speed jumps about 40-50
    critical_dust = 35 #found from trial error, dust level jumps about 40
    
    try:
        while True:
            try:
                user_input = {
                    "speed": speed,
                    "altitude": altitude,
                    "movement": dir
                }
                altitude = 0

                telemetry = drone.update_telemetry(user_input)
                
                telemetry_data_str = json.dumps(telemetry)
                telemetry_data = json.loads(telemetry_data_str)
                print(telemetry_data)

                tilt_angle = calculate_tilt_angle(telemetry_data['gyroscope'])
                if tilt_angle > 1.5: #root(3), I see that's how gyro angle is being measured in the drone module
                    speed -= 1
                else:
                    speed = base_speed

                metrics = drone.get_metrics()
                metrics_str = json.dumps(metrics)
                metrics_data = json.loads(metrics_str)

                if (telemetry_data['y_position'] <= 0):
                    print('Drone landed!')
                    print('Battery: ' + str(round(telemetry_data['battery'], 2)) + '%')
                    print("Iterations: ", metrics['iterations'])
                    print("Total distance: ", metrics['total_distance'])
                    print("--"*50)
                
                    break

                total_altitude = telemetry_data['y_position']
                wind_speed = telemetry_data['wind_speed']
                dust_level = telemetry_data['dust_level']
                battery = telemetry_data['battery']

                if telemetry_data['sensor_status'] == "GREEN":
                    altitude = altitude_ref['GREEN'] - total_altitude if total_altitude <= altitude_ref['GREEN'] else 0

                if telemetry_data['sensor_status'] == "YELLOW" or wind_speed > critical_wind or dust_level > critical_dust:
                    altitude = altitude_ref['YELLOW'] - total_altitude if total_altitude >= altitude_ref['YELLOW'] else 0
                
                if telemetry_data['sensor_status'] == "RED":
                    speed = 5
                    altitude = altitude_ref['RED'] - total_altitude if total_altitude >= altitude_ref['RED'] else 0

                if battery < 30:
                    speed = 2

                if battery < 3:
                    altitude = - total_altitude if total_altitude > 0 else 0
                    speed = 0
                    
 
            except ValueError as e:
                print(e)
                break
                
            # Add delay
            time.sleep(dt)
            
    except KeyboardInterrupt:
        print("Simulation stopped.")

if __name__ == "__main__":
    main()