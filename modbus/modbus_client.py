from pymodbus.client import ModbusTcpClient
import sqlite3
import time
from datetime import datetime

# Connect to SQLite
conn = sqlite3.connect("database/process_data.db")
cursor = conn.cursor()

# Connect to Modbus Server
client = ModbusTcpClient("127.0.0.1", port=502)

if client.connect():
    print("✅ Connected to Modbus Server")
    print("Logging data every second...\n")

    try:
        while True:

            result = client.read_holding_registers(address=0, count=5)

            if not result.isError():

                registers = result.registers

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                tank_level = registers[0]
                temperature = registers[1]
                pressure = registers[2] / 10
                flow_rate = registers[3]
                motor_speed = registers[4]

                cursor.execute("""
                    INSERT INTO modbus_data
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    timestamp,
                    tank_level,
                    temperature,
                    pressure,
                    flow_rate,
                    motor_speed
                ))

                conn.commit()

                print(
                    f"{timestamp} | "
                    f"Level={tank_level} % |"
                    f"Temp={temperature}°C |"
                    f"Pressure={pressure:.1f} bar |"
                    f"Flow={flow_rate} L/min |"
                    f"Motor={motor_speed}RPM"
                )

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping logger...")

    client.close()
    conn.close()

else:
    print("❌ Could not connect to Modbus Server")