## Storing compressed images in SQLite with python

I am working on a project that requires working with a large number of images of galaxies. While a million files is something easily handled by the linux file system it can be problematic to manage. For instance,  in order to transfer the full image catalog (~ 2GB) it has to be packed into a zip or tar file, which takes a long time (but much less than a direct transfer of individual files). Also,  in the case of distributed file systems like those used in Big Data applications a very large set of small (a few Kb) files is a worst case scenario.

One solution that so far works well is storing the images in an SQLite database. I found lots of information on the web about this problem but all where partial solutions. So as a reminder to myself, and hoping that this may be useful to other people, this is my end-to-end solution.

SQLite  lets us store all the images in one single database file (this as far as I know is not the case for other databases) and even in RAM. while allowing us fast operations on the individual images.  According to  this paper data stored in blobs can be accessed %30 faster than a file system (although the study is old).

The key idea here is to store the compressed (encoded) images as raw binary blobs in the database and then decode them as needed. This saves both disk space and reading time.

Below is a code that takes all the jpg files in a folder and stores them in a SQLite database (the actual code I use reads from another database to extract file names and properties of the galaxies).

```python
import os
import glob
import numpy as np
import sqlite3
import cv2
 
PATH = '/home/miguel/Science/DATA/SDSS/IMAGES/SQLite/Images/'
```
Get the list of files in the folder

```python
#--- Extract files from folder following pattern
files   = glob.glob(PATH+"*.jpg")
n_files = len(files)
print('Number of files in folder: ', n_files)
```
Create a table in a database with three columns:

ObjId: The unique Id of the galaxy, also used as filename.
img: The raw bytes of the image, this has to be decompressed.
size: The size of the image in pixels (my images are squared).

```python
#--- Simple database creator
def create_db(filename):
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS Images")
    cursor.execute("CREATE TABLE Images(ObjId INT, img BLOB, size INT)")
    db.commit()
    db.close()
 
filename_db = 'DR7_IMAGES.db'
create_db(filename_db)
```



