import os
from bson import ObjectId
from flask import Flask, request, jsonify, render_template, redirect, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'userKey'

client = MongoClient('mongodb://yhcyoon:yhc5631@54.180.118.223', 27017)           ### 리눅스서버
#client = MongoClient('localhost', 27017)                                            ## 로컬

db = client.illustre  # 'illustre' 라는 이름의 db를 만들거나 사용합니다


@app.route('/webhook', methods=['POST'])
def web_hook():
    web_hook_data = request.form
    print(web_hook_data)
    os.system('cd /home/ubuntu/illustre/myProject && git pull')
    return jsonify({'result': 'success'})


@app.route('/')
def Hello():
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
def Login_Page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def Login():
    userID = request.form['userID']
    password = request.form['password']

    user = db.user.find_one({'userID': userID, 'password': password})

    if user is not None:
        # 세션을 생성하는데
        # 세션에 'sessionID'라는 변수에
        # 유저 생성시 만들어진 _id 값을 넣어둠(유저 고유 식별자이기 때문)
        session['sessionID'] = str(user['_id'])
        return redirect('/')
    return render_template('login.html')


@app.route('/signup', methods=['GET'])
def Sign_Up_Page():
    return render_template('signUp.html')


@app.route('/signup', methods=['POST'])
def Sign_Up():
    userID = request.form['userID']
    password = request.form['password']
    nickname = request.form['nickname']

    # DB에 삽입할 user 만들기
    user = {
        'userID': userID,
        'password': password,
        'nickname': nickname
    }

    # user 에 user 저장하기
    db.user.insert_one(user)

    # login 페이지로 이동
    # return jsonify({'result': 'success', 'msg': '회원가입이 완료되었습니다'})
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def Logout():
    session.pop('sessionID')
    return jsonify({'result': 'success'})


@app.route('/<category>', methods=['GET'])
def Get_Pictures(category):
    # 1. DB에서 리뷰 정보 모두 가져오기
    if category == 'all':
        pictureInfos = list(db.pictureInfos.find({}, {'_id':0}))
    else:
        pictureInfos = list(db.pictureInfos.find({'category': category}, {'_id':0}))

    # 2. 성공 여부 & 리뷰 목록 반환하기
    return jsonify({'result': 'success', 'pictureInfos': pictureInfos})


@app.route('/<searchCategory>/<searchContent>', methods=['GET'])
def Search_Content(searchCategory, searchContent):
    # 1. DB에서 리뷰 정보 모두 가져오기
    if searchCategory == 'searchTitle':
        pictureInfos = list(db.pictureInfos.find({'title': {'$regex':searchContent, '$options': 'i'}}, {'_id': 0}))
    elif searchCategory == 'searchNickname':
        pictureInfos = list(db.pictureInfos.find({'nickname': {'$regex':searchContent, '$options': 'i'}}, {'_id': 0}))
    elif searchCategory == 'searchComment':
        pictureInfos = list(db.pictureInfos.find({'comment': {'$regex':searchContent, '$options': 'i'}}, {'_id': 0}))
    else:
        pictureInfos = list(db.pictureInfos.find({'$or':[{'title': {'$regex':searchContent, '$options': 'i'}},{'nickname': {'$regex':searchContent, '$options': 'i'}},{'comment': {'$regex':searchContent, '$options': 'i'}}]}, {'_id': 0}))

    # 2. 성공 여부 & 리뷰 목록 반환하기
    return jsonify({'result': 'success', 'pictureInfos': pictureInfos})


@app.route('/pictureregist', methods=['GET'])
def Picture_Regist_Page():
    picturenumber = db.pictureInfos.count() + 1
    # 세션에 'sessionID'라는 변수가 있는
    if 'sessionID' in session:
        # 세션에 'sessionID'라는 변수의 값을 가져와서
        session_id = session['sessionID']
        # 'sessionID'에 담긴 값(유저 생성시에 만들어진 _id 값)에 대한
        # 유저 정보가 user DB에 있는지 확인
        user = db.user.find_one({'_id': ObjectId(session_id)})
        print(session_id)
        # 세션에 'sessionID'라는 변수의 값이 비어있거나
        # 'sessionID'에 담긴 값(유저 생성시에 만들어진 _id 값)에 대한
        # 유저 정보가 없다면
        if session_id is None or user is None:
            # 로그인 페이지를 띄워줌
            return render_template('login.html')
        # 아니라면 로그인 한 세션이 있는 유저이므로 메인 페이지로 보냄
        return render_template('pictureRegist.html', nickname=user['nickname'], userkey=user['_id'], picturenumber=picturenumber)
    return render_template('login.html')



