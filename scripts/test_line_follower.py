import argparse
import importlib
from typing import Dict
import cv2
from simple_pid import PID


class Config:
    IMAGE_W = 320
    IMAGE_H = 240
    CV_CONTROLLER_MODULE = "donkeycar.parts.line_follower"
    CV_CONTROLLER_FILE = None
    CV_CONTROLLER_CLASS = "LineFollower"
    OVERLAY_IMAGE = True
    SCAN_Y = 120
    SCAN_HEIGHT = 20
    COLOR_THRESHOLD_LOW = (20, 100, 100)
    COLOR_THRESHOLD_HIGH = (30, 255, 255)
    TARGET_PIXEL = 320//2
    TARGET_THRESHOLD = 10
    CONFIDENCE_THRESHOLD = 0.5
    THROTTLE_INITIAL = 0.0
    THROTTLE_STEP = 0.1
    THROTTLE_MAX = 1.0
    THROTTLE_MIN = -1.0


def import_class_from_file(file_path, class_name):
    spec = importlib.util.spec_from_file_location("module.name", file_path)  # type: ignore
    module = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)
    return getattr(module, class_name)


def load_config_from_file(file_path) -> Config:
    config = Config()
    with open(file_path, 'r') as file:
        exec(file.read(), globals(), config.__dict__)
    return config


def main(cfg):
    # Dynamically import the CV controller module and class
    if cfg.CV_CONTROLLER_FILE is not None:
        # Dynamically import the CV controller class from the specified file
        cv_controller_class = import_class_from_file(cfg.CV_CONTROLLER_FILE, cfg.CV_CONTROLLER_CLASS)
    elif cfg.CV_CONTROLLER_MODULE is not None:
        module = importlib.import_module(cfg.CV_CONTROLLER_MODULE)
        cv_controller_class = getattr(module, cfg.CV_CONTROLLER_CLASS)
    else:
        raise ValueError("Either CV_CONTROLLER_FILE or CV_CONTROLLER_MODULE must be specified")
    
    assert cv_controller_class is not None, f"CV controller class {cfg.CV_CONTROLLER_CLASS} not found"

    # Initialize PID controller
    pid = PID(Kp=0.1, Ki=0.01, Kd=0.005, setpoint=0)

    # Initialize CV controller
    cv_controller = cv_controller_class(pid, cfg)

    # Initialize video capture from the default camera (index 0)
    cap = cv2.VideoCapture(0)

    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        if not ret:
            break

        # Resize the frame to the specified dimensions
        frame_resized = cv2.resize(frame, (cfg.IMAGE_W, cfg.IMAGE_H))

        # Convert the frame from BGR to RGB color space
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

        # Run the CV controller on the frame
        steering, throttle, frame_overlay = cv_controller.run(frame_rgb)

        # Display the frame with overlay
        if frame_overlay is not None:
            frame_overlay = cv2.cvtColor(frame_overlay, cv2.COLOR_RGB2BGR)
            cv2.imshow("CV Controller", frame_overlay)
        else:
            cv2.imshow("CV Controller", frame_resized)

        # Print the steering and throttle values
        print(f"Image size: {frame_resized.shape[1]}x{frame_resized.shape[0]}, Steering: {steering:.2f}, Throttle: {throttle:.2f}")

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and close windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CV Controller Test')
    parser.add_argument('--file', type=str, default=Config.CV_CONTROLLER_FILE,
                        help='CV controller file path')
    parser.add_argument('--follower_class', type=str, default=Config.CV_CONTROLLER_CLASS,
                        help='CV controller class name')
    parser.add_argument('--config', type=str, help='Configuration file path')

    args = parser.parse_args()

    cfg = load_config_from_file(args.config) if args.config is not None else Config()

    # Override the CV controller file and class if specified in the command line arguments
    if args.file is not None:
        cfg.CV_CONTROLLER_FILE = args.file
    if args.follower_class is not None:
        cfg.CV_CONTROLLER_CLASS = args.follower_class

    main(cfg)
