from flask import Flask, Blueprint, render_template, send_from_directory, jsonify
from flask_bootstrap import Bootstrap
import pandas as pd


example_site = Blueprint('example_site',
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

@example_site.route('/example/<path:filename>')
def base_static(filename):
    return send_from_directory(example_site.root_path + '/../example_site/static', filename)

@example_site.route('/example/api')
def api():
    """
    Example API route for use as an ajax data source
    :return:
    """
    df = pd.read_csv('/media/mcamp/LocalSSHD/PythonProjects/Datasets/Bike-Sharing-Dataset/hour.csv')
    return jsonify(dict(data=df.as_matrix().tolist()))


@example_site.route('/example/blog_home')
def index():
    """
    Example blog home page
    :return:
    """
    user = User()
    blog_posts = []
    for i in range(5):
        blog_posts.append(BlogPost())

    temp_link_list = [Links() for i in range(2)]
    links_widget = dict(title='Example Link Widget',
                        links_col1=temp_link_list,
                        links_col2=temp_link_list)
    print(links_widget)
    html = render_template('index.html',
                           current_user = user,
                           blog_posts = blog_posts,
                           links=links_widget)
    return html


@example_site.route('/example/datatable')
def table():
    '''
    Example of how to use data tables to display a dataframe. Can either accept data pushed via AJAX data source
    or it can be passed data directly from a dataframe converted to a matrix
    :return:
    '''
    df = pd.read_csv('/media/mcamp/LocalSSHD/PythonProjects/Datasets/Bike-Sharing-Dataset/hour.csv')
    cols = df.columns
    table = dict(title='Example DataTable', columns=cols, rows=[])

    html = render_template('example_datatable.html',
                           table=table,
                           datapath='/api')
    return html