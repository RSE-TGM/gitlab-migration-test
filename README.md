# Modbus-tcp

Python 3.8 program for data acquisition from electric meters and/or devices supporting the modbus protocol over the TCP/IP channel. 
This program reads modbus data and saves them to a postgres or influx database. In debug mode the program is not connecting to any database and only logs the modbus data to standard output.

Reading modbus data from the following devices is already implemented:
1. Janitza UMG512-4201-2529
2. Frer QUBO 96


## Run this code
todo: add infos standalone and docker


## Contributing
Feel free to add any other modbus device, please follow these steps:
1. Open a new branch with the name of the device that you want to add, eg. 'abb-meter' and upload the technical sheets in the /docs folder 
2. Create a new python file in the ./src/models directory with the device name, and write the code required
3. Update the modbus_devices dictionary in the ./src/models/__init__.py file to be able to use it in the main code
4. Update the example.env file and this readme to make sure that everyone knows what was added and ho to use it
5. Merge the open branch into the master and close the branch

## License
For open source projects, say how it is licensed.
