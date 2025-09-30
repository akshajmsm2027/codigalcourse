"""
Pseudo-3D Car Dodger (no downloads) — tkinter only.

Save as car_3d_fake.py and run:
    python car_3d_fake.py

This simulates 3D by using a simple perspective projection:
 - Each obstacle has a 'z' (distance). As z decreases, its screen position and scale change.
 - Road lines and roadside scale with perspective to create depth.
"""

import tkinter as tk
import random
import time
import math

# --- Config ---
WIDTH = 640
HEIGHT = 480
FPS = 60
TICK_MS = int(1000 / FPS)

LANE_COUNT = 3
ROAD_WIDTH_AT_BOTTOM = 420
ROAD_WIDTH_AT_HORIZON = 40
HORIZON_Y = 120

CAR_BASE_WIDTH = 80
CAR_BASE_HEIGHT = 140
CAR_Y_POS = HEIGHT - CAR_BASE_HEIGHT - 20

MAX_SPEED = 140.0   # units per second (virtual)
MIN_SPEED = 0.0

OBSTACLE_MIN_Z = 0.5   # closest
OBSTACLE_MAX_Z = 6.5   # farthest spawn

SPAWN_INTERVAL_SEC = 0.9

# Perspective projection helpers
def interp(a, b, t): return a + (b - a) * t

def world_to_screen(x_norm, z):
    """
    x_norm: -1 (left edge of road) .. +1 (right edge of road)
    z: distance (0 = camera, larger = far)
    returns (sx, sy, scale)
    """
    # map z in [NEAR_Z, FAR_Z] to perspective t in [0..1] where 1 is horizon
    # use simple inverse relation: larger z => closer to horizon
    # clamp z
    zc = max(0.001, min(z, OBSTACLE_MAX_Z))
    t = (zc - OBSTACLE_MIN_Z) / (OBSTACLE_MAX_Z - OBSTACLE_MIN_Z)
    sy = interp(HEIGHT, HORIZON_Y, t)
    road_width = interp(ROAD_WIDTH_AT_BOTTOM, ROAD_WIDTH_AT_HORIZON, t)
    sx = WIDTH/2 + x_norm * (road_width/2)
    # scale: objects farther are smaller
    scale = interp(1.0, 0.15, t)
    return sx, sy, scale

