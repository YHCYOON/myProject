from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('localhost', 27017)  #mongoDB는 27017 포트로 돌아갑니다.
db = client.DraWell  # 'DraWell'라는 이름의 db를 만들거나 사용합니다.

@app.route('/index')
def index():
    return render_template('index.html')


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


@app.route('/pictureRegist', methods=['GET'])
def picture_Regist_Page():
    return render_template('pictureRegist.html')


@app.route('/pictureRegist', methods=['POST'])
def picture_Regist():
    # 클라이언트가 give로 준 값들 가져오기
    imgurl_receive = request.form['imgURL_give']
    category_receive = request.form['category_give']
    id_receive = request.form['userID_give']
    pw_receive = request.form['userPW_give']
    nickname_receive = request.form['userNickname_give']
    title_receive = request.form['title_give']
    comment_receive = request.form['comment_give']

    # DB에 삽입할 pictureInfo 만들기
    pictureInfo = {
        'imgURL': imgurl_receive,
        'category': category_receive,
        'userID': id_receive,
        'userPW': pw_receive,
        'userNickname': nickname_receive,
        'title': title_receive,
        'comment': comment_receive
    }

    # pictureInfos 에 pictureInfo 저장하기
    db.pictureInfos.insert_one(pictureInfo)
    
    # 성공 여부 & 성공 메시지 반환
    return jsonify({'result': 'success', 'msg': '등록되었습니다!'})


@app.route('/pictureRank')
def picture_Rank():
    return render_template('pictureRank.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)