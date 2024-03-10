# Copying to and from the Donkey Car

## Copy files from the Donkey Car to your host PC

In a new terminal session on your host PC use rsync to copy your cars folder from the Raspberry Pi.

rsync -rv --progress --partial pi@<your_pi_ip_address>:~/mycar/data/  ~/mycar/data/


## Copy model back to car

In previous step we managed to get a model trained on the data. Now is time to move the model back to Raspberry Pi, so we can use it for testing it if it will drive itself.

Use rsync again to move your trained model pilot back to your car.

rsync -rv --progress --partial ~/mycar/models/ pi@<your_ip_address>:~/mycar/models/
