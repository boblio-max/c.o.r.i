# C.O.R.I Centralized Configuration
# This file holds all the critical settings for the robot. 
# Change these values here, and they will update across the entire system.

# --- NETWORK SETTINGS ---
SERVER_HOST = "192.168.1.20"  # IP address of the server (or Pi, if running server there)
SERVER_PORT = 8765

# --- HARDWARE SETTINGS (RASPBERRY PI) ---
# Mapping of logical joints to physical PWM channels on the ServoKit
SERVO_MAP = {
    'base': 11,          # A1: Base rotation
    'shoulder': 12,      # A2: Shoulder
    'elbow': 13,         # A3: Elbow
    'wrist': 14,         # A4: Wrist
    'claw': 15,          # Claw/Grabber
    'spare': 10          # Extra servo
}

# The ordered list of servo indices expected by the payload (must be length 6)
SERVO_INDICES = [
    SERVO_MAP['base'],
    SERVO_MAP['shoulder'],
    SERVO_MAP['elbow'],
    SERVO_MAP['wrist'],
    SERVO_MAP['claw'],
    SERVO_MAP['spare']
]

# The default "safe" pose the robot will return to if connection is lost.
# [base, shoulder, elbow, wrist, claw, spare]
SAFE_POSE = [180.0, 180.0, 90.0, 90.0, 0.0, 0.0]

# --- SAFETY LIMITS ---
# Minimum and maximum allowable angles for the servos
SERVO_MIN_ANGLE = 0
SERVO_MAX_ANGLE = 180
