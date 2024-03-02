# Auto Pilots for Donkey Car

## Introduction
This document outlines the primary methods for autopiloting a Donkey car. Autopiloting techniques enable the car to navigate tracks autonomously using various algorithms and data inputs.

## Autopilot Methods

### 1. Behavioral Cloning
Behavioral Cloning involves a human driver collecting data by manually driving the car. This data, which includes images, steering, and throttle inputs, is used to train a neural network to mimic human driving behavior.

**Pros**:
- Directly learns from human expertise.
- Can adapt to complex track layouts.

**Cons**:
- Requires substantial data collection.
- Performance is limited by the quality and variety of the training data.

**Examples**: A project where the car learns to navigate a track with sharp turns and varying lighting conditions by training on diverse driving data collected under similar conditions.

### 2. Computer Vision
This method employs traditional computer vision techniques, such as color space conversion and edge detection, to interpret the track. The car uses these interpretations to stay on course.

**Pros**:
- Less reliant on extensive data collection.
- Can be effective in well-defined environments.

**Cons**:
- Struggles with complex environments and varying lighting conditions.
- Requires fine-tuning of vision algorithms for different tracks.

**Examples**: Implementing an algorithm that detects track edges using color contrast and guides the car along the center line.

### 3. Path Following
Path Following involves generating a predefined path based on XYZ coordinates collected from a human-driven lap. The car autonomously follows this path using algorithms.

**Pros**:
- Precise control over the car's path.
- Consistent performance across laps.

**Cons**:
- Requires initial manual lap to generate the path.
- Less adaptive to dynamic changes in the track environment.

**Examples**: Using GPS or other positioning systems to create a detailed path map and programming the car to follow this path with minimal deviation.

## Additional Resources

- **[Donkey Car Autopilots](http://docs.donkeycar.com/guide/train_autopilot/)**: Official guide to training your Donkey car's autopilot.

## Conclusion

Choosing the right autopilot method depends on your specific needs, the complexity of the track, and the available resources. By understanding the strengths and limitations of each method, you can better tailor the Donkey car's autopilot to achieve optimal performance.