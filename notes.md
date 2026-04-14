# Notes

## Tick Loop

Here is the math behind tick loops. Each tick is a time step in the RL sense of the term. There are two things we need to fix -

* The number of ticks we want the world to advance in 1 second. This is usually set by the Frames Per Second (FPS) number. This can also be thought of as the frequency. Lets call this $\nu$ ticks per second.
* The total number of seconds we want the world to last. Think of this as the episode length. Lets call this $L$ seconds.

With this we can now calculate the total number of time steps aka ticks in our trajectory $\tau = L \nu$. We need the tick loop to loop $\tau$ many times.

Each loop needs to last $1/\nu$ seconds. In reality, the runtime of the loop is usually a lot less than that, so the CPU thread will need to sleep for some seconds in each loop. For simple loops I can make the simplifying assumption that the loop takes 0 seconds and just have the thread sleep for $1/\nu$ seconds. For more complex loops, I can calculate the precise time it takes the loop to run, say $\delta t$ and then sleep for $1/\nu - \delta t$ seconds.

```python
# Simple Loop
tot_ticks = fps * episode_duration
tick_duration = 1/fps
for t in range(tot_ticks):
  # advance the world by one time step
  time.sleep(tick_duration)
```

```python
# Accurate Loop
tot_ticks = fps * episode_len
tick_duration = 1/fps
for t in range(tot_ticks):
  start_tick = time.perf_counter()
  # advance the world by one time step
  end_tick = time.perf_counter()
  delta = end_tick - start_tick
  sleep_secs = tick_duration - delta
  time.sleep(sleep_secs)
```

## Processors

Based on my current understanding there are three types of processors -

* Data processors that are returned by `lerobot.processor.make_default_processors()`.
* Model processors that are returned by `lerobot.policies.factory.make_pre_post_processors()`.
* Environment processors which I have not explored yet.

This set of components have to be the single most over-engineered piece of code in the library! It is probably needed for a super generic library like lerobot that has to work with multiple robots, different data formats, etc. but for my use case where I am mostly messing around with a single robot type, it is pretty confusing to use. So far I'll  have to keep using the model processors as they do the standardization and un-standardization of data but once I have a solid test bed to verify my changes, I'll probably end up using conceptually simpler alternatives from Lightning or Keras or even home-grown.

## Training

The `//lerobot/scripts/lerobot_train.py` is pretty complicated as well, but not over-engineered. Once I start implementing my own models, I should write my own training script and gradually build towards the complexity that is present in `lerobot_train.py`. For now I should keep using this script as-is without any simplifications.

## Calibration

Calibration entry for the various motors looks like this:

```json
"shoulder_pan": {
    "id": 1,
    "drive_mode": 0,
    "homing_offset": -1792,
    "range_min": 862,
    "range_max": 3211
},
```

The `homing_offset` is used to shift the motor's coordinate system so that a known physical position, e.g., the mid point of the motor, or the closed position for the gripper maps to a predictable raw value. This is baked into the motor driver code so that the motor's actual physical position is the current reading plus the offset, `Present_Position = Actual_Position - Homing_Offset` as mentioned in `//lerobot/motors/feetech/feetech.py` line 285. As a client of the driver code, I don't have to worry about applying the homing offset. The driver code, e.g., in `feetech.py` does this for me.

Conceptually, I think of the servo motor position in terms or rotating a positive or a negative angle in degrees, but what goes to the motor is an integer. All the STS3215 servo motors have a "resolution" of 12 bits $[0, 4095]$, so the maximum resolution is 4096, i.e., 4096 steps of the motor will complete one complete $360 \degree$ turn. Conversely, it means that they can rotate in increments of $\frac{360}{4096} \degree$, but not lower. The `range_min` and `range_max` are the min and max values of the integers that can go to the driver. The lerobot SDK `//lerobot/motors/motor_bus.py` does the conversion of the user supplied value in degrees, to the integer that the driver expects. Here is how the conversion works:
$$
mid = \frac{1}{2}(max + min) \\
raw = deg \times \frac{4095}{360} + mid \\
deg = (raw - mid) \times \frac{360}{4095}
$$
As the range max and min values indicate, the joint will not have full range of motion from $-360 \degree$ to $360 \degree$. The min and max values in degrees can be calculated as:
$$
h = \frac{1}{2} (range\_max - range\_min) \\
deg\_min = -h \times \frac{360}{4095} \\
deg\_max = h \times \frac{360}{4095}
$$
The gripper calibration works a bit differently. Here is what it looks like:

```json
"gripper": {
    "id": 6,
    "drive_mode": 0,
    "homing_offset": 1184,
    "range_min": 2019,
    "range_max": 3486
}
```

The gripper position values I need to think about are between 0 which is closed, to 100 which is completely open. The code in `motor_bus.py` does the conversion:
$$
n = \frac{raw - min}{max - min} \times 100 \\
raw = \frac{n (max - min)}{100} + min
$$
The "user mode" apis like `robot.get_observation()` or `robot.send_action()` always deal in normalized (or as I am calling them "conceptual") values, e.g., I'll specify the shoulder pan joint's value in degrees, the lerobot SDK and feetech driver code will do all the necessary conversions to the actual integral value that goes to the motor. This means that the datasets that I record will also have these normalized values.

### Model Training

Typically, in ML I z-scale my input dataset where for each column $\mathbf x_z = \frac{\mathbf x - \mu}{\sigma}$. The model training code in lerobot has model pre- and post-processors that have a "normalization" step where they do this. This is good for a generic model, but a more robuts approach will be to use the calibration data to rescale my input to be between some small range like $[-1, 1]$. So going into training, I can calculate the absolute minimum and maximum values the shoulder pan joint can have based on the calibration data. From there I can apply a simple rescaler like so -
$$
x = 2 \frac{deg - deg\_min}{deg\_max - deg\_min} - 1
$$
Where `deg_min` and `deg_max` are functions of `range_min` and `range_max` that I can get from the calibration. I don't have to compute the statistics for the entire dataset before I can apply this rescaler.
