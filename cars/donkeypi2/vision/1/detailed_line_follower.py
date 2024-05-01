import cv2
import numpy as np
from simple_pid import PID
import logging

logger = logging.getLogger(__name__)


class LineFollower:
    """
    OpenCV based controller
    This controller takes a horizontal slice of the image at a set Y coordinate.
    Then it converts to HSV and does a color thresh hold to find the yellow pixels.
    It does a histogram to find the pixel of maximum yellow. Then is uses that iPxel
    to guid a PID controller which seeks to maintain the max yellow at the same point
    in the image.
    """

    def __init__(self, pid, cfg):
        self.overlay_image = cfg.OVERLAY_IMAGE
        self.scan_y = cfg.SCAN_Y  # num pixels from the top to start horiz scan
        self.scan_height = cfg.SCAN_HEIGHT  # num pixels high to grab from horiz scan
        self.color_thr_low = np.asarray(cfg.COLOR_THRESHOLD_LOW)  # hsv dark yellow
        self.color_thr_hi = np.asarray(cfg.COLOR_THRESHOLD_HIGH)  # hsv light yellow
        self.target_pixel = (
            cfg.TARGET_PIXEL
        )  # of the N slots above, which is the ideal relationship target
        self.target_threshold = (
            cfg.TARGET_THRESHOLD
        )  # minimum distance from target_pixel before a steering change is made.
        self.confidence_threshold = (
            cfg.CONFIDENCE_THRESHOLD
        )  # percentage of yellow pixels that must be in target_pixel slice
        self.steering = 0.0  # from -1 to 1
        self.throttle = cfg.THROTTLE_INITIAL  # from -1 to 1
        self.delta_th = cfg.THROTTLE_STEP  # how much to change throttle when off
        self.throttle_max = cfg.THROTTLE_MAX
        self.throttle_min = cfg.THROTTLE_MIN

        self.pid_st = pid

    def get_i_color(self, cam_img: np.ndarray):
        """
        get the horizontal index of the color at the given slice of the image
        input: cam_image, an RGB numpy array
        output: index of max color, value of cumulative color at that index, and mask of pixels in range
        """
        # take a horizontal slice of the image
        iSlice = self.scan_y
        scan_line = cam_img[iSlice: iSlice + self.scan_height, :, :]

        # convert to HSV color space
        img_hsv = cv2.cvtColor(scan_line, cv2.COLOR_RGB2HSV)

        # make a mask of the colors in our range we are looking for
        mask = cv2.inRange(img_hsv, self.color_thr_low, self.color_thr_hi)

        # which index of the range has the highest amount of yellow?
        hist = np.sum(mask, axis=0)
        max_yellow = np.argmax(hist)

        return max_yellow, hist[max_yellow], mask

    def run(self, cam_img: np.ndarray):
        """
        main runloop of the CV controller
        input: cam_image, an RGB numpy array
        output: steering, throttle, and the image.
        If overlay_image is True, then the output image
        includes and overlay that shows how the
        algorithm is working; otherwise the image
        is just passed-through untouched.
        """
        if cam_img is None:
            return 0, 0, False, None

        max_yellow, confidence, mask = self.get_i_color(cam_img)

        if self.target_pixel is None:
            # Use the first run of get_i_color to set our relationship with the yellow line.
            # You could optionally init the target_pixel with the desired value.
            self.target_pixel = max_yellow
            logger.info(f"Automatically chosen line position = {self.target_pixel}")

        assert self.target_pixel is not None, "No target pixel set."
        assert isinstance(self.target_pixel, int), "Target pixel must be an integer."

        if self.pid_st.setpoint != self.target_pixel:
            # this is the target of our steering PID controller
            self.pid_st.setpoint = self.target_pixel

        if confidence >= self.confidence_threshold:
            # invoke the controller with the current yellow line position
            # get the new steering value as it chases the ideal
            self.steering = self.pid_st(max_yellow)

            # slow down linearly when away from ideal, and speed up when close
            if abs(max_yellow - self.target_pixel) > self.target_threshold:
                # we will be turning, so slow down
                if self.throttle > self.throttle_min:
                    self.throttle -= self.delta_th
                if self.throttle < self.throttle_min:
                    self.throttle = self.throttle_min
            else:
                # we are going straight, so speed up
                if self.throttle < self.throttle_max:
                    self.throttle += self.delta_th
                if self.throttle > self.throttle_max:
                    self.throttle = self.throttle_max
        else:
            logger.info(
                f"No line detected: confidence {confidence} < {self.confidence_threshold}"
            )

        # show some diagnostics
        if self.overlay_image:
            cam_img = self.overlay_display(
                cam_img, mask, max_yellow, confidence, self.target_pixel
            )

        return self.steering, self.throttle, cam_img

    def draw_target_pixel(
        self,
        img: np.ndarray,
        target_pixel: int,
        scan_y: int,
        color: tuple = (0, 255, 255),
        size: int = 5,
        thickness: int = 2
    ) -> None:
        """
        Draw a marker or circle at the target pixel location on the image.
        """
        cv2.drawMarker(
            img,
            (target_pixel, scan_y),
            color,
            cv2.MARKER_CROSS,
            markerSize=size,
            thickness=thickness
        )
    
    def overlay_display(
        self,
        cam_img: np.ndarray,
        mask: np.ndarray,
        max_yellow: np.intp,
        confidence: float,
        target_pixel: int,
    ) -> np.ndarray:
        """
        Composite mask on top the original image.
        show some values we are using for control
        """

        # Expand the dimensions of the mask to match the image shape
        mask_exp = np.stack((mask,) * 3, axis=-1)

        # Define the region of interest (ROI) where the line is being detected
        iSlice = self.scan_y

        # Make a copy of the original image to avoid modifying it directly
        img = np.copy(cam_img)

        # Overlay the mask on the ROI of the image
        img[iSlice: iSlice + self.scan_height, :, :] = mask_exp
        
        # Draw a marker or circle at the target pixel location
        self.draw_target_pixel(
            img, target_pixel, iSlice
        )
    
        # Prepare the display strings with relevant information
        display_str = []
        display_str.append("STEERING:{:.1f}".format(self.steering))
        display_str.append("THROTTLE:{:.2f}".format(self.throttle))
        display_str.append("I YELLOW:{:d}".format(max_yellow))
        display_str.append("CONF:{:.2f}".format(confidence))
        display_str.append(
            "TARGET PIXEL: {:d}".format(target_pixel)
        )

        # Set the initial position for displaying the text
        y = 10
        x = 10

        # Iterate over each display string and render it on the image
        for s in display_str:
            cv2.putText(
                img,
                s,
                color=(0, 0, 0),
                org=(x, y),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.4,
            )
            y += 10

        return img
