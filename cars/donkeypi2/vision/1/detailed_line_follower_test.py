import numpy as np
from simple_pid import PID
from detailed_line_follower import LineFollower


class TestConfig:
    OVERLAY_IMAGE = True
    SCAN_Y = 100
    SCAN_HEIGHT = 20
    COLOR_THRESHOLD_LOW = (20, 100, 100)
    COLOR_THRESHOLD_HIGH = (30, 255, 255)
    TARGET_PIXEL = None
    TARGET_THRESHOLD = 20
    CONFIDENCE_THRESHOLD = 0.5
    THROTTLE_INITIAL = 0.5
    THROTTLE_STEP = 0.1
    THROTTLE_MAX = 1.0
    THROTTLE_MIN = 0.0


def test_initialization():
    pid = PID(1, 0.1, 0.05, setpoint=0)
    cfg = TestConfig()
    line_follower = LineFollower(pid, cfg)

    assert line_follower.overlay_image == cfg.OVERLAY_IMAGE
    assert line_follower.scan_y == cfg.SCAN_Y
    assert line_follower.scan_height == cfg.SCAN_HEIGHT
    assert np.array_equal(
        line_follower.color_thr_low, np.asarray(cfg.COLOR_THRESHOLD_LOW)
    )
    assert np.array_equal(
        line_follower.color_thr_hi, np.asarray(cfg.COLOR_THRESHOLD_HIGH)
    )
    assert line_follower.target_pixel == cfg.TARGET_PIXEL
    assert line_follower.target_threshold == cfg.TARGET_THRESHOLD
    assert line_follower.confidence_threshold == cfg.CONFIDENCE_THRESHOLD
    assert line_follower.steering == 0.0
    assert line_follower.throttle == cfg.THROTTLE_INITIAL
    assert line_follower.delta_th == cfg.THROTTLE_STEP
    assert line_follower.throttle_max == cfg.THROTTLE_MAX
    assert line_follower.throttle_min == cfg.THROTTLE_MIN
    assert line_follower.pid_st == pid


def test_get_i_color():
    pid = PID(1, 0.1, 0.05, setpoint=0)
    cfg = TestConfig()
    line_follower = LineFollower(pid, cfg)

    # Define variables for image dimensions and color values
    img_height = 200
    img_width = 400
    num_color_channels = 3
    yellow_line_start_x = 200
    yellow_line_end_x = 220
    yellow_hue = 30
    yellow_saturation = 255
    yellow_value = 255

    yellow_line_hsv = (
        yellow_hue,
        yellow_saturation,
        yellow_value,
    )

    # Create a test image with a yellow line
    img = np.zeros((img_height, img_width, num_color_channels), dtype=np.uint8)
    img[cfg.SCAN_Y : cfg.SCAN_Y + cfg.SCAN_HEIGHT, yellow_line_start_x:yellow_line_end_x] = yellow_line_hsv

    max_yellow, confidence, mask = line_follower.get_i_color(img)
    total_sum = int(np.sum(mask))

    assert 200 <= max_yellow < 220  # Expected max yellow index within the range
    assert confidence > 0  # Expected non-zero confidence
    assert total_sum > 0  # Expected non-empty mask


def test_run():
    pid = PID(1, 0.1, 0.05, setpoint=0)
    cfg = TestConfig()
    line_follower = LineFollower(pid, cfg)

    # Create a test image with a yellow line
    img = np.zeros((200, 400, 3), dtype=np.uint8)
    img[cfg.SCAN_Y : cfg.SCAN_Y + cfg.SCAN_HEIGHT, 200:220] = (
        30,
        255,
        255,
    )  # Yellow line

    steering, throttle, output_img = line_follower.run(img)

    assert steering != 0  # Expected non-zero steering
    assert throttle >= cfg.THROTTLE_MIN and throttle <= cfg.THROTTLE_MAX
    assert output_img is not None


def test_overlay_display():
    pid = PID(1, 0.1, 0.05, setpoint=0)
    cfg = TestConfig()
    line_follower = LineFollower(pid, cfg)

    # Create a test image and mask
    img = np.zeros((200, 400, 3), dtype=np.uint8)
    mask = np.zeros((cfg.SCAN_HEIGHT, 400), dtype=np.uint8)
    mask[:, 200:220] = 255

    output_img = line_follower.overlay_display(img, mask, 210, 0.8, 200)

    assert output_img is not None
    assert output_img.shape == img.shape
