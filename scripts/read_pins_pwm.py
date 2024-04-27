import RPi.GPIO as GPIO
import time
import argparse


def read_pwm_duty_cycle_and_frequency(pin):
    GPIO.setup(pin, GPIO.IN)

    try:
        while True:
            # Measure the duration of the PWM pulse
            pulse_start = time.time()
            while GPIO.input(pin) == GPIO.HIGH:
                pass
            pulse_end = time.time()
            pulse_duration = pulse_end - pulse_start

            # Measure the duration of the PWM cycle
            cycle_start = time.time()
            while GPIO.input(pin) == GPIO.LOW:
                pass
            cycle_end = time.time()
            cycle_duration = cycle_end - cycle_start

            # Calculate the PWM duty cycle and frequency
            duty_cycle = (pulse_duration / (pulse_duration + cycle_duration)) * 100
            frequency_hz = 1 / (pulse_duration + cycle_duration)

            print(f"Pin {pin} PWM Duty Cycle: {duty_cycle:.2f}% Frequency {frequency_hz:.0f} Hz")

            time.sleep(0.5)  # Delay between readings (adjust as needed)

    except KeyboardInterrupt:
        print("Script interrupted by user.")

    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read PWM duty cycle and frequency from a GPIO pin.")
    parser.add_argument(
        "--pin",
        type=int,
        default=37,
        help="GPIO pin number (using physical pin numbering, default: 37). Pins 37 and 38 can be used"
    )
    args = parser.parse_args()

    GPIO.setmode(GPIO.BOARD)  # Using physical pin numbering
    read_pwm_duty_cycle_and_frequency(args.pin)