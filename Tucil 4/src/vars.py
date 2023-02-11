from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('hello.html', list_of_names=['chris','asu','ben'])


@app.route('/<int:name>')
def greet(name):
    return f"Hello {name}"

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)