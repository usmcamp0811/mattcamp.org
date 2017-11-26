from flask import Flask, Blueprint, render_template, send_from_directory, jsonify
from flask_bootstrap import Bootstrap
import pandas as pd


main_site = Blueprint('main_site',
                      __name__,
                      template_folder='templates',
                      static_folder='static',
                      static_url_path='')

class User(object):
    #TODO: Implement
    name = 'Matt Camp'
    email = 'usmcamp0811@gmail.com'

class BlogPost(object):
    #TODO: Implement
    post_title = "Hello Blog Post!"
    post_summary = 'This is a place holdering summary of a blog post... Stuff goes here... '
    post_image = '/img/4-14_Marines_in_Fallujah.jpg'
    post_link = '#'
    post_date = 'Novemeber 10, 1775'
    post_by = 'Matt Camp'
    post_by_url = '#'
    post = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Reiciendis aliquid atque, nulla? Quos cum ex quis soluta, a laboriosam. Dicta expedita corporis animi vero voluptate voluptatibus possimus, veniam magni quis!'

class Links(object):
    # TODO: Implement
    text = "Some Awesome Page"
    url = 'http://example.org'

@main_site.route('/main/<path:filename>')
def base_static(filename):
    return send_from_directory(main_site.root_path + '/../main_site/static', filename)

@main_site.route('/api')
def api():
    df = pd.read_csv('/media/mcamp/LocalSSHD/PythonProjects/Datasets/Bike-Sharing-Dataset/hour.csv')
    return jsonify(dict(data=df.as_matrix().tolist()))


@main_site.route('/')
def index():

    user = User()
    blog_posts = []
    for i in range(5):
        blog_posts.append(BlogPost())

    temp_link_list = [Links() for i in range(2)]
    links_widget = dict(title='Links Widget',
                        links_col1=temp_link_list,
                        links_col2=temp_link_list)

    html = render_template('index.html',
                           current_user = user,
                           blog_posts = blog_posts,
                           links=links_widget,
                           active_page='home')
    return html

@main_site.route('/about')
def about():

    html = render_template('about.html',
                           active_page='about')
    return html

@main_site.route('/nav')
def navbar():

    user = User()
    blog_posts = []
    for i in range(5):
        blog_posts.append(BlogPost())

    html = render_template('base.html',
                           current_user = user,
                           blog_posts = blog_posts)
    return html

@main_site.route('/datatable')
def table():

    df = pd.read_csv('/media/mcamp/LocalSSHD/PythonProjects/Datasets/Bike-Sharing-Dataset/hour.csv')
    cols = df.columns
    table = dict(title='Example DataTable', columns=cols, rows=[])

    html = render_template('example_datatable.html',
                           table=table,
                           datapath='/api')
    return html