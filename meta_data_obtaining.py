import requests
import ijson
import json

APIKEY = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIxOTc4Yjc5YzU1NmQxYzM2ZDhlNGU0MTNlZjMwZWVkNSIsIm5iZiI6MTc0MDYwMzc5Ny4yNzksInN1YiI6IjY3YmY4MTk1YjZjN2UzNDI1Y2EyMzZlMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.pbAeQMwK5EDV1h21mJ6u_C1_jhVcAKTljG5MrEUMVco"

def search_movie(title):

    url = f"https://api.themoviedb.org/3/search/movie?query={title}&include_adult=true&language=en-US&page=1"
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {APIKEY}"
    }
    
    response = requests.get(url, headers=headers)
    
    return response.json()["results"][0]

def ids_to_eng(ids):

    gen_to_id_map = {"Action":28,"Adventure":12,"Animation":16,"Comedy":35,"Crime":80,"Documentary":99,"Drama":18,"Family":10751,"Fantasy":14,"History":36,"Horror":27,"Music":10402,"Mystery":9648,"Romance":10749,"Science Fiction":878,"TV Movie":10770,"Thriller":53,"War":10752,"Western":37}

    id_to_gen_map =  {_id: gen for gen, _id in gen_to_id_map.items()}

    return [id_to_gen_map.get(x) for x in ids]


def get_year(date):
    return date[:4]


def get_meta_data_json(input_file):
    with open(input_file, "r", encoding="utf-8") as _in, open((input_file.replace(".txt", "_meta.txt")), "w", encoding="utf-8") as _out: 
        _out.write("[\n") 
        count = 0 
        jobj = ijson.items(_in, "item")
        for obj in jobj:
            if count != 0:
                _out.write(",\n") 

            title = obj["title"]

            data = search_movie(title)
            
            new_obj = {
                "_id": count,
                "api_id": data["id"],
                "title": title,  
                "genres": ids_to_eng(data["genre_ids"]),
                "overview": data["overview"],
                "release_date": get_year(data["release_date"]),
                "script": None
            }

            count = count +1

            _out.write(json.dumps(new_obj, ensure_ascii=False))

        _out.write("\n]")

#print(search_movie("12 Monkeys"))
get_meta_data_json("first_three_genre.txt")