# icesat_glah_extract
GUI application for extracting your data from GLAH files

It was my first GUI app which was created for handling ICESat mission hdf data more efficiently. It is for Python 2.7 and depends on h5py library.

Find sample ICESat mission data on NASA website to see how it works.
http://icesat.gsfc.nasa.gov/icesat/hdf5_products/data/index.php 

For me, the main problem with ICESat data is their huge volume (for GLAH14 is usually more than 1.5 million measurement for each parameter) and the fact that they often contains quite a long part of orbit track. While working on specific area (eg. one country) you often need just small part of it.

To solve those problem I created simple GUI app. You just need to choose your file(s) (or directory), pick parameters you like and specify area in boundrybox (in degrees, WGS84). Application will extract your data from your fiel(s) and put inside simple txt file. What is more, it automatically creates separate txt file for each laser campaign. Thanks to that, you do not need to check and sort files manually, processing is faster and timestamp analysis is easier. 

Output data is customized for geographical information system (GIS) software like QGIS vs ArcGIS. Each row correspond to one measurement and columns are picked parameters.
