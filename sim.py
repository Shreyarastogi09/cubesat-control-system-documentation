import numpy as np
import matplotlib.pyplot as plt
import random

# --- PIECE B: THE BRAIN (Controller) ---
class PIDController:
    def __init__(self, Kp, Ki, Kd, max_integral=50):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.integral = 0
        self.prev_error = 0
        # ANTI-WINDUP: Prevents the controller from over-memorizing errors
        self.max_integral = max_integral 

    def compute(self, error, dt):
        self.integral += error * dt
        
        # Apply Anti-Windup Limits
        if self.integral > self.max_integral:
            self.integral = self.max_integral
        elif self.integral < -self.max_integral:
            self.integral = -self.max_integral
            
        derivative = (error - self.prev_error) / dt
        output = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)
        self.prev_error = error
        return output

# --- PIECE A: THE PHYSICS (Plant) ---
class CubeSat:
    def __init__(self, J):
        self.J = J
        self.angle = 0.0
        self.velocity = 0.0

    def apply_torque(self, torque, dt):
        acceleration = torque / self.J
        self.velocity += acceleration * dt
        self.angle += self.velocity * dt
        return self.angle

# --- PIECE C: THE GAME LOOP (Main Simulation) ---
def run_simulation():
    # Setup Hardware
    satellite = CubeSat(J=0.0022)
    # Tuned Brain (Lowered P slightly, Doubled D for stronger brakes)
    controller = PIDController(Kp=0.01, Ki=0.0001, Kd=0.01)
    
    # State tracking for keyboard controls
    state = {
        'target': np.radians(90),
        'paused': False
    }
    
    dt = 0.1  
    time_data, angle_data, target_data = [], [], []
    
    # --- VISUAL UPGRADES ---
    plt.style.use('dark_background') 
    plt.ion()  
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.canvas.manager.set_window_title('ADCS Ground Control')

    # --- KEYBOARD CONTROLS ---
   # --- KEYBOARD CONTROLS ---
    def on_press(event):
        if event.key == 'up':
            state['target'] += np.radians(15)
        elif event.key == 'down':
            state['target'] -= np.radians(15)
        elif event.key == ' ': 
            state['paused'] = not state['paused']
        # --- NEW: THE SOLAR FLARE KICK ---
        elif event.key == 'right':
            # Instantly add a massive amount of velocity to the satellite
            satellite.velocity += 2.0 
            print("\n⚠️ WARNING: MASSIVE SOLAR FLARE DETECTED! (Pushed Right) ⚠️")
        elif event.key == 'left':
            satellite.velocity -= 2.0 
            print("\n⚠️ WARNING: MASSIVE SOLAR FLARE DETECTED! (Pushed Left) ⚠️")

    fig.canvas.mpl_connect('key_press_event', on_press)

    print("\n" + "="*40)
    print("🚀 ADVANCED ADCS SIMULATOR ONLINE")
    print("ENVIRONMENT: Solar Wind & Sensor Noise ACTIVE")
    print("CONTROLS:")
    print("  [UP] / [DOWN] : Steer Target")
    print("  [SPACEBAR]    : Pause / Resume")
    print("="*40 + "\n")
    
    step = 0
    while plt.fignum_exists(fig.number): 
        # If paused, keep window open but skip physics
        if state['paused']:
            plt.pause(0.1)
            continue

        current_time = step * dt
        
        # --- 1. SENSOR NOISE ---
        # The sensor isn't perfect, it jitters slightly
        noise = random.uniform(-0.001, 0.001) 
        measured_angle = satellite.angle + noise
        
        # Calculate Error based on the noisy reading
        error = state['target'] - measured_angle
        
        # Compute PID Command
        torque_command = controller.compute(error, dt)
        
        # --- 2. ACTUATOR LIMITS ---
        # Reaction wheels have a maximum speed/torque limit
        if torque_command > 0.5: torque_command = 0.5
        if torque_command < -0.5: torque_command = -0.5

        # --- 3. EXTERNAL DISTURBANCES ---
        # A constant solar radiation pressure is pushing the satellite
        solar_push = 0.005
        total_torque = torque_command + solar_push

        # Apply Physics
        satellite.apply_torque(total_torque, dt)
        
        # Save exact data (not noisy data) for plotting
        time_data.append(current_time)
        angle_data.append(np.degrees(satellite.angle))
        target_data.append(np.degrees(state['target']))

        # Draw frame (every 5 steps to keep animation smooth)
        if step % 3== 0:
            ax.clear() 
            
            display_time = time_data[-150:]
            display_angle = angle_data[-150:]
            display_target = target_data[-150:]
            
            # Neon Styling
            ax.plot(display_time, display_target, color='#FF3366', linestyle='--', linewidth=2, label='Target Angle')
            ax.plot(display_time, display_angle, color='#00E5FF', linewidth=3, label='CubeSat Actual Position')
            
            # Glow effect
            ax.fill_between(display_time, display_angle, np.degrees(state['target']), color='#00E5FF', alpha=0.1)
            
            # Scrolling X-Axis
            ax.set_xlim(max(0, current_time - 15), max(15, current_time + 2))
            
            # Dynamic Y-Axis
            current_target_deg = np.degrees(state['target'])
            ax.set_ylim(current_target_deg - 100, current_target_deg + 100) 
            
            ax.set_title('Live Telemetry (Spacebar to Pause, UP/DOWN to Steer)', color='white', fontsize=14, pad=15)
            ax.set_xlabel('Mission Time (s)', color='gray')
            ax.set_ylabel('Angle (deg)', color='gray')
            
            ax.legend(loc='upper left', facecolor='black', edgecolor='gray')
            ax.grid(color='#333333', linestyle='-', linewidth=0.5)
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            plt.pause(0.01) 
            
        step += 1

    plt.ioff()
    plt.show()

