# What to do where

Because the the donkey car projects must exist on the car and on the host, there are two places to do things.  This document is a guide to what to do where.

## On the car

### Drive the car
The car is the only place to drive the car.  The car is the only place to collect data.  The car is the only place to test the car.

So you will always invoke the command `python manage.py drive` on the car.

## On the host

### Train the autopilot

Because the training is a computationally intensive process, it is best to do this on the host.  However, the training data must be collected on the car.  So the process is to collect the data on the car, and then transfer the data to the host for training.

There is a guide [here](http://docs.donkeycar.com/guide/deep_learning/train_autopilot/#training-with-the-command-line) on how to do this.



