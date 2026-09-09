# compile_website.py
# 
# Basically what it says on the tin.
# This script compiles the database content into a proper website structure and format.
# 404.html is a special case file, since it is the only one that exists on the root level of the website.
# All other webpages are intended to live in the "web" subfolder.
#
# In the "src" directory, there exists a template.html file that acts as the common styling and structure for every other page on the website.
# All other html files should only contain the web content that will be filled into the template.html.
# The key word in the template file that will be replaced with the file contents is "{WEB_PAGE_CONTENT}".
#
# Before execution, this script will compute a hash of the "src" directory to detect if any changes have been made since the last time the website was compiled.
# If no changes are detected, the script will terminate.
# If changes are detected, the script will execute, and the hash value will be writen to the file "database.hash" ONLY AFTER THE COMPILATION COMPLETES WITHOUT ERROR!
#
# This script will otherwise maintain the folder structure contained in the "src/databases" subfolder when compiling to "web".
# This script will also output a warning if a subdirectory does not contain any html files to compile, suggesting that section could be refactored or is incomplete.
#
# TODO: Add a feature to audit weblinks to make sure there are no broken links anywhere
#
#
# Additions:
# - Added section to configure the "/scripts/config.js" file by filling in the database path and database hash



# Directory hashing code that should be invariant to OS and file order
# Source - https://stackoverflow.com/a/54477583
# Posted by danmou, modified by community. See post 'Timeline' for change history
# Retrieved 2026-09-06, License - CC BY-SA 4.0

import hashlib
from _hashlib import HASH as Hash
from pathlib import Path
from typing import Union

