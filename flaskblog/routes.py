import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort,Response
from flaskblog import app, db, bcrypt , mail ,Message
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                MemberForm,RequestResetForm,ResetPasswordForm,ConfirmRequestForm,
                                RoomIDForm,ContactForm)
from flaskblog.models import User,Member,Alert
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
import cv2
import face_recognition
import numpy as np
from timeit import default_timer as timer


known_face_names = []
images = []

def walk(RoomID):
    images.clear()
    user=User.query.filter_by(id=RoomID).first()
    for member in user.members:
        memeber_image_file = os.path.join(app.root_path, 'static\profile_pics',  member.image_file)
        # print(' memeber_image_file:', memeber_image_file)        
        curImg = cv2.imread(memeber_image_file)
        images.append(curImg)
        name=member.username
        known_face_names.append(name)



def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def mark_attendance(name,user_id):
    user=User.query.filter_by(id=user_id).first()
    member=Member.query.filter_by(username=name,admin=user).first()
    # print(member) #testing
    curr_time=datetime.utcnow()
    last_attendace_time=member.attendance_time
    # print(last_attendace_time)  #testing
    time_gap=curr_time-last_attendace_time
    print(time_gap)
    minimum_time_gap=user.time_gap*3600 #in seconds

    if (time_gap.total_seconds())>minimum_time_gap:
        member.attendance_count=member.attendance_count+1
        member.attendance_time=curr_time
        db.session.commit()

#testing mail for alert
# def send_mail_alert(user,picture_fn):
#     picture_path = os.path.join(app.root_path, 'static/alert_pics', picture_fn)

#     msg = Message("Unknown Person Alert",
#                     sender="project.pleasenoreply@gmail.com",
#                     recipients=[user.email],)
    
#     msg.body = "An Unknown person is trying to mark attendance"
#     with app.open_resource(picture_path) as fp:
#         msg.attach(picture_path, "image/jpg", fp.read())
#     mail.send(msg)

def create_alert(user_id,picture_fn):
    # user=User.query.filter_by(id=user_id).first()
    # send_mail_alert(user,picture_fn)
    alert = Alert(image_file=picture_fn,user_id=user_id)
    db.session.add(alert)
    db.session.commit()


def gen_frames(RoomID):
    camera = cv2.VideoCapture(0)
    print('image files in gen_frame',known_face_names)
    known_face_encodings = findEncodings(images)
    # print('Encoding Complete')
    user=User.query.filter_by(id=RoomID).first()
    # min_time_gap=user.time_gap/3600

    flag=0
    end_time=0
    start_time=timer()
    while (end_time-start_time)<120:
    # while True:
        count =0
        name_index=[]
        num_frames=5
        # now count frames and then output a name for it 
        while count< num_frames:
            success, img = camera.read()
            if not success:
                break
            else:

                #img = captureScreen() #to capture screen
                imgS = cv2.resize(img,(0,0),None,0.50,0.50)
                imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

                #encoding the current frame
                facesCurFrame = face_recognition.face_locations(imgS)
                encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)

                # marking the face and compare it with given database
                for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
                    matches = face_recognition.compare_faces(known_face_encodings,encodeFace)
                    faceDis = face_recognition.face_distance(known_face_encodings,encodeFace)
                    # print(matches) 
                    # print(faceDis)
                    matchIndex = np.argmin(faceDis)
            
                    if faceDis[matchIndex]<=0.60:
                            name = known_face_names[matchIndex].upper()
                            # markAttendance(name)
                    else:
                        name = 'Unknown'
                        matchIndex=-1
                    #adding the result in array for each frames 
                    name_index.append(matchIndex)

                    y1,x2,y2,x1 = faceLoc
                    y1, x2, y2, x1 = y1*2,x2*2,y2*2,x1*2
                    cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
                    cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
                    cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                    
                    count=count+1 
                    # print("count=",count)

                ret, buffer = cv2.imencode('.jpg', img)
                img = buffer.tobytes()
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')

        # final_index=statistics.mode(name_index)
        final_index=max(set(name_index), key=name_index.count)
        if(final_index!=-1):
                name=known_face_names[final_index]
                mark_attendance(name=name,user_id=RoomID)      

        else: 
            name="Unknown"
            #save the image
            alert_image=camera.read()
            random_hex = secrets.token_hex(8)
            random_hex=random_hex+'.jpg'
            picture_path = os.path.join(app.root_path, 'static/alert_pics', random_hex)
            cv2.imwrite(picture_path,alert_image[1]) 

            camera.release()
            cv2.destroyAllWindows() 
            flag=1 #break the outer loop

            create_alert(user_id=RoomID,picture_fn=random_hex)
            break


        # print(name)  #testing
        print(name_index)  #testing
        if flag==1:
            break 
        end_time=timer()
    camera.release()
    cv2.destroyAllWindows() 

