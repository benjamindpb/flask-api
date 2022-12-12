import requests
import time

file_url = "https://dumps.wikimedia.org/wikidatawiki/entities/latest-truthy.nt.gz"

start1 = time.time()
print("Dump truthy gzip file download...")
r = requests.get(file_url, stream = True)
print("Download complete.")
end1 = time.time()
print(f"Execution time: {end1 - start1} seconds.\n")

start2 = time.time() 
print("Creating gzip file...")
with open("dump/latest-truthy.nt.gz","wb") as dump:
    for chunk in r.iter_content(chunk_size=1024):
        if chunk:
            dump.write(chunk)
end2 = time.time()
print("Gzip file created.")
print(f"Execution time: {end2 - start2} seconds.\n")