def md5_update_from_file(filename: Union[str, Path], hash: Hash) -> Hash:
    assert Path(filename).is_file()
    with open(str(filename), "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash

def md5_file(filename: Union[str, Path]) -> str:
    return str(md5_update_from_file(filename, hashlib.md5()).hexdigest())

def md5_update_from_dir(directory: Union[str, Path], hash: Hash) -> Hash:
    assert Path(directory).is_dir()
    for path in sorted(Path(directory).iterdir(), key=lambda p: str(p).lower()):
        hash.update(path.name.encode())
        if path.is_file():
            hash = md5_update_from_file(path, hash)
        elif path.is_dir():
            hash = md5_update_from_dir(path, hash)
    return hash

def md5_dir(directory: Union[str, Path]) -> str:
    return str(md5_update_from_dir(directory, hashlib.md5()).hexdigest())



# Back to my code
import os
import sys
import shutil

def print_log(log_file_handle, msg):
    print(msg)
    log_file_handle.write(msg + "\n")
#END_DEF

def compile_directory(log_file_handle, template_data, src_dir, dst_dir, warn_empty = True):
    assert os.path.isdir(src_dir)
    assert os.path.isdir(dst_dir)
    
    # Compile HTML files
    count = 0
    for src_file in Path(src_dir).glob("*.html"):
        print_log(log_file_handle, str(src_file))
        dst_file = os.path.join(dst_dir, os.path.basename(src_file))
        
        with open(dst_file, "w") as src_file_handle:
            with open(src_file, "r") as dst_file_handle:
                src_file_handle.write(template_data.format(WEB_PAGE_CONTENT=dst_file_handle.read()))
        
        count = count + 1
    
    if count == 0 and warn_empty:
        print_log(log_file_handle, "WARNING: '{0}' contains no HTML files".format(os.path.normpath(src_dir)))
    
    # Compile subdirectories
    for path in Path(src_dir).glob("*/"):
        print_log(log_file_handle, str(path))
        os.mkdir(os.path.normpath(os.path.join(dst_dir, os.path.basename(path))))
        compile_directory(log_file_handle, template_data, os.path.normpath(os.path.join(src_dir, os.path.basename(path))), os.path.normpath(os.path.join(dst_dir, os.path.basename(path))))
#END_DEF

def clear_directory(directory):
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if os.path.isfile(path) or os.path.islink(path):
            os.unlink(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
#END_DEF

pwd = os.path.dirname(os.path.abspath(sys.argv[0]))
source_path = os.path.join(pwd, "src")
database_path = os.path.join(pwd, "src/databases")
website_path = os.path.join(pwd, "web")

error_file = os.path.join(pwd, "404.html")
hash_file = os.path.join(pwd, "database.hash")
config_file = os.path.join(pwd, "scripts/config.js")
template_file = os.path.join(source_path, "template.html")
error_contents_file = os.path.join(source_path, "404_contents.html")

log_file = os.path.join(pwd, "log.txt")
log_file_handle = open(log_file, "w")

# Confirm that all of the required directories and files are present
try:
    assert os.path.isdir(source_path)
    assert os.path.isdir(database_path)
    assert os.path.isdir(website_path)
    assert os.path.isfile(template_file)
    assert os.path.isfile(error_contents_file)
except:
    print_log(log_file_handle, "ERROR: One or more of the following required file/directories were not found:")
    print_log(log_file_handle, os.path.normpath(source_path))
    print_log(log_file_handle, os.path.normpath(database_path))
    print_log(log_file_handle, os.path.normpath(website_path))
    print_log(log_file_handle, os.path.normpath(template_file))
    print_log(log_file_handle, os.path.normpath(error_contents_file))
    sys.exit(1)
#END_TRY




# Read stored hash value and compare to the current database hash
file_hash_value = "No Existing Hash"
if os.path.isfile(hash_file):
    with open(hash_file, "r") as file:
        file_hash_value = file.read()
#END_IF

database_hash_value = md5_dir(source_path)
print_log(log_file_handle, "database.hash:\t{0}".format(file_hash_value))
print_log(log_file_handle, "Folder Hash:\t{0}".format(database_hash_value))

if file_hash_value == database_hash_value:
    print_log(log_file_handle, "Hash values are identical. No compilation needed.")
    log_file_handle.close()
    sys.exit(0)
#END_IF



# Hash values are different, proceed with compilation
print_log(log_file_handle, "Hash values are not identical. Proceeding with compilation...")
print_log(log_file_handle, "")

template_data = ""
with open(template_file, "r") as file:
    template_data = file.read()

try:
    clear_directory(website_path)
except Exception as e:
    print_log(log_file_handle, "ERROR: Failed to clear website directory.\nError({0}): {1}".format(e.errno, e.strerror))
    log_file_handle.close()
    sys.exit(1)
#END_TRY

# Create 404 Page
try:
    print_log(log_file_handle, os.path.normpath(error_file))
    with open(error_file, "w") as error_file_handle:
        with open(error_contents_file, "r") as error_contents_handle:
            error_file_handle.write(template_data.format(WEB_PAGE_CONTENT=error_contents_handle.read()))
except IOError as e:
    print_log(log_file_handle, "I/O error({0}): {1}".format(e.errno, e.strerror))
    log_file_handle.close()
    sys.exit(1)
#END_TRY


# Loop through all subdirectories and HTML files in databases directory and compile them
try:
    compile_directory(log_file_handle, template_data, database_path, website_path, False)
except IOError as e:
    print_log(log_file_handle, "I/O error({0}): {1}".format(e.errno, e.strerror))
    log_file_handle.close()
    sys.exit(1)
except Exception as e:
    print_log(log_file_handle, "ERROR: Failed to compile website data.\nError({0}): {1}".format(e.errno, e.strerror))
    log_file_handle.close()
    sys.exit(1)
#END_TRY



# Build the config.js file
config_contents = "class Config {{\n\tconstructor(config={{}}){{\n\t\tthis.databasePath = \"{DATABASE_DIRECTORY}\";\n\t\tthis.hash = \"{DATABASE_HASH_VALUE}\";\n\t\tthis.cache = {CACHE};\n\t}}\n}}\n\nexport {{ Config }}"
with open(config_file, "w") as file:
    print_log(log_file_handle, "Building config.js...")
    file.write(config_contents.format(DATABASE_DIRECTORY = "/src/databases/", DATABASE_HASH_VALUE = database_hash_value, CACHE = "true"))


# Last step, write database hash value to file
with open(hash_file, "w") as file:
    print_log(log_file_handle, "Storing database hash value...")
    file.write(database_hash_value)

print_log(log_file_handle, "Compilation completed successfully!")
log_file_handle.close()
sys.exit(0)