@app.route('/FaceRecognise/<int:RoomID>')
def FaceRecognise(RoomID):
    # walk(where='index')
    walk(RoomID)
    return render_template('FaceRecognise.html',RoomID=RoomID)


@app.route('/video_feed/<int:RoomID>')
def video_feed(RoomID):
    return Response(gen_frames(RoomID=RoomID), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/")
@app.route("/home", methods=['GET','POST'])
def home():
    if current_user.is_authenticated:
        return redirect(url_for('Alerts'))
    return render_template('welcome.html')
    


@app.route("/about",methods=['GET', 'POST'])
def about():
    form = ContactForm()
    if form.validate_on_submit():
        name=form.name.data
        message=form.message.data
        email=form.email.data
        msg = Message("Message from face recognition project",
                  sender='project.pleasenoreply@gmail.com',
                  recipients=['mukulgupta2718@gmail.com'])
        msg.body = f'''Hello I am {name}, 
my message :
{message}

you can contact me at {email}.
'''
        mail.send(msg)
        flash('Message has been sent !', 'success')
        return redirect(url_for('home'))
    return render_template('about.html', title='Contact Me',form=form)


def save_picture(form_picture):
    #save picture with random hex name
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    # output_size = (125, 125)  # #this resizing can make website fast but will degrade image recognition
    i = Image.open(form_picture)
    # i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/register", methods=['GET', 'POST'])
def register():
    #to logout the current user if he is logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    #save hashed password in database   
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        picture_file = save_picture(form.picture.data)
        user = User(username=form.username.data, email=form.email.data,
                         password=hashed_password,image_file=picture_file)
        db.session.add(user)
        db.session.commit()
        send_mail_confirmation(user)
        flash('Your account has been created! Verification email has been sent to the registered email address\
                \n Verify your Email to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.email_confirmed: #if email is verified , only then allow login
                if bcrypt.check_password_hash(user.password, form.password.data) :
                    login_user(user, remember=form.remember.data)

                    # next_page = request.args.get('next')
                    # return redirect(next_page) if next_page else redirect(url_for('home'))
                    return redirect(url_for('home'))
                else:
                    flash('Login Unsuccessful. Please check email and password', 'danger')
            else:
                flash('Login Unsuccessful. Please verify your email ', 'danger')    
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/RoomID", methods=['GET', 'POST'])
def RoomID():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RoomIDForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=form.RoomID.data).first()
        return redirect(url_for('FaceRecognise',RoomID=user.id))
    return render_template('RoomID.html', form=form,title='Enter Room')    


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            old_pic_path=os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
            current_user.image_file = picture_file
            os.remove(old_pic_path)

        current_user.username = form.username.data
        current_user.time_gap = form.TimeGap.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('all_members'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.TimeGap.data = current_user.time_gap
        form.email.data = current_user.email
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/account/member/<int:member_id>/update", methods=['GET', 'POST'])
@login_required
def member_account(member_id):
    member = Member.query.get_or_404(member_id)
    if member.admin != current_user:
        abort(403)
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            old_pic_path=os.path.join(app.root_path, 'static/profile_pics', member.image_file)
            member.image_file = picture_file
            os.remove(old_pic_path)

        member.username = form.username.data
        member.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('all_members'))
    elif request.method == 'GET':
        form.username.data = member.username
        form.email.data = member.email
        image_file = url_for('static', filename='profile_pics/' + member.image_file)
    return render_template('member_account.html', title='Member Account',
                           image_file=image_file, form=form, member_id=member.id, member=member)

@app.route("/members/all", methods=['GET', 'POST'])
@login_required
def all_members():
    page = request.args.get('page', 1, type=int)
    members = Member.query.filter_by(admin=current_user).paginate(page=page, per_page=5)
    user_image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('all_members.html', members=members, image_file= user_image_file)



@app.route("/member/new", methods=['GET', 'POST'])
@login_required
def new_member():
    form = MemberForm()
    if form.validate_on_submit():
        picture_file = save_picture(form.picture.data)
        member = Member(username=form.username.data, email=form.email.data,
                         image_file=picture_file,admin=current_user)
        db.session.add(member)
        db.session.commit()
        flash('New Member has been added !', 'success')
        return redirect(url_for('all_members'))
    return render_template('create_member.html', title='New Member',
                           form=form, legend='New Member')


@app.route("/member/<int:member_id>/delete", methods=['POST'])
@login_required
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    if member.admin != current_user:
        abort(403)
    pic_path=os.path.join(app.root_path, 'static/profile_pics', member.image_file)
    os.remove(pic_path)
    db.session.delete(member)
    db.session.commit()
    flash(member.username+'has been Removed!', 'success')
    return redirect(url_for('all_members'))


@app.route("/user/alerts")
@login_required
def Alerts():
    return redirect(url_for('user_alerts',username=current_user.username))

@app.route("/user/<string:username>/alerts")
@login_required
def user_alerts(username):
    page = request.args.get('page', 1, type=int)
    # user = User.query.filter_by(username=username).first_or_404()
    alerts = Alert.query.filter_by(author=current_user)\
        .order_by(Alert.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_alerts.html', alerts=alerts, user=current_user)

@app.route("/user/alerts/delete/<int:alert_id>", methods=['POST'])
@login_required
def delete_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    if alert.author != current_user:
        abort(403)
    pic_path=os.path.join(app.root_path, 'static/alert_pics', alert.image_file)
    os.remove(pic_path)
    db.session.delete(alert)
    db.session.commit()
    flash('the has been Removed!', 'success')
    return redirect(url_for('Alerts'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='project.pleasenoreply@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

def send_mail_confirmation(user):
    token = user.get_mail_confirm_token()
    
    msg = Message("Please Confirm Your Email",
                    sender="project.pleasenoreply@gmail.com",
                    recipients=[user.email],)
    
    msg.body = f'''To verify your email, visit the following link:
{url_for('confirm_email', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
    

@app.route("/confirm_email", methods=['GET', 'POST'])
def confirm_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ConfirmRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user.email_confirmed:
            send_mail_confirmation(user)
            flash('An email has been sent with instructions to Verify yor email address.', 'info')
        flash('Email already Verified!', 'info')
        return redirect(url_for('login'))
    return render_template('confirm_request.html', title='Verify Email', form=form)

@app.route('/confirm_email/<token>')
def confirm_email(token):
    email = User.verify_mail_confirm_token(token)
    if email:
        user = User.query.filter_by(email=email).first()
        user.email_confirmed = True
        # user.email_confirm_date = datetime.utcnow()
        # db.session.add(user)
        db.session.commit()
        flash( 'Your email has been verified and you can now login to your account',"success",)
        return redirect(url_for("login"))
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('login'))
        # return render_template("errors/token_invalid.html")


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)