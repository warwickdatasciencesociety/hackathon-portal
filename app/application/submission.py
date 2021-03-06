from flask_login import login_required, current_user
from flask import Blueprint, request, render_template, redirect
from flask import current_app as app

from flask_jwt_extended import jwt_optional, get_jwt_identity
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from werkzeug.utils import secure_filename
from .models import Submission, User, UserTeam, Team
from .score import evaluate_score
from . import db
import datetime, time
import os

# blueprint configuration
submission_bp = Blueprint("submission_bp", __name__)
# root POST request for now

def get_scores():
    scores = db.session.query(Submission.team_id, func.min(Submission.score)).group_by(Submission.team_id).all()

    # can't be asked to look up SQLAlchemy joins
    scores_names = list()
    for (teamid, score) in scores:
        scores_names.append((Team.query.filter_by(team_id=teamid).first().teamname, score))

    return sorted(scores_names, key=lambda x : x[1])

@submission_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    d = datetime.datetime.utcnow()
    end_date = datetime.datetime.strptime('Nov 15 2020 7:00PM', '%b %d %Y %I:%M%p')
    if d >= end_date:
        return redirect("/thankyou")
    username=current_user.username
    # username = get_jwt_identity()
    # # username is None if not logged in
    # # redirect if this is the case
    # if username is None:
    #     return redirect("/login")
    user_id = User.query.filter_by(username=username).first().user_id
    team_id = UserTeam.query.filter_by(user_id=user_id).first().team_id
    team_name = Team.query.filter_by(team_id=team_id).first().teamname

    potential_d = Submission.query.filter_by(team_id=team_id).order_by(desc(Submission.upload_time)).first()

    if potential_d is None:
        d = datetime.datetime.utcnow() + datetime.timedelta(hours=-1)
    else:
        d = potential_d.upload_time


    if request.method == "POST":
        if (d + datetime.timedelta(hours=1) < datetime.datetime.utcnow()):

            csv_file = request.files["cFile"]
            jupyter_file = request.files["jFile"]
            # check extensions
            csv_filename = csv_file.filename
            jupyter_filename = jupyter_file.filename
            if "." in csv_filename and csv_filename.rsplit(".", 1)[1].lower() == "csv" and "." in jupyter_filename and jupyter_filename.rsplit(".", 1)[1].lower() == "ipynb":
                csv_filename = secure_filename(csv_file.filename)
                jupyter_filename = secure_filename(jupyter_file.filename)

                # save the files to the upload folder
                # get the id to give them
                new_submission = Submission(team_id=team_id, user_id = user_id, upload_time=datetime.datetime.utcnow(), tag=request.form["tag"])

                

                csv_file.save(os.path.join(app.config["UPLOAD_FOLDER"], f"{new_submission.submission_id}.csv"))
                jupyter_file.save(os.path.join(app.config["UPLOAD_FOLDER"], f"{new_submission.submission_id}.ipynb"))
                eval_score = evaluate_score(os.path.join(app.config["UPLOAD_FOLDER"], f"{new_submission.submission_id}.csv"), os.path.join(app.config["ML_FOLDER"], "gt.csv"))
                # call the score function
                if eval_score == 2147483647:
                    scores = get_scores()
                    submissions = db.session.query(Submission.score, Submission.tag, Submission.user_id).filter_by(team_id=team_id).all()
                    subs = []
                    for submission in submissions:
                        user_submission = db.session.query(User.username).filter_by(user_id=submission[2]).first()
                        subs.append([submission[0], submission[1], user_submission[0]])
                    return render_template("portal.html",
                        username=username,
                        team_name=team_name,
                        scores=scores,submissions=subs,sub_length=len(submissions),
                        year=d.year, month=d.month-1, day=d.day, hour=d.hour, minute=d.minute,
                        second=d.second,
                        submission_status="Submission Error: Invalid .csv file submitted")
                db.session.add(new_submission)
                db.session.flush()
                new_submission.score = eval_score
                
                db.session.add(new_submission)
                db.session.commit()
                return redirect("/")

            scores = get_scores()
            submissions = db.session.query(Submission.score, Submission.tag, Submission.user_id).filter_by(team_id=team_id).all()
            subs = []
            for submission in submissions:
                user_submission = db.session.query(User.username).filter_by(user_id=submission[2]).first()
                subs.append([submission[0], submission[1], user_submission[0]])
            return render_template("portal.html",
                username=username,
                team_name=team_name,
                scores=scores,submissions=subs,sub_length=len(submissions),
                year=d.year, month=d.month-1, day=d.day, hour=d.hour, minute=d.minute,
                second=d.second,
                submission_status="Submission Error: Bad file extensions used")


        return render_template("portal.html",
                username=username,
                team_name=team_name,
                scores=scores,submissions=submissions,sub_length=len(submissions),
                year=d.year, month=d.month-1, day=d.day, hour=d.hour, minute=d.minute,
                second=d.second,
                submission_status="Submission Error: You already submitted less than an hour ago!")
        
    # get the team ID and max score
    scores = get_scores()

    submissions = db.session.query(Submission.score, Submission.tag, Submission.user_id).filter_by(team_id=team_id).all()
    subs = []
    for submission in submissions:
        user_submission = db.session.query(User.username).filter_by(user_id=submission[2]).first()
        subs.append([submission[0], submission[1], user_submission[0]])

    return render_template("portal.html",
            username=username,
            team_name=team_name,
            scores=scores,submissions=subs,sub_length=len(submissions),
            year=d.year, month=d.month-1, day=d.day, hour=d.hour, minute=d.minute,
            second=d.second,
            )