if __name__ == "__main__":
    run_simulation()

    # --- PIECE D: THE AI AUTO-GRADER (Headless Simulation) ---
def evaluate_fitness(Kp, Ki, Kd):
    # 1. Setup a fresh satellite for this test run
    satellite = CubeSat(J=0.0022)
    controller = PIDController(Kp, Ki, Kd)
    
    target = np.radians(90)
    dt = 0.1
    steps = int(30 / dt) # Exactly 30 seconds of physics
    
    # The Score Trackers
    total_error_penalty = 0
    total_power_penalty = 0
    
    # 2. Run the mission instantly (No graphs, no pauses!)
    for step in range(steps):
        error = target - satellite.angle
        torque = controller.compute(error, dt)
        
        if torque > 0.5: torque = 0.5
        if torque < -0.5: torque = -0.5
            
        satellite.apply_torque(torque, dt)
        
        # 3. Calculate Penalties
        # We use absolute value (abs) because being -10 degrees off is just as bad as +10.
        total_error_penalty += abs(error) 
        total_power_penalty += abs(torque) 

    # 4. Final Grade (Lower is better. 0 is a mathematically perfect flight)
    # We multiply power by 5 so the AI knows wasting battery is a big deal.
    final_score = total_error_penalty + (total_power_penalty * 5)
    
    return final_score

# --- TEST THE GRADER ---
# Put this at the very bottom of your file to test it before running the visual graph
if __name__ == "__main__":
    print("Grading Human Tuning...")
    human_score = evaluate_fitness(Kp=0.01, Ki=0.0001, Kd=0.1)
    print(f"Human Score: {human_score:.2f} penalties")
    
    print("\nGrading Terrible Tuning...")
    bad_score = evaluate_fitness(Kp=1.0, Ki=0, Kd=0) # Way too strong, no brakes
    print(f"Terrible Score: {bad_score:.2f} penalties\n")
    
    # Uncomment this if you still want to run the visual simulator afterward
    # run_simulation()