import requests
import time
import os

start = time.time()
print("GZip dump truthy file download.\n")

filepath = 'dump/latest-truthy.nt.gz'
dump_url = 'https://dumps.wikimedia.org/wikidatawiki/entities/latest-truthy.nt.gz'

if os.path.exists(filepath):
	os.remove(filepath)
	print("Successfully! The previous dump file has been removed.\n")

r = requests.get(dump_url, stream = True)

print("Creating GZip dump file...")
with open(filepath,"wb") as dump:
    for chunk in r.iter_content(chunk_size=8192):
        # if chunk:
        dump.write(chunk)
end = time.time()
print(f"Gzip file created in {end - start} seconds.\n")
