from flask import Flask, Blueprint, render_template, send_from_directory, jsonify
from flask_bootstrap import Bootstrap
import pandas as pd
import numpy as np
from flask_jsonpify import jsonpify
from models.bitcoin_dashboard.data_analysis.dashboard import getAllData
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
    title = "Some Awesome Page"
    url = 'http://example.org'
    icon = 'fa-star'

@example_site.route('/example/<path:filename>')
def base_static(filename):
    return send_from_directory(example_site.root_path + '/../example_site/static', filename)

@example_site.route('/example/api')
def api():
    """
    Example API route for use as an ajax data source
    :return:
    """
    tblGainLoss, tblDailyGainLoss, coinHistory, tblCoins = getAllData(ndays=2)
    # df = pd.read_csv('/media/mcamp/LocalSSHD/PythonProjects/Datasets/Bike-Sharing-Dataset/hour.csv')
    print(tblGainLoss.columns, tblDailyGainLoss.columns, coinHistory.columns, tblCoins.columns)
    print(dict(data=tblCoins.astype(str).as_matrix().tolist()))
    return jsonify(dict(data=tblCoins.astype(str).as_matrix().tolist()))


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
    html = render_template('blog_home.html',
                           current_user = user,
                           blog_posts = blog_posts,
                           links=links_widget)
    return html


@example_site.route('/example/datatable')
def table():
    '''
    Example of how to use data tables to display a dataframe. Can either accept data pushed via AJAX data source
    or it can be passed data directly from a dataframe converted to a matrix

    NOTE!: seems like DataTables has to have the dataframe converted to strings else it wont format currectly
    :return:
    '''
    # tblGainLoss, tblDailyGainLoss, coinHistory, tblCoins = getAllData(ndays=2)
    # data = tblCoins.as_matrix()
    data =[]
    # df = pd.read_csv('/media/mcamp/LocalSSHD/PythonProjects/Datasets/Bike-Sharing-Dataset/hour.csv')
    cols = ['date', 'name', 'timestamp', 'label', 'price_btc', 'price_cny',
            'price_eur', 'price_gbp', 'price_rur', 'price_usd', 'volume_24h',
            'PriceDelta']
    table = dict(title='Example DataTable', columns=cols, rows=data)

    html = render_template('example_datatable.html',
                           table=table,
                           datapath='/example/api',
                           active_page='examples')
    return html

@example_site.route('/example/test.json')
def send_bc2():
    # df = pd.read_csv('/home/mcamp/PythonProjects/BitCoinDashboard/test.csv')
    tblGainLoss, tblDailyGainLoss, coinHistory, tblCoins = getAllData(ndays=7)
    N = 1024
    ix = np.arange(N)
    y = np.sin(2 * np.pi * ix / float(N / 3)) * 20 + 30
    x = range(0,N)
    return jsonpify(np.array([x, y]).T.tolist())

@example_site.route('/example/flot_lineplot')
def plot_flot():
    html = render_template('flot_line_plot.html',
                           path_to_data='/example/test.json',
                           active_page='examples')
    return html

@example_site.route('/example/sidebar')
def under_construction2():
    path = 'examples'
    link = Links()
    links = [link for x in range(5)]
    html = render_template('example_sidebar_page.html',
                           active_page=path,
                           sidelinks=links)
    return html

@example_site.route('/example/socket')
def docket_test():
    path = 'examples'
    link = Links()
    links = [link for x in range(5)]
    html = render_template('socket_io_example.html')
    return html