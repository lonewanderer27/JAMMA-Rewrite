from flask import Flask, redirect, request, url_for, render_template
from firebase import firebase
import re
from badwords import badwords
import sys

# config
# server will reload on source changes, and provide a debugger for errors
DEBUG = True
TEMPLATES_AUTO_RELOAD = True 

app = Flask(__name__)
app.config.from_object(__name__) # consume the configuration above
commentFailed = None

firebase = \
    firebase.FirebaseApplication('https://jamma-comments-default-rtdb.asia-southeast1.firebasedatabase.app/', None)

@app.route('/')
def index():
  result = firebase.get('/messages', None)
  return render_template('index.html',  messages=result)

# decorator which tells flask what url triggers this fn
@app.route('/messages')
def messages():
  result = firebase.get('/messages', None)
  return render_template('index.html', messages=result, commentFailed=commentFailed)

@app.route('/submit_message', methods=['POST'])
def submit_message():
  messege = request.form['message']
  esername = request.form['username']
  if not messege or not esername:
    commentFailed = 'True'
    result = firebase.get('/messages', None)
    return render_template('index.html', messages=result, commentFailed=commentFailed)
    
  else:
    commentFailed = None
    registerComment = request.form['message']
    commentFiltered = ""
    userCommentAsList = re.sub("[^\w](!@34%^&*.,)", " ", registerComment).split()
    for word in userCommentAsList:
                  numOFasterisk = len(word) 
                  asterisks = ""
                  tempword = word.lower()
                  if tempword in badwords:
                      asterisks = (numOFasterisk * '*')
                      commentFiltered += str(f"{asterisks} ")
                  else:
                      commentFiltered += str(f"{word} ")
    print(commentFiltered)
    message = {
        'body': commentFiltered,
        'userName': request.form['username'],
        'userEmail': request.form['email'],
        'userTel': request.form['tel'],
      }
    firebase.post('/messages', message)
    return redirect(url_for('messages'))

if __name__ == "__main__":
  app.run()