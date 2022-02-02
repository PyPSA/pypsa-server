
# PyPSA-server: web interface for running PyPSA-Eur-Sec scenarios

PyPSA-server allows you to run live online custom optimisations for a sector-coupled model of the European energy system, [PyPSA-Eur-Sec](https://github.com/PyPSA/pypsa-eur-sec). You can, for example, explore different scenarios to reach net-zero carbon dioxide emissions across electricity, heating, transport and industry.

You can find a live version at:

<https://model.energy/scenarios/>


## Software requirements for installation

PyPSA-server has only been tested on the Ubuntu distribution of GNU/Linux.

Ubuntu packages:

`sudo apt install redis-server zip`

To install, we recommend using [miniconda](https://docs.conda.io/en/latest/miniconda.html) in combination with [mamba](https://github.com/QuantStack/mamba).

	conda install -c conda-forge mamba
	mamba env create -f environment.yaml

For (optional) server deployment:

	sudo apt install nginx
	mamba install gunicorn

## Data requirements for installation

Download and unpack the required data bundle (around 90 MB), derived from [PyPSA-Eur-Sec](https://github.com/PyPSA/pypsa-eur-sec).

	wget https://model.energy/scenarios/static/pypsa-server-data-bundle-210801.zip
	unzip pypsa-server-data-bundle-210801.zip

## Run server locally on your own computer

To run locally you need to start the Python Flask server in one terminal, and redis in another:

Start the Flask server in one terminal with:

`python server.py`

This will serve to local address:

http://127.0.0.1:5002/

In the second terminal start Redis:

`rq worker pypsa`

where `pypsa` is the name of the queue. No jobs will be solved until
this is run. You can run multiple workers to process jobs in parallel.


## Deploy on a publicly-accessible server

Use nginx, gunicorn for the Python server, rq, and manage with supervisor.


## License

Copyright 2021-2 Tom Brown <https://nworbmot.org/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation; either [version 3 of the
License](LICENSE.txt), or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the [GNU
Affero General Public License](LICENSE.txt) for more details.
