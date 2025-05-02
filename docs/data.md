## Data processing 

To convert the excel to json 
```
$ cd data/
$ docker build -t cws_data_pipeline .
$ docker run -it -v `pwd`:/app/input -v `pwd`:/app/output cws_data_pipeline --sanctuaries_path /app/input/updated_sanctuaries_with_species_and_ngos.xlsx --output_path /app/output/output_file.json
```