@app.route('/pictureregist', methods=['POST'])
def Picture_Regist():
    # 클라이언트가 give로 준 값들 가져오기
    imgurl_receive = request.form['imgURL_give']
    category_receive = request.form['category_give']
    title_receive = request.form['title_give']
    comment_receive = request.form['comment_give']
    date_receive = request.form['date_give']
    nickname_receive = request.form['nickname_give']
    userkey_receive = request.form['userkey_give']
    picturenumber_receive = request.form['picturenumber_give']


    # DB에 삽입할 pictureInfo 만들기
    pictureInfo = {
        'imgURL': imgurl_receive,
        'category': category_receive,
        'title': title_receive,
        'comment': comment_receive,
        'date': date_receive,
        'nickname': nickname_receive,
        'userkey': userkey_receive,
        'likeCount': 0,
        'picturenumber': picturenumber_receive
    }

    # pictureInfos 에 pictureInfo 저장하기
    db.pictureInfos.insert_one(pictureInfo)
    
    # 성공 여부 & 성공 메시지 반환
    return jsonify({'result': 'success', 'msg': '저장되었습니다!'})


@app.route('/picturedetail/<picturenumber>/', methods=['GET'])
def picture_detail_Page(picturenumber):
    # 세션에 'sessionID'라는 변수가 있는
    if 'sessionID' in session:
        # 세션에 'sessionID'라는 변수의 값을 가져와서
        session_id = session['sessionID']
        # 'sessionID'에 담긴 값(유저 생성시에 만들어진 _id 값)에 대한
        # 유저 정보가 user DB에 있는지 확인
        user = db.user.find_one({'_id': ObjectId(session_id)})
        print(session_id)
        # 세션에 'sessionID'라는 변수의 값이 비어있거나
        # 'sessionID'에 담긴 값(유저 생성시에 만들어진 _id 값)에 대한
        # 유저 정보가 없다면
        if session_id is None or user is None:
            # 로그인 페이지를 띄워줌
            return render_template('login.html')
        # 아니라면 로그인 한 세션이 있는 유저이므로 메인 페이지로 보냄
        picture_detail = list(db.pictureInfos.find({'picturenumber': picturenumber}))
        picture_detail_content = {'picturenumber': picture_detail[0]['picturenumber'],
                                  'title': picture_detail[0]['title'],
                                  'category': picture_detail[0]['category'],
                                  'nickname': picture_detail[0]['nickname'],
                                  'comment': picture_detail[0]['comment'],
                                  'imgURL': picture_detail[0]['imgURL'],
                                  'date': picture_detail[0]['date'],
                                  'likeCount': picture_detail[0]['likeCount']}
        return render_template('pictureDetail.html', detailContent=picture_detail_content, nickname=user['nickname'],
                               userkey=user['_id'])
    return render_template('pictureDetail.html')


@app.route('/addgallery', methods=['POST'])
def Add_Gallery():
    # 클라이언트가 give로 준 값들 가져오기
    userkey_receive = request.form['userkey_give']
    picturenumber_receive = request.form['picturenumber_give']

    # DB에 삽입할 gallery 만들기
    gallery = {'userkey': userkey_receive,
               'picturenumber': picturenumber_receive}

    # pictureInfos 에 pictureInfo 저장하기
    db.gallery.insert_one(gallery)
    
    return jsonify({'result': 'success', 'msg': '갤러리에 추가되었습니다'})


@app.route('/rank/<category>', methods=['GET'])
def Rank_Page(category):
    # 세션에 'sessionID'라는 변수가 있는
    if 'sessionID' in session:
        # 세션에 'sessionID'라는 변수의 값을 가져와서
        session_id = session['sessionID']
        # 'sessionID'에 담긴 값(유저 생성시에 만들어진 _id 값)에 대한
        # 유저 정보가 user DB에 있는지 확인
        user = db.user.find_one({'_id': ObjectId(session_id)})
        print(session_id)
        # 세션에 'sessionID'라는 변수의 값이 비어있거나
        # 'sessionID'에 담긴 값(유저 생성시에 만들어진 _id 값)에 대한
        # 유저 정보가 없다면
        if session_id is None or user is None:
            # 로그인 페이지를 띄워줌
            return render_template('login.html')
        # 아니라면 로그인 한 세션이 있는 유저이므로 메인 페이지로 보냄

        # 카테고리에 따라 likeCount 값을 이용하여 오름차순으로 정렬
        if category == '전체랭킹' or category == '전체 랭킹':
            picture_rank_content = list(db.pictureInfos.find({}).sort("likeCount", -1))
        else:
            picture_rank_content = list(db.pictureInfos.find({'category': category}).sort("likeCount", -1))

        return render_template('rank.html', picture_rank_content=picture_rank_content, nickname=user['nickname'], category=category)
    return render_template('rank.html')


@app.route('/mypicture', methods=['GET'])
def Mypicture_Page():
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
        # 아니라면 로그인 한 세션이 있는 유저이므로 갤러리 페이지로 보냄
        return render_template('mypicture.html', nickname=user['nickname'], userkey=user['_id'])
    return render_template('mypicture.html')


@app.route('/getmypicture', methods=['GET'])
def Get_Mypicture():
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

    # 1. DB에서 리뷰 정보 모두 가져오기
    mypicture = list(db.pictureInfos.find({'userkey': session['sessionID']}, {'_id': 0}))

    # 2. 성공 여부 & 리뷰 목록 반환하기
    return jsonify({'result': 'success', 'mypicture': mypicture})

#
# @app.route('/gallery', methods=['GET'])
# def Gallery_Page():
#     # 세션에 'sessionID'라는 변수가 있는
#     if 'sessionID' in session:
#         # 세션에 'sessionID'라는 변수의 값을 가져와서
#         session_id = session['sessionID']
#         # 'sessionID'에 담긴 값(유저 생성시에 만들어진 _id 값)에 대한
#         # 유저 정보가 user DB에 있는지 확인
#         user = db.user.find_one({'_id': ObjectId(session_id)})
#
#         # 세션에 'sessionID'라는 변수의 값이 비어있거나
#         # 'sessionID'에 담긴 값(유저 생성시에 만들어진 _id 값)에 대한
#         # 유저 정보가 없다면
#         if session_id is None or user is None:
#             # 로그인 페이지를 띄워줌
#             return render_template('login.html')
#         # 아니라면 로그인 한 세션이 있는 유저이므로 갤러리 페이지로 보냄
#         return render_template('gallery.html', nickname=user['nickname'], userkey=user['_id'])
#     return render_template('gallery.html')

#
# @app.route('/getgallery', methods=['GET'])
# def Get_Gallery():
#     # 세션에 'sessionID'라는 변수가 있는
#     if 'sessionID' in session:
#         # 세션에 'sessionID'라는 변수의 값을 가져와서
#         session_id = session['sessionID']
#         # 'sessionID'에 담긴 값(유저 생성시에 만들어진 _id 값)에 대한
#         # 유저 정보가 user DB에 있는지 확인
#         user = db.user.find_one({'_id': ObjectId(session_id)})
#
#         # 세션에 'sessionID'라는 변수의 값이 비어있거나
#         # 'sessionID'에 담긴 값(유저 생성시에 만들어진 _id 값)에 대한
#         # 유저 정보가 없다면
#         if session_id is None or user is None:
#             # 로그인 페이지를 띄워줌
#             return render_template('login.html')
#         # 아니라면 로그인 한 세션이 있는 유저이므로 메인 페이지로 보냄
#
#     # 1. DB에서 리뷰 정보 모두 가져오기
#     gallery_picture_number = list(db.gallery.find({'userkey': session['sessionID']}, {'_id': 0, 'userkey': 0}))
#     picture_number = list(gallery_picture_number.value())
#     for i in picture_number:
#
#
#     # 2. 성공 여부 & 리뷰 목록 반환하기
#     return jsonify({'result': 'success', 'gallery': gallery})
#


@app.route('/like', methods=['POST'])
def Add_Like():
    # 1. 클라이언트가 준 값 가져오기
    picturenumber_receive = request.form['picturenumber_give']

    # 2. picturenumber 일치하는 그림 찾기
    picturelike = db.pictureInfos.find_one({'picturenumber': picturenumber_receive})['likeCount']

    # 3. like 에 1더하기
    new_like = picturelike + 1

    # 4. pictureInfos 목록에서 pictruenumber이 picturenumber_receive인 문서의 likeCount 를 new_like 로 변경

    db.pictureInfos.update_one({'picturenumber': picturenumber_receive}, {'$set': {'likeCount': new_like}})
    return jsonify({'result': 'success', 'msg': "좋아요!!"})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)