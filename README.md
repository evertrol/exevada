# The Extreme Event Attribution Database

The Extreme Event Attribution Database, Exevada, is designed to store properties of extreme meteorological events (heatwaves, heavy rainfall, etc.) and the corresponding attribution analyses thereof. These analyses aim to determine to what extent climate change increases the likelihood and severety of such events, and make extensive use of observation time series and climate model output. The database allows the storage of the results (intensity change, probability ratio) of these analyses, attach references to scientific publications and describe the societal impact of the extreme events (e.g. forest fires, floodings).


This repository contains also web frontent code to visualize the database in a browser. It shows events on a world map, allows users to search corresponding attribution studies and publications and look up the fitted distributions of climate models that have been analyzed in attribution studies. The frontend can be configured to use 'Copernicus C3S styling', as explained in the installation guide.


## Technology used

The backend uses
- [postgresql](https://www.postgresql.org) database containing the catalogue of events and analyses,
- [postgis](https://postgis.net) to extend the database with geospatial information (event location, measurement stations, etc.),
- [Django](https://www.djangoproject.com) the framework to serve the database over the web.

The frontend uses following technologies:
- [bootstrap](https://getbootstrap.com/docs/4.5/getting-started/introduction/) for the various HTML elements and layout of the frontend,
- [datatables](https://datatables.net) for tabular data representation,
- [leaflet](https://leafletjs.com) for geographical data representation (maps of events or measurement stations)



## Installation

Installation is detailed in the INSTALL.md file.


## License and copyright

This project copyright 2020, Netherlands eScience Center, and is
licensed under the Apache License 2.0.

See the NOTICE and LICENSE files.
