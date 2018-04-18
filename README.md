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

Now we iterate over the files, read theis raw content in binary format and inset them in a table.

```python
#--- Open database and loop over files to insert in database
con = sqlite3.connect(filename_db)
cur = con.cursor()
for i, file_i in enumerate(files):
 
    #--- Read image as a binary blob
    with open(file_i, 'rb') as f:
        image_bytes = f.read()
    f.close()
 
    #--- Decode raw bytes to get image size
    nparr  = np.fromstring(image_bytes, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    image_size = img_np.shape[1]
 
    #--- Extract file name without extension
    filename = os.path.relpath(file_i, PATH)
    objid = int(os.path.splitext(filename)[0])
 
    #--- Insert image and data into table
    cur.execute("insert into Images VALUES(?,?,?)", (objid,sqlite3.Binary(image_bytes),image_size)   )
    con.commit()
 
    #--- Cheap progress
    if ((i % 100) == 0):
        print(i, n_files)
 
cur.close()
con.close()
```

Note the code that reads the image as a binary blob:

```python
with open(file_i, 'rb') as f:
   image_bytes = f.read()
   f.close()
```

I wanted to store the image size so I had to “decode” the blob. This step is not neccesary if you just want to store the images as in a file system. The first line converts the string into a byte (uint8 or unsigned char) numpy array. The second line does the magic of decoding the raw bytes into an image. It actually decompresses the jpg data:

```python
nparr = np.fromstring(image_bytes, np.uint8)
img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
```

Some websites show how to passe the blob using a buffer. I am instead passing the image blob using a SQLite function, I don’t know which way is better. I suppose using sqlite3 own functions leads to more maintainable code (or not…).


```python
sqlite3.Binary(image_bytes)
```
Finally we read some images from the database.

```python
con = sqlite3.connect(filename_db)
cur = con.cursor()
row = cur.execute("SELECT ObjId, img from Images")
for ObjId, item in row:
 
    #--- Decode blob
    nparr  = np.fromstring(item, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
 
    #--- Display image
    cv2.imshow('image',img_np)
    k = cv2.waitKey(0)
    if k == 27:         # wait for ESC key to exit
        cv2.destroyAllWindows()
        break
 
cur.close()
con.close()
```

