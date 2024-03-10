# Start Driving



Ensure to place car on the track so that it is ready to drive.

Now you can start your car again and pass it your model to drive.

```bash
python manage.py drive --model ~/mycar/models/mypilot.h5
```

However, you will see better performance if you start with the tflite mode.

```bash
python manage.py drive --model ~/mycar/models/mypilot.tflite --type tflite_linear --myconfig myconfig.py
```

Make sure to have the correct config for the data that the model was trained on etc

Load the UI and select Autopilot from the drop down