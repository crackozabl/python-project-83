from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def get():
    return render_template('index.html')
