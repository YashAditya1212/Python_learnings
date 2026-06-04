import os
#we need to enter the path to folder
# Changed to split by commas, and strip() removes extra spaces
raw_input = input("Enter the full folder paths separated by COMMAS: ")
folders = [folder.strip() for folder in raw_input.split(",")]       

for folder in folders:
    try:
        files = os.listdir(folder)
        print("\n--- Files in the folder '" + folder + "' are: ---")
        
        for file in files:
            print(file)
            
    except FileNotFoundError:
        print("\nError: The directory '" + folder + "' does not exist.")
        continue
    except PermissionError:
        print("\nError: Permission denied for directory '" + folder + "'.")
        continue
    except NotADirectoryError:
        print("\nError: '" + folder + "' is a file, not a directory.")
        continue
