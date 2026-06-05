def contentUpdater(file_path, key, value):
  with open("file.txt","r") as f:
    lines= f.readlines()
  with open("file.txt","w") as o:
    for line in lines:
      if key in line:
        f.write(key+" = "+value)

contentUpdater(path,key,value)
