import pandas as pd
from sqlalchemy.orm import sessionmaker
from model import Food
from __init__ import engine

Session=sessionmaker(bind=engine)
session=Session()

# retrieve data from kaggle and add to database
data = pd.read_csv("/Users/joeychiu/Downloads/recipes_data.csv")
# the total length of data is 2231142, would take a while to upload the data to dataset. Adjust the range if needed
for x in range(len(data)):
    food = Food(data.iloc[x, 0],data.iloc[x, 5],data.iloc[x, 2])
    session.add(food)
session.commit()


from app.__init__ import app
from flask import render_template, request, url_for
from bs4 import BeautifulSoup
import requests
from werkzeug.utils import redirect


@app.route('/welcome', methods=["POST", "GET"])
def welcome():
    if request.method == "POST":
        location = request.form['location']
        return redirect(url_for('restaurant', location=location, page="0"))
    else:
        ingredients=","
        return render_template('welcome.html', ingredients=ingredients)

# web scrape data from yelp.com
@app.route('/restaurant/<location>/<page>')
def restaurant(location, page):
    location = location.replace(" ", "+")
    if page=="0":
        page=""
    url = "https://www.yelp.com/search?find_desc=&find_loc=" + location + "&start="+page+"0"
    r = requests.get(url)
    s = BeautifulSoup(r.content, "html.parser")
    result = s.find(class_="undefined list__09f24__ynIEd")
    restaurants = result.find_all(class_="container__09f24__mpR8_ hoverable__09f24__wQ_on css-1qn0b6x")
    names=[]
    links=[]
    rates=[]
    for i in range(len(restaurants)):
        name = restaurants[i].find(class_="css-1egxyvc").get_text()
        names.append(name)
        pic = restaurants[i].find(class_="child__09f24__Z2_cG css-1qn0b6x")
        href = pic.find('a')
        link = "https://www.yelp.com" + href['href']
        links.append(link)
        if restaurants[i].find(class_="css-gutk1c"):
            rate = restaurants[i].find(class_="css-gutk1c").get_text()
        else:
            rate='None'
        rates.append(rate)
    page = s.find(class_="css-1aq64zd").get_text()
    index = page.index("of")
    max_page = page[index + 3:]
    max_page=int(max_page)
    length=len(names)
    return render_template('restaurant.html', location=location, max_page=max_page, names=names, links=links, rates=rates, length=length)

@app.route("/ingredient/<ingredients>", methods=["POST", "GET"])
def ingredient(ingredients):
    if request.method=="POST":
        ingredient=request.form['ingredient']
        if ingredient == "":
            return redirect(url_for("food", ingredients=ingredients))
        else:
            ingredients = ingredients + ingredient + ","
            return redirect(url_for("ingredient", ingredients=ingredients))
    else:
        list = ingredients.split(",")
        list.pop(0)
        list.pop(len(list)-1)
        return render_template('ingredient.html', ingredients=list, copy=ingredients)

@app.route("/delete_selection/<ingredients>/<ingredient>", methods=['POST'])
def delete(ingredients, ingredient):
    ingredients=ingredients.replace(","+ingredient, "")
    return redirect(url_for("ingredient", ingredients=ingredients))

@app.route("/food/<ingredients>")
def food(ingredients):
    success = []
    results = session.query(Food).all()
    for result in results:
        str_ingredient=str(result.ingredient)
        list = str_ingredient.split("\"")
        list = list[1::2]
        contained = 0
        for element in list:
            if ingredients.find(element) != -1:
                contained += 1
            if contained == len(list):
                success.append(result.name)
    return render_template('food.html', success=success)

@app.route("/get_recipe/<name>")
def get_recipe(name):
    result=session.query(Food).filter_by(name=name).first()
    return render_template('get_recipe.html', recipe=result.direction)
