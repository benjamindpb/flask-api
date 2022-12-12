WDQS_ENDPOINT = 'https://query.wikidata.org/sparql'
WD_API_ENNPOINT = 'https://www.wikidata.org/w/api.php'
USER_AGENT = "wd-atlas/0.1 (benjamin.delpino@ug.uchile.cl; benjamin.dpb@gmail.com) [python-requests/2.28.1 python-flask/2.2.2]"
WD_QUERY = '''
  SELECT DISTINCT 
  ?item ?label ?description ?thumb ?image ?lat ?lon ?countryCode WHERE {{
    # Get all instances and subclasses of one item 
    ?item wdt:P31/wdt:P279* wd:{} .
    # Get label from the item
    ?item rdfs:label ?label .
    FILTER (LANG(?label)="en")
    # Get coordinate location
    ?item wdt:P625 ?coord .
    ?item p:P625 [ psv:P625[ wikibase:geoGlobe ?globe ; ] ] .
    FILTER ( ?globe = wd:Q2 )
    # Get item description
    OPTIONAL {{?item schema:description ?description .
            FILTER (LANG(?description)="en")}}
    # Get item image 
    OPTIONAL {{?item wdt:P18 ?image .}}   
    # Get the item country name and the country code
    OPTIONAL {{?item wdt:P17 ?country .
            ?country wdt:P297 ?code . }}
    BIND(LCASE(?code) as ?countryCode)
    
    # Get coordinates
    BIND(geof:longitude(?coord) AS ?lon)
    BIND(geof:latitude(?coord)  AS ?lat)
    
    # Generate thumbnail image
    BIND(REPLACE(wikibase:decodeUri(STR(?image)), "http://commons.wikimedia.org/wiki/Special:FilePath/", "") as ?fileName) .
    BIND(REPLACE(?fileName, " ", "_") as ?safeFileName)
    BIND(MD5(?safeFileName) as ?fileNameMD5) .
    BIND(CONCAT("https://upload.wikimedia.org/wikipedia/commons/thumb/", 
                SUBSTR(?fileNameMD5, 1, 1), "/", 
                SUBSTR(?fileNameMD5, 1, 2), "/", ?safeFileName, "/350px-", ?safeFileName) as ?thumb)
  }} limit {}
  '''