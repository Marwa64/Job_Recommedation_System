import flask
from flask import request
import json
from flask import jsonify
from flask_cors import CORS
from JobRecommender import job_recommendation
from database_connection import get_database

app = flask.Flask(__name__)
CORS(app)
cors = CORS(app, resource={
   r"/*": {
       "origins": "*"
   }
})
app.config["DEBUG"] = True


db = get_database()


@app.route('/', methods=['GET'])
def home():
   return "<h1>Recommender System</h1>"


# A route to return add a job the user was interested in
@app.route('/job_viewed/<profile_id>', methods=['POST'])
def add_job_viewed(profile_id):
   content_type = request.headers.get('Content-Type')
   if content_type == 'application/json':
       payload = request.json
       db_obj = db.viewed_jobs.find_one({"profile_id": profile_id})
       viewed_jobs = []
       if db_obj:
           viewed_jobs = db_obj["jobs"]

       while viewed_jobs.__len__() >= 3:
           viewed_jobs.pop(0)
       viewed_jobs.append(payload)

       myquery = {"profile_id": profile_id}
       new_values = {"$set": {"jobs": viewed_jobs}}
       if db_obj:
           db.viewed_jobs.update_one(myquery, new_values)
       else:
           db.viewed_jobs.insert_one({"profile_id": profile_id, "jobs": viewed_jobs})
       return 'Job Added'
   else:
       return 'Content-Type not supported!'


# A route to return top 9 job recommendations
@app.route('/jobs/<track>', methods=['POST'])
def jobs(track):
   content_type = request.headers.get('Content-Type')
   if content_type == 'application/json':
       payload = request.json
       result_urls = []
       db_obj = db.viewed_jobs.find_one({"profile_id": payload['profile_id']})
       viewed_jobs = []
       if db_obj:
           viewed_jobs = db_obj["jobs"]
           for viewed in viewed_jobs:
               result_urls.append(viewed["url"])

       recomm = job_recommendation(track, viewed_jobs, 16)
       result_dict = []
       for job_recomm in recomm:
           for test in job_recomm.iterrows():
               obj = test[1].to_json(orient="index")
               jsonObject = json.loads(obj)
               if jsonObject['url'] not in result_urls:
                   result_urls.append(jsonObject['url'])
                   result_dict.append(jsonObject)

       return jsonify(result_dict)

   else:
       return 'Content-Type not supported!'


app.run()
