from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('classifications.html')

@app.route('/about')
def about():
  return render_template('about.html')

#@app.route('/classifications')
#def classifications():
#  return render_template('classifications.html')

if __name__ == '__main__':
  app.run(port=33507)
