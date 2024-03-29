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

## Transfer data from the car to the host

The data is collected on the car, and then transferred to the host for training.  

You can do this through the Donkey UI, or you can do it manually via the command line.

### Using the Donkey UI

The Donkey UI has a feature to transfer data from the car to the host.  You can find this feature in the "Car Connector" tab of the UI.

## Using the command line

If you prefer to transfer the data manually via the command line, you can use the `rsync` command.

In a new terminal session on your host PC use rsync to copy your cars
folder from the Raspberry Pi.

```bash
rsync -rv --progress --partial pi@<your_pi_ip_address>:~/mycar/data/  ~/mycar/data/
```

This command does the following:

- rsync: The command to start the synchronization process.
- -rv: This combines two options:
- -r: Recursive. This option tells rsync to copy directories recursively, meaning it will copy all directories and their contents.
    
- -v: Verbose. This option makes rsync provide detailed information about what it's doing.
- --progress: This option displays detailed progress of the transfer, showing the percentage of data transferred, transfer speeds, and estimated time of completion. It's useful for monitoring the status of the transfer.
- --partial: This option allows rsync to keep partially transferred files if the transfer is interrupted. This can be useful for resuming large file transfers without starting from scratch.
- pi@<your_pi_ip_address>:~/mycar/data/: The source path. This specifies the user (pi) and IP address of the remote Raspberry Pi (<your_pi_ip_address>). 
-  ~/mycar/data/ is the directory on the Raspberry Pi you want to synchronize from. The ~ symbol represents the home directory of the user pi.
-  ~/mycar/data/: The destination path. This is the local directory where you want to synchronize the files to. Similar to the source path, ~ represents the home directory of the current user on the local system.