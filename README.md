# Flask API for [Wikidata Atlas](https://wdatlas.dcc.uchile.cl/) project

## Requirements

The Python version must be greater than or equal to **3.9**.

To install the additional requirements of the API, the following command must be executed in the terminal, located in the main folder of the API.
```console
pip install -r requirements.txt
```


## API execution

Once all the API requirements have been installed, it is possible to run it. 

To do this, you must execute the following command in the terminal:
```console
python app.py
```
With this, the default API will be hosted in **localhost:5000** (http://127.0.0.1:5000)

## Uses (API calls)
The API has the following endpoints to obtain information from the Wikidata database:

- Getting instances of a georeferential type
```console
localhost:5000/data/<search>/<limit>
```
Where **search** corresponds to the label of the type and **limit** to the number of instances to get.

- Returns a dictionary with all georeferenceable types found after preprocessing the dump.
```console
localhost:5000/types
```
- Returns the information corresponding to a type, given its ID.
```console
localhost:5000/type/<id>
```
Where **id** corresponds to the unique identifier of the entity ([entity ID](https://www.wikidata.org/wiki/Wikidata:Identifiers))

- This endpoint is related to type search autocompletion. It is based on the percentage of georeferenceable instances of a given type to get all types whose label starts with the lookup that is entered as input.
```console
localhost:5000/autocomplete/<search>
```
Where **search** corresponds to a string that symbolizes the desired search.

---

[![Alt text](https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Wikidata_Stamp_Rec_Dark.svg/200px-Wikidata_Stamp_Rec_Dark.svg.png "Powered by Wikidata")](https://www.wikidata.org/wiki/Wikidata:Main_Page)
