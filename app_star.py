import os
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv
import datetime

app_star = Flask(__name__)
load_dotenv()

key = os.getenv('API_KEY_NASA') # API key stored in .env
index_html = 'star_index.html'
story_html = 'star_story.html'
endpoint_apod = 'https://api.nasa.gov/planetary/apod'

# define a function that query an api and return info in JSON format
def query_api(endpoint, payload):
    response = requests.get(endpoint, params=payload)
    return response.json()

# extract info from the html form and create a date string
def extract_date():
    day = request.form['day']
    month = request.form['month']
    year = request.form['year']
    return '{}-{}-{}'.format(year,month,day)


# -------- Home page -------- #
@app_star.route('/')
def index():
    # request root url of the page - for home button
    root_url = request.url_root
    return render_template(index_html, root_url = root_url)


# -------- Response page -------- #
@app_star.route('/response', methods=['POST', 'GET'])
def response():
    if request.method == 'POST':
        # compile user input into a date string
        user_date = extract_date()
        # compile payload based on user input
        payload_apod = {
            'date': user_date,
            'hd': True,
            'api_key': key
        }
        # request api
        response = query_api(endpoint_apod, payload_apod)
        # retrieve info from api response
        date = response['date']
        explanation = response['explanation']
        title = response['title']
        url = response['url']
        hdurl = response['hdurl']
        # request root url of the page - for home button
        root_url = request.url_root
        if 'copyright' in response.keys(): 
            # for the cases when 'copyright' info is given
            copy_right = response['copyright']
            result = render_template(
                story_html,
                root_url = root_url,
                pic_title = title,
                date = date,
                description = explanation,
                picture=url,
                hdlink = hdurl,
                cpr = copy_right)
        else:
            # sometimes there is no 'copyright' info
            result = render_template(
                story_html,
                root_url = root_url,
                pic_title = title,
                date = date,
                description = explanation,
                picture=url,
                hdlink = hdurl)
        return result
    else:
        render_template(index_html)


# -------- Today page -------- #
# - Use the same template as the Response page
# - Queries automatically sent using the current date
@app_star.route('/today')
def today():
    # retrieve the current date
    now = datetime.datetime.now()
    if now.hour > 12: # only update the date after 12pm
        today_date = '{}-{}-{}'.format(now.year,now.month,now.day)
    else: # otherwise use the story from the previous day
        today_date = '{}-{}-{}'.format(now.year,now.month,now.day - 1)
    payload_apod = {
        'date': today_date,
        'hd': True,
        'api_key': key
    }
    # request api
    response = query_api(endpoint_apod, payload_apod)
    # retrieve info from api response
    date = response['date']
    explanation = response['explanation']
    title = response['title']
    url = response['url']
    hdurl = response['hdurl']
    # request root url of the page - for home button
    root_url = request.url_root
    if 'copyright' in response.keys():
        copy_right = response['copyright']
        result = render_template(
            story_html,
            root_url = root_url,
            pic_title = title,
            date = date,
            description = explanation,
            picture=url,
            hdlink = hdurl,
            cpr = copy_right)
    else:
        result = render_template(
            story_html,
            root_url = root_url,
            pic_title = title,
            date = date,
            description = explanation,
            picture=url,
            hdlink = hdurl)
    return result


if __name__ == '__main__':
#     app_star.run('0.0.0.0', port=3000,debug=True)

    if 'PORT' in os.environ:
        app_star.run(host='0.0.0.0', port=int(os.environ['PORT']))
    else:
        app_star.run(debug=True)