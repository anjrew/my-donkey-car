# Using computer vision techniques

1. Firstly create a new project with the computer vision template. This will create a new project with the necessary dependencies and files to get started with computer vision.
```bash
donkey createcar --template=cv_control --path=~/mycar
```
2. Choose a color threshold for the line detection. This is the color that the car will follow. The default is yellow.
   
The color threshold values represent the range of colors used to detect the line; they should be chosen to include the colors in the line in the area that it passes through the detection bar and ideally they should not include any other colors. 

The Donkeycar package includes a script to make this easy to do. the hsv_picker.sh script allows you to view the live camera image or alternatively to choose a static image to view. 

You can run the hsv_picker.sh script to view a screen shot image; with the donkey python environment activated run the script from the root of your donkeycar repo folder;

```bash
python scripts/hsv_picker.py --file=<path-to-image>
```
To view the camera stream, again with donkey python environment activated, run the script from the root of your donkeycar repo folder;

```bash
python scripts/hsv_picker.sh
```

It is a good idea to get an image directly from the car in the racing environment to ensure that the lighting conditions are the same as when the car is running or get a static image from the track taken from the recorded video.

## Other Resources

- [Official Docs](https://docs.donkeycar.com/guide/computer_vision/computer_vision/)