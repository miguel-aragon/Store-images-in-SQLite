#
#  Store images in a database as binary compressed blobs
#
#  Written by Miguel A. Aragon-Calvo, 2018
#
#
#



import os
import glob
import numpy as np
import sqlite3
import cv2
 
PATH_IMAGES = 'Images/'
 
#--- Extract files from folder following pattern
files   = glob.glob(PATH_IMAGES+"*.jpg")
n_files = len(files)
print('Number of files in folder: ', n_files)
 
#--- Simple database creator
def create_db(filename):
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS Images")
    cursor.execute("CREATE TABLE Images(ObjId INT, img BLOB, size INT)")
    db.commit()
    db.close()
 
filename_db = 'testdb_0.db'
create_db(filename_db)
 
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


#--- Read back images
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
