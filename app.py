import os

from bson import ObjectId, datetime
from flask import Flask, request, jsonify, render_template, redirect, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'userKey'

# client = MongoClient('mongodb://yhcyoon:yhc5631@54.180.118.223', 27017)           ## 리눅스서버
client = MongoClient('localhost', 27017)                                            ## 로컬

db = client.illustre  # 'illustre' 라는 이름의 db를 만들거나 사용합니다


@app.route('/webhook', methods=['POST'])
def web_hook():
    web_hook_data = request.form
    print(web_hook_data)
    os.system('cd /home/ubuntu/illustre/myProject && git pull')
    return jsonify({'result': 'success'})


@app.route('/')
def main():
    # 세션에 'sessionID'라는 변수가 있는
    if 'sessionID' in session:
        # 세션에 'sessionID'라는 변수의 값을 가져와서
        session_id = session['sessionID']
        # 'sessionID'에 담긴 값(유저 생성시에 만들어진 _id 값)에 대한
        # 유저 정보가 user DB에 있는지 확인
        user = db.user.find_one({'_id': ObjectId(session_id)})

        # 세션에 'sessionID'라는 변수의 값이 비어있거나
        # 'sessionID'에 담긴 값(유저 생성시에 만들어진 _id 값)에 대한
        # 유저 정보가 없다면
        if session_id is None or user is None:
            # 로그인 페이지를 띄워줌
            return render_template('login.html')
        # 아니라면 로그인 한 세션이 있는 유저이므로 메인 페이지로 보냄
        return render_template('main.html', nickname=user['nickname'])
    return render_template('login.html')


@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['userID']
    password = request.form['password']

    user = db.user.find_one({'user_id': user_id, 'password': password})

    print(user)

    if user is not None:
        # 세션을 생성하는데
        # 세션에 'sessionID'라는 변수에
        # 유저 생성시 만들어진 _id 값을 넣어둠(유저 고유 식별자이기 때문)
        session['sessionID'] = str(user['_id'])
        return redirect('/')
    return render_template('login.html')


@app.route('/signUp', methods=['GET'])
def sign_up_page():
    return render_template('signUp.html')


@app.route('/signUp', methods=['POST'])
def sign_up():
    user_id = request.form['userID']
    password = request.form['password']
    nickname = request.form['nickname']

    db.user.insert_one({'user_id': user_id, 'password': password, 'nickname': nickname})
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('sessionID')
    return jsonify({'result': 'success'})


@app.route('/main', methods=['GET'])
def main_page():
    return render_template('main.html')


@app.route('/images/<category>', methods=['GET'])
def show_Pictures(category):
    # 1. DB에서 리뷰 정보 모두 가져오기
    if category == 'all':
        pictureInfos = list(db.pictureInfos.find({}, {'_id': 0}))
    else:
        pictureInfos = list(db.pictureInfos.find({'category': category}, {'_id': 0}))

    # 2. 성공 여부 & 리뷰 목록 반환하기
    return jsonify({'result': 'success', 'pictureInfos': pictureInfos})


@app.route('/images/<searchCategory>/<searchContent>', methods=['GET'])
def search_Content(searchCategory, searchContent):
    # 1. DB에서 리뷰 정보 모두 가져오기
    if searchCategory == 'searchTitle':
        pictureInfos = list(db.pictureInfos.find({'title': {'$regex':searchContent, '$options': 'i'}}, {'_id': 0}))
    elif searchCategory == 'searchNickname':
        pictureInfos = list(db.pictureInfos.find({'userNickname': {'$regex':searchContent, '$options': 'i'}}, {'_id': 0}))
    elif searchCategory == 'searchComment':
        pictureInfos = list(db.pictureInfos.find({'comment': {'$regex':searchContent, '$options': 'i'}}, {'_id': 0}))
    else:
        pictureInfos = list(db.pictureInfos.find({'$or':[{'title': {'$regex':searchContent, '$options': 'i'}},{'userNickname': {'$regex':searchContent, '$options': 'i'}},{'comment': {'$regex':searchContent, '$options': 'i'}}]}, {'_id': 0}))

    # 2. 성공 여부 & 리뷰 목록 반환하기
    return jsonify({'result': 'success', 'pictureInfos': pictureInfos})


##### pictureRegist.html 호출 / 현재 pictureInfos를 카운트하여 dbNumber값을 함께 반환 #####
@app.route('/pictureregist', methods=['GET'])
def picture_Regist_Page():
    now = datetime.strftime.now('%Y%m%d %H%M%S')
    return render_template('pictureRegist.html', now=now)


@app.route('/pictureregist', methods=['POST'])
def picture_Regist():
    # 클라이언트가 give로 준 값들 가져오기
    imgUrl_receive = request.form['imgURL_give']
    category_receive = request.form['category_give']
    id_receive = request.form['userID_give']
    pw_receive = request.form['userPW_give']
    nickname_receive = request.form['userNickname_give']
    title_receive = request.form['title_give']
    comment_receive = request.form['comment_give']
    likeCount_receive = request.form['likeCount_give']
    datetime_receive = request.form['now_give']

    # DB에 삽입할 pictureInfo 만들기
    pictureInfo = {
        'imgURL': imgUrl_receive,
        'category': category_receive,
        'userID': id_receive,
        'userPW': pw_receive,
        'userNickname': nickname_receive,
        'title': title_receive,
        'comment': comment_receive,
        'likeCount': likeCount_receive,
        'datetime': datetime_receive
    }

    # pictureInfos 에 pictureInfo 저장하기
    db.pictureInfos.insert_one(pictureInfo)
    
    # 성공 여부 & 성공 메시지 반환
    return jsonify({'result': 'success', 'msg': '등록되었습니다!'})


@app.route('/picturedetail/picturecode=<pictureCode>/', methods=['GET'])
def picture_detail_Page(pictureCode):
    picture_detail = list(db.pictureInfos.find({'_id': ObjectId.Parse(pictureCode)}))
    picture_detail_content = {'title': picture_detail[0]['title'],
                              'category': picture_detail[0]['category'],
                              'userNickname': picture_detail[0]['userNickname'],
                              'comment': picture_detail[0]['comment'],
                              'imgURL': picture_detail[0]['imgURL'],
                              'datetime': picture_detail[0]['datetime'],
                              'likeCount': picture_detail[0]['likeCount']}
    return render_template('pictureDetail.html', detailContent=picture_detail_content)


@app.route('/pictureRank')
def picture_Rank():
    return render_template('pictureRank.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)