from pymodbus.client import ModbusTcpClient
import time
import random

# ----------------------------
# Connect to Modbus Server
# ----------------------------

client = ModbusTcpClient("127.0.0.1", port=502)

if not client.connect():
    print("❌ Could not connect to ModRSsim2")
    exit()

print("✅ Industrial Tank Process Simulator Started")

# ----------------------------
# Initial Process Values
# ----------------------------

tank = 20
temperature = 30
direction = "FILLING"

# ----------------------------
# Main Loop
# ----------------------------

try:

    while True:

        if direction == "FILLING":

            # Tank fills
            tank += random.randint(2, 5)

            if tank >= 100:
                tank = 100
                direction = "DRAINING"

            motor = 1450
            flow = random.randint(118, 123)

            # Pressure increases with tank level
            pressure = round(2.0 + tank * 0.01, 1)

            # Temperature rises slowly
            if temperature < 36:
                temperature += random.choice([0, 1])

        else:

            # Tank drains
            tank -= random.randint(2, 5)

            if tank <= 20:
                tank = 20
                direction = "FILLING"

            motor = 0
            flow = random.randint(0, 5)

            # Pressure decreases with tank level
            pressure = round(1.5 + tank * 0.008, 1)

            # Temperature cools slowly
            if temperature > 30:
                temperature -= random.choice([0, 1])

        # ----------------------------
        # Safety Limits
        # ----------------------------

        tank = max(20, min(100, tank))
        temperature = max(30, min(36, temperature))

        pressure = max(1.5, min(3.0, pressure))

        # ----------------------------
        # Write ALL registers together
        # ----------------------------

        registers = [
            tank,                   # Register 0
            temperature,            # Register 1
            int(pressure * 10),     # Register 2
            flow,                   # Register 3
            motor                   # Register 4
        ]

        client.write_registers(0, registers)

        print(
            f"{direction:<9}"
            f" | Tank={tank:3}%"
            f" | Temp={temperature}°C"
            f" | Pressure={pressure:.1f} bar"
            f" | Flow={flow:3} L/min"
            f" | Motor={motor:4} RPM"
        )

        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping simulator...")

finally:
    client.close()