geo3.db: data/Finland_addresses_2020-11-13.csv data/municipalities.csv create_database.py
	rm -f "$@"
	python3 create_database.py "$@"

data/Finland_addresses_2020-11-13.csv: data/finland_addresses_2020-11-13_json.7z
	7z x "$<" data/Finland_addresses_2020-11-13.csv -so | iconv -f ISO-8859-15 -t UTF-8 > "$@"
	touch "$@"

data/finland_addresses_2020-11-13_json.7z:
	curl -fL -o "$@" https://www.avoindata.fi/data/dataset/941b70c8-3bd4-4b4e-a8fb-0ae29d2647a1/resource/18e2b019-e986-4cf5-abfe-e6771f6e04d8/download/finland_addresses_2020-11-13_json.7z

data/municipalities.csv: data/municipalities.json
	echo "code,name" > $@
	jq -r '.[]|[.code,.classificationItemNames[0].name]|@csv' $< >> $@

data/municipalities.json:
	curl -fL -o "$@" "https://data.stat.fi/api/classifications/v2/classifications/kunta_1_20200101/classificationItems?content=data&format=json&lang=fi&meta=max"
