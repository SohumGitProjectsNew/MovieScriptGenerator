import requests
from bs4 import BeautifulSoup
import json

movies = []

site_url = "https://imsdb.com"

genres = ["Action",	"Adventure", "Animation", "Comedy", "Crime", "Drama", "Family", "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Short", "Thriller", "War", "Western"]
alphas = ["#", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]


def get_page_links(url, limit):
    
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")

    links = []

    count = limit

    for p in soup.find_all('p'):
        a_tag = p.find('a')
        if a_tag and 'href' in a_tag.attrs:
            if limit==None:
                links.append((a_tag.text.strip(), a_tag['href']))
            else:
                if count>0:
                    links.append((a_tag.text.strip(), a_tag['href']))
                    count=count-1

    return(links)


def page_of_letters(letter, limit):
    
    url_page = site_url + "/alphabetical/" + letter

    return(get_page_links(url_page, limit))


def page_of_genre(genre, limit):
    
    url_page = site_url + "/genre/" + genre

    return(get_page_links(url_page, limit))


def get_script_url(url_movie):

    url_page = site_url + url_movie

    page = requests.get(url_page)

    soup = BeautifulSoup(page.content, "html.parser")

    try:
        script_link = soup.find('p', align="center").find('a')

        script_link = script_link['href']
 
        return(script_link)

    except:
        print("could not get script URL from: " + str(url_page))
        return None


def get_script_text(scipt_link):
    
    url_page = site_url + scipt_link

    page = requests.get(url_page)

    soup = BeautifulSoup(page.content, "html.parser")

    try:
        script = ''.join(str(content) for content in soup.find("pre").contents)
        return(script)

    except:
        print("could not get movie from: " + str(url_page))
        return(None)


def convert_to_jason():

    return json.dumps(movies, indent=4)


def save_to_file(file_path, json_data):

    with open(file_path, "w", encoding="utf-8") as file:

        file.write(json_data)


def wrapper(save_file_path, genre, limit):

    print("Saving to:" + str(save_file_path),"\nSorting by genre: " + str(genre) + "\nLimit = " + str(limit))

    list_of_tups = []

    if genre==True:
        for gen in genres:
            print("getting urls from " + str(gen))
            list_of_tups.extend(page_of_genre(gen,limit))
    else:
        for alpha in alphas:
            print("getting urls from " + str(alpha))
            list_of_tups.extend(page_of_letters(alpha,limit))
    
    for title, url in list_of_tups:
        script_final_url = get_script_url(url)
        print(script_final_url)
        if script_final_url != None:
            script_text = get_script_text(script_final_url)
            if script_text != None:
                movies.append({"title": title, "script": script_text})

    json_data = convert_to_jason()
    save_to_file(save_file_path,json_data) 

wrapper("first_three_genre.txt", True, 3)
#wrapper("movie_scripts.txt", False, None)