# --- Game ---
class Fake3DGame:
    def __init__(self, root):
        self.root = root
        root.title("Pseudo-3D Car — No Downloads")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#4a8fb6")
        self.canvas.pack()
        self.last_time = time.time()
        self.running = True

        # Player state
        self.car_x = 0.0  # -1..+1 across road
        self.car_speed = 60.0  # virtual
        self.score = 0
        self.pressed = {"Left": False, "Right": False, "Up": False, "Down": False}

        # Obstacles: list of dict {x_norm, z, width, height, id}
        self.obstacles = []
        self.last_spawn = 0.0
        self.spawn_interval = SPAWN_INTERVAL_SEC

        # Bind keys
        root.bind("<KeyPress>", self.on_key)
        root.bind("<KeyRelease>", self.on_key_release)

        # HUD
        self.hud_score = None
        self.hud_speed = None

        # draw initial scene
        self.draw_static()
        self.reset()
        self.loop()

    def reset(self):
        self.canvas.delete("dynamic")
        self.obstacles.clear()
        self.car_x = 0.0
        self.car_speed = 60.0
        self.score = 0
        self.running = True
        self.last_spawn = time.time()
        self.spawn_interval = SPAWN_INTERVAL_SEC

    def draw_static(self):
        """Draw sky, horizon, road banks once"""
        self.canvas.delete("static")
        # sky gradient simulation (simple rectangles)
        for i in range(6):
            c = 200 - i*14
            self.canvas.create_rectangle(0, i * 80, WIDTH, (i+1)*80,
                                         fill=f'#{c:02x}{(180+i*5):02x}{(200+i*3):02x}',
                                         width=0, tags="static")
        # horizon line
        self.canvas.create_line(0, HORIZON_Y, WIDTH, HORIZON_Y, fill="#cfe8ff", width=2, tags="static")

    def on_key(self, e):
        k = e.keysym
        if k in self.pressed:
            self.pressed[k] = True
        if k.lower() == 'r':
            self.reset()
        if k == "Escape":
            self.root.quit()

    def on_key_release(self, e):
        k = e.keysym
        if k in self.pressed:
            self.pressed[k] = False

    def spawn_obstacle(self):
        # choose lane-ish x_norm (-1..1) but allow some jitter
        lane = random.randrange(LANE_COUNT)
        lane_pos = -1 + (2 * lane) / (LANE_COUNT - 1) if LANE_COUNT > 1 else 0
        jitter = (random.random() - 0.5) * 0.6  # allow spread
        x_norm = max(-1.0, min(1.0, lane_pos + jitter))
        z = random.uniform(OBSTACLE_MAX_Z * 0.7, OBSTACLE_MAX_Z)
        w = random.uniform(0.4, 0.9)  # relative width
        h = random.uniform(0.2, 0.6)  # relative height
        obs = {"x": x_norm, "z": z, "w": w, "h": h, "id": None}
        self.obstacles.append(obs)

    def update(self, dt):
        # speed control
        if self.pressed["Up"]:
            self.car_speed = min(MAX_SPEED, self.car_speed + 80 * dt)
        if self.pressed["Down"]:
            self.car_speed = max(MIN_SPEED, self.car_speed - 120 * dt)
        # lateral movement proportional to speed for feel
        move_speed = 1.6 * (self.car_speed/60.0)
        if self.pressed["Left"]:
            self.car_x -= move_speed * dt
        if self.pressed["Right"]:
            self.car_x += move_speed * dt
        # clamp car_x to road edges (-1..1)
        self.car_x = max(-0.9, min(0.9, self.car_x))

        # spawn obstacles based on time and difficulty
        now = time.time()
        if now - self.last_spawn > self.spawn_interval:
            self.spawn_obstacle()
            self.last_spawn = now
            # slowly increase difficulty by shortening interval
            self.spawn_interval = max(0.25, self.spawn_interval * 0.985)

        # move obstacles toward camera: decrease z based on car_speed
        # Convert car_speed units to z units per second; tune for feel
        for obs in list(self.obstacles):
            # obstacles move toward player faster when player speed is higher
            obs["z"] -= (self.car_speed / 60.0) * 1.2 * dt
            if obs["z"] < OBSTACLE_MIN_Z:
                # passed the player -> remove and score
                self.obstacles.remove(obs)
                self.score += 10

        # check collisions
        if self.check_crash():
            self.running = False

    def check_crash(self):
        # get player's screen rect
        car_sx, car_sy, car_scale = world_to_screen(self.car_x, OBSTACLE_MIN_Z + 0.02)
        cw = CAR_BASE_WIDTH * car_scale
        ch = CAR_BASE_HEIGHT * car_scale
        car_rect = (car_sx - cw/2, car_sy - ch, car_sx + cw/2, car_sy)
        for obs in self.obstacles:
            sx, sy, s = world_to_screen(obs["x"], obs["z"])
            ow = obs["w"] * CAR_BASE_WIDTH * s * 1.1
            oh = obs["h"] * CAR_BASE_HEIGHT * s * 1.1
            obs_rect = (sx - ow/2, sy - oh, sx + ow/2, sy)
            # simple AABB collision
            if (car_rect[0] < obs_rect[2] and car_rect[2] > obs_rect[0] and
                car_rect[1] < obs_rect[3] and car_rect[3] > obs_rect[1]):
                return True
        return False

    def draw_road(self):
        # draw road trapezoid
        self.canvas.delete("road")
        # four corners of road in screen coords using left/right at bottom and horizon
        left_bottom = (WIDTH/2 - ROAD_WIDTH_AT_BOTTOM/2, HEIGHT)
        right_bottom = (WIDTH/2 + ROAD_WIDTH_AT_BOTTOM/2, HEIGHT)
        left_h = (WIDTH/2 - ROAD_WIDTH_AT_HORIZON/2, HORIZON_Y)
        right_h = (WIDTH/2 + ROAD_WIDTH_AT_HORIZON/2, HORIZON_Y)
        self.canvas.create_polygon(left_bottom + right_bottom + right_h + left_h,
                                   fill="#2b2b2b", outline="", tags="road")
        # roadside strips
        self.canvas.create_polygon(0, HEIGHT, left_bottom[0], HEIGHT, left_h[0], HORIZON_Y, 0, HORIZON_Y,
                                   fill="#124", outline="", tags="road")
        self.canvas.create_polygon(WIDTH, HEIGHT, right_bottom[0], HEIGHT, right_h[0], HORIZON_Y, WIDTH, HORIZON_Y,
                                   fill="#124", outline="", tags="road")
        # dashed center line segments (in world z space)
        self.canvas.delete("center_dashes")
        for z in [i * 0.5 + 0.5 for i in range(int(OBSTACLE_MAX_Z*2))]:
            sx, sy, s = world_to_screen(0, z)
            dash_w = 8 * s
            dash_h = 28 * s
            if sy < HEIGHT - 10 and sy > HORIZON_Y + 10:
                self.canvas.create_rectangle(sx - dash_w/2, sy - dash_h/2, sx + dash_w/2, sy + dash_h/2,
                                             fill="#eee", width=0, tags=("road","center_dashes"))

    def draw_dynamic(self):
        # remove previous dynamic items
        self.canvas.delete("dynamic")
        # road + dashes
        self.draw_road()

        # draw obstacles (farther ones first)
        sorted_obs = sorted(self.obstacles, key=lambda o: o["z"], reverse=True)
        for obs in sorted_obs:
            sx, sy, s = world_to_screen(obs["x"], obs["z"])
            ow = obs["w"] * CAR_BASE_WIDTH * s
            oh = obs["h"] * CAR_BASE_HEIGHT * s
            # simple car/box shape
            left = sx - ow/2
            right = sx + ow/2
            top = sy - oh
            bottom = sy
            shade = int(180 - s * 120)
            color = f'#{shade:02x}{50:02x}{50:02x}'  # red-ish scaled
            rect_id = self.canvas.create_rectangle(left, top, right, bottom, fill=color,
                                                   outline="black", width=1, tags="dynamic")
            # small roof
            roof_w = ow * 0.6
            self.canvas.create_rectangle(sx - roof_w/2, top + oh*0.05, sx + roof_w/2, top + oh*0.35,
                                         fill="#ff9f9f", outline="", tags="dynamic")

        # draw player car at bottom (always at near z)
        sx, sy, s = world_to_screen(self.car_x, OBSTACLE_MIN_Z + 0.01)
        cw = CAR_BASE_WIDTH * s
        ch = CAR_BASE_HEIGHT * s
        left = sx - cw/2
        right = sx + cw/2
        top = CAR_Y_POS
        bottom = CAR_Y_POS + ch
        # body
        self.canvas.create_rectangle(left, top, right, bottom, fill="#0fa046", outline="white", width=2, tags="dynamic")
        # windshield
        self.canvas.create_polygon(sx - cw*0.25, top + ch*0.1, sx + cw*0.25, top + ch*0.1,
                                   sx + cw*0.18, top + ch*0.35, sx - cw*0.18, top + ch*0.35,
                                   fill="#bfefff", outline="", tags="dynamic")
        # wheels
        wheel_h = ch*0.18
        self.canvas.create_oval(left+6, bottom-wheel_h, left+18, bottom-4, fill="#111", tags="dynamic")
        self.canvas.create_oval(right-18, bottom-wheel_h, right-6, bottom-4, fill="#111", tags="dynamic")

        # HUD
        self.canvas.create_text(12, 12, anchor="nw", text=f"Score: {self.score}", font=("Helvetica", 14, "bold"),
                                fill="white", tags="dynamic")
        self.canvas.create_text(WIDTH-12, 12, anchor="ne", text=f"Speed: {int(self.car_speed)}",
                                font=("Helvetica", 14, "bold"), fill="white", tags="dynamic")

        # If crashed, overlay message
        if not self.running:
            self.canvas.create_rectangle(60, HEIGHT//2-80, WIDTH-60, HEIGHT//2+80, fill="#000000", stipple="gray25",
                                         outline="white", width=2, tags="dynamic")
            self.canvas.create_text(WIDTH//2, HEIGHT//2-20, text="CRASH!", font=("Helvetica", 36, "bold"),
                                    fill="#ff6666", tags="dynamic")
            self.canvas.create_text(WIDTH//2, HEIGHT//2+20, text=f"Score: {self.score}    Press R to restart",
                                    font=("Helvetica", 14), fill="white", tags="dynamic")

    def loop(self):
        now = time.time()
        dt = now - self.last_time if self.last_time else 1.0 / FPS
        self.last_time = now
        if self.running:
            self.update(dt)
        self.draw_dynamic()
        self.root.after(TICK_MS, self.loop)


if __name__ == "__main__":
    root = tk.Tk()
    game = Fake3DGame(root)
    root.mainloop()
