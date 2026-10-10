from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file
)

import os
import json
from functools import wraps
from datetime import datetime

import joblib
import numpy as np

from werkzeug.utils import secure_filename

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet


# ============================================================
# APP CONFIGURATION
# ============================================================

app = Flask(__name__)

app.secret_key = "AI_CAMPUS_PLACEMENT_SECRET_8763"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATES_DIR = os.path.join(
    BASE_DIR,
    "templates"
)

STATIC_DIR = os.path.join(
    BASE_DIR,
    "static"
)

UPLOAD_DIR = os.path.join(
    STATIC_DIR,
    "uploads"
)

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# PROJECT INFORMATION
# ============================================================

TEAM_NAME = "SECRET CIRCLE 🔴"

PROJECT_NAME = "AI CAMPUS PLACEMENT PRO"


# ============================================================
# MACHINE LEARNING MODEL
# ============================================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "placement_model.pkl"
)

try:

    model = joblib.load(MODEL_PATH)

    print("=" * 60)
    print("PLACEMENT MODEL LOADED SUCCESSFULLY")
    print("=" * 60)

except Exception as e:

    model = None

    print("=" * 60)
    print("PLACEMENT MODEL COULD NOT BE LOADED")
    print("ERROR:", e)
    print("=" * 60)


# ============================================================
# USER DATABASE
# ============================================================

USERS_FILE = os.path.join(
    BASE_DIR,
    "users.json"
)


def load_users():

    if not os.path.exists(USERS_FILE):
        return {}

    try:

        with open(
            USERS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, dict):
                return data

            return {}

    except Exception as e:

        print("Users file error:", e)

        return {}


def save_users(users):

    try:

        with open(
            USERS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                users,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except Exception as e:

        print("Could not save users:", e)

        return False


# ============================================================
# DEFAULT USER DATA
# ============================================================

def default_user_data():

    return {

        # Login
        "password": "8763",

        # Personal Profile
        "name": "Abhijeet Sabut",
        "email": "",
        "phone": "",
        "date_of_birth": "",
        "gender": "",
        "address": "",

        # Academic Profile
        "course": "CSE",
        "branch": "CSE",
        "department": "CSE",
        "semester": "5th Sem",
        "college": "AIET",
        "roll_no": "",
        "candidate_id": "",
        "graduation_year": "2028",

        # Academic Details
        "cgpa": "",
        "ssc_marks": "",
        "hsc_marks": "",
        "backlogs": "0",

        # Experience
        "internships": "1",
        "projects": "3",
        "certifications": "4",
        "workshops": "4",

        # Skills
        "aptitude": "78",
        "soft_skills": "75",
        "coding_skills": "90",
        "communication": "75",

        # Activities
        "extracurricular": "No",
        "placement_training": "Yes",

        # Photo
        "profile_photo": "",

        # Prediction History
        "history": []
    }


# ============================================================
# CURRENT LOGIN USER
# ============================================================

def get_current_username():

    return session.get(
        "user",
        ""
    )


# ============================================================
# CURRENT USER DATA
# ============================================================

def get_current_user_data():

    username = get_current_username()

    if not username:

        return default_user_data()

    users = load_users()

    defaults = default_user_data()

    # ========================================================
    # DEFAULT ABHIJEET ACCOUNT
    # ========================================================

    if username == "abhijeet":

        if username not in users:

            users[username] = defaults

            save_users(users)

            return users[username]

        user = users[username]

        changed = False

        for key, value in defaults.items():

            if key not in user:

                user[key] = value

                changed = True

        if changed:

            save_users(users)

        return user

    # ========================================================
    # REGISTERED USER
    # ========================================================

    if username in users:

        user = users[username]

        changed = False

        for key, value in defaults.items():

            if key not in user:

                user[key] = value

                changed = True

        if changed:

            save_users(users)

        return user

    # ========================================================
    # FALLBACK
    # ========================================================

    data = defaults.copy()

    data["name"] = username

    return data


# ============================================================
# SAVE CURRENT USER DATA
# ============================================================

def save_current_user_data(data):

    username = get_current_username()

    if not username:

        print("SAVE ERROR: No logged-in user.")

        return False

    users = load_users()

    if username not in users:

        users[username] = default_user_data()

    users[username].update(data)

    success = save_users(users)

    if success:

        # ----------------------------------------------------
        # IMPORTANT:
        # Update session display name immediately.
        # ----------------------------------------------------

        saved_name = str(
            users[username].get(
                "name",
                ""
            )
        ).strip()

        if saved_name:

            session["display_name"] = saved_name

        print("=" * 60)
        print("USER DATA SAVED SUCCESSFULLY")
        print("LOGIN ID:", username)
        print("DISPLAY NAME:", saved_name)
        print("=" * 60)

    else:

        print("USER DATA SAVE FAILED")

    return success


# ============================================================
# GLOBAL JINJA VARIABLES
# ============================================================

@app.context_processor
def inject_global_data():

    user_data = get_current_user_data()

    login_username = get_current_username()

    saved_profile_name = str(
        user_data.get(
            "name",
            ""
        )
    ).strip()

    # --------------------------------------------------------
    # IMPORTANT FIX
    #
    # Dashboard/sidebar should display the saved profile name.
    #
    # Login ID remains available separately as login_username.
    # --------------------------------------------------------

    display_name = (
        saved_profile_name
        if saved_profile_name
        else login_username
    )

    return {

        "team_name": TEAM_NAME,

        "project_name": PROJECT_NAME,

        # Actual login ID
        "login_username": login_username,

        # Saved profile name
        "display_name": display_name,

        # IMPORTANT:
        # Existing templates using {{ username }}
        # will now show the saved profile name.
        "username": display_name,

        # User data
        "user": user_data,

        "profile": user_data,

        "user_data": user_data,

        "current_user": user_data,

        "student": user_data,

        "student_profile": user_data,

        # Skills
        "skills": user_data,

        # Academic
        "academic": user_data,

        "academic_data": user_data,

        # Activities
        "activities": user_data
    }


# ============================================================
# TEMPLATE HELPERS
# ============================================================

def template_exists(filename):

    return os.path.exists(
        os.path.join(
            TEMPLATES_DIR,
            filename
        )
    )


def render_first_existing(
    filenames,
    **context
):

    for filename in filenames:

        if template_exists(filename):

            return render_template(
                filename,
                **context
            )

    return (

        "<h2>Template Not Found</h2>"

        "<p>Please create one of these templates:</p>"

        "<ul>"

        + "".join(
            f"<li>{filename}</li>"
            for filename in filenames
        )

        + "</ul>"

    ), 500


# ============================================================
# LOGIN REQUIRED
# ============================================================

def login_required(function):

    @wraps(function)

    def decorated_function(
        *args,
        **kwargs
    ):

        if "user" not in session:

            flash(
                "Please login to access this page.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        return function(
            *args,
            **kwargs
        )

    return decorated_function


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():

    if "user" not in session:

        return redirect(
            url_for("login")
        )

    return redirect(
        url_for("dashboard")
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if "user" in session:

        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            request.form.get(
                "user_id",
                request.form.get(
                    "user",
                    request.form.get(
                        "email",
                        ""
                    )
                )
            )
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not username or not password:

            flash(
                "Please enter your ID and password.",
                "error"
            )

            return render_template(
                "login.html"
            )

        username_lower = username.lower()

        users = load_users()

        # ====================================================
        # DEFAULT ACCOUNT
        # ====================================================

        if (
            username_lower == "abhijeet"
            and password == "8763"
        ):

            if "abhijeet" not in users:

                users["abhijeet"] = default_user_data()

                save_users(users)

            session.clear()

            session["user"] = "abhijeet"

            session["logged_in"] = True

            # Load saved profile name
            saved_user = users.get(
                "abhijeet",
                default_user_data()
            )

            session["display_name"] = saved_user.get(
                "name",
                "Abhijeet Sabut"
            )

            flash(
                f"Welcome back, {session['display_name']}!",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

        # ====================================================
        # REGISTERED USER
        # ====================================================

        matched_username = None

        for stored_username in users:

            if (
                stored_username.lower()
                == username_lower
            ):

                matched_username = stored_username

                break

        if matched_username:

            stored_user = users.get(
                matched_username,
                {}
            )

            stored_password = str(
                stored_user.get(
                    "password",
                    ""
                )
            )

            if stored_password == password:

                session.clear()

                session["user"] = matched_username

                session["logged_in"] = True

                session["display_name"] = stored_user.get(
                    "name",
                    matched_username
                )

                flash(
                    "Login successful!",
                    "success"
                )

                return redirect(
                    url_for("dashboard")
                )

        flash(
            "Invalid ID or password.",
            "error"
        )

        return render_template(
            "login.html"
        )

    return render_template(
        "login.html"
    )


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if "user" in session:

        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            request.form.get(
                "user_id",
                ""
            )
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            request.form.get(
                "confirmPassword",
                request.form.get(
                    "confirm",
                    ""
                )
            )
        )

        if not username or not password:

            flash(
                "Please fill all required fields.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        if len(username) < 3:

            flash(
                "ID must contain at least 3 characters.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        if len(password) < 4:

            flash(
                "Password must contain at least 4 characters.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        users = load_users()

        if username.lower() == "abhijeet":

            flash(
                "The ID 'abhijeet' is reserved.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        for existing_username in users:

            if (
                existing_username.lower()
                == username.lower()
            ):

                flash(
                    "This ID already exists.",
                    "error"
                )

                return redirect(
                    url_for("register")
                )

        data = default_user_data()

        data["password"] = password

        data["name"] = username

        data["candidate_id"] = username

        users[username] = data

        if save_users(users):

            flash(
                "Account created successfully. Please login.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        flash(
            "Could not create account.",
            "error"
        )

    return render_first_existing(
        [
            "register.html",
            "create_account.html"
        ]
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
@login_required
def dashboard():

    user_data = get_current_user_data()

    return render_first_existing(
        [
            "dashboard.html",
            "home.html"
        ],

        dashboard=True,

        user=user_data,

        profile=user_data,

        user_data=user_data,

        current_user=user_data,

        skills=user_data,

        academic=user_data,

        activities=user_data,

        # IMPORTANT
        username=user_data.get(
            "name",
            get_current_username()
        ),

        display_name=user_data.get(
            "name",
            get_current_username()
        )
    )


# ============================================================
# DASHBOARD ALIASES
# ============================================================

@app.route("/home")
@login_required
def home():

    return redirect(
        url_for("dashboard")
    )


@app.route("/dashbaord")
@login_required
def dashbaord():

    return redirect(
        url_for("dashboard")
    )


# ============================================================
# STUDENT PROFILE
# ============================================================

@app.route(
    "/student-profile",
    methods=["GET", "POST"]
)
@login_required
def student_profile():

    user_data = get_current_user_data()

    # ========================================================
    # SAVE PROFILE
    # ========================================================

    if request.method == "POST":

        print("=" * 60)
        print("PROFILE SAVE REQUEST RECEIVED")
        print("FORM DATA:")
        print(dict(request.form))
        print("=" * 60)

        # ----------------------------------------------------
        # Get existing values
        # ----------------------------------------------------

        old_name = user_data.get(
            "name",
            get_current_username()
        )

        old_email = user_data.get(
            "email",
            ""
        )

        old_phone = user_data.get(
            "phone",
            ""
        )

        old_dob = user_data.get(
            "date_of_birth",
            ""
        )

        old_gender = user_data.get(
            "gender",
            ""
        )

        old_college = user_data.get(
            "college",
            "AIET"
        )

        old_branch = user_data.get(
            "branch",
            "CSE"
        )

        old_course = user_data.get(
            "course",
            "CSE"
        )

        old_department = user_data.get(
            "department",
            "CSE"
        )

        old_semester = user_data.get(
            "semester",
            "5th Sem"
        )

        old_roll_no = user_data.get(
            "roll_no",
            ""
        )

        old_candidate_id = user_data.get(
            "candidate_id",
            get_current_username()
        )

        old_graduation_year = user_data.get(
            "graduation_year",
            "2028"
        )

        old_address = user_data.get(
            "address",
            ""
        )

        # ----------------------------------------------------
        # Accept multiple possible HTML field names
        # ----------------------------------------------------

        name = request.form.get(
            "name",
            request.form.get(
                "full_name",
                request.form.get(
                    "fullName",
                    old_name
                )
            )
        ).strip()

        email = request.form.get(
            "email",
            old_email
        ).strip()

        phone = request.form.get(
            "phone",
            request.form.get(
                "phone_number",
                request.form.get(
                    "phoneNumber",
                    old_phone
                )
            )
        ).strip()

        date_of_birth = request.form.get(
            "date_of_birth",
            request.form.get(
                "dob",
                request.form.get(
                    "dateOfBirth",
                    old_dob
                )
            )
        ).strip()

        gender = request.form.get(
            "gender",
            old_gender
        ).strip()

        college = request.form.get(
            "college",
            request.form.get(
                "college_university",
                request.form.get(
                    "collegeUniversity",
                    old_college
                )
            )
        ).strip()

        branch = request.form.get(
            "branch",
            old_branch
        ).strip()

        course = request.form.get(
            "course",
            old_course
        ).strip()

        department = request.form.get(
            "department",
            old_department
        ).strip()

        semester = request.form.get(
            "semester",
            old_semester
        ).strip()

        roll_no = request.form.get(
            "roll_no",
            request.form.get(
                "rollNumber",
                request.form.get(
                    "roll_number",
                    old_roll_no
                )
            )
        ).strip()

        candidate_id = request.form.get(
            "candidate_id",
            request.form.get(
                "candidateId",
                old_candidate_id
            )
        ).strip()

        graduation_year = request.form.get(
            "graduation_year",
            request.form.get(
                "graduationYear",
                old_graduation_year
            )
        ).strip()

        address = request.form.get(
            "address",
            old_address
        ).strip()

        # ----------------------------------------------------
        # DO NOT allow empty name to destroy saved name
        # ----------------------------------------------------

        if not name:

            name = old_name

        if not name:

            name = get_current_username()

        # ----------------------------------------------------
        # Candidate ID should never become empty
        # ----------------------------------------------------

        if not candidate_id:

            candidate_id = old_candidate_id

        if not candidate_id:

            candidate_id = get_current_username()

        # ----------------------------------------------------
        # Build profile data
        # ----------------------------------------------------

        profile_data = {

            "name": name,

            "email": email,

            "phone": phone,

            "date_of_birth": date_of_birth,

            "gender": gender,

            "college": college,

            "branch": branch,

            "course": course,

            "department": department,

            "semester": semester,

            "roll_no": roll_no,

            "candidate_id": candidate_id,

            "graduation_year": graduation_year,

            "address": address
        }

        print("=" * 60)
        print("PROFILE DATA TO SAVE:")
        print(profile_data)
        print("=" * 60)

        # ----------------------------------------------------
        # SAVE TO USERS.JSON
        # ----------------------------------------------------

        saved = save_current_user_data(
            profile_data
        )

        if saved:

            # ------------------------------------------------
            # Update session display name
            # ------------------------------------------------

            session["display_name"] = name

            flash(
                "Student profile saved successfully!",
                "success"
            )

            print("=" * 60)
            print("PROFILE SAVED SUCCESSFULLY")
            print("NAME:", name)
            print("EMAIL:", email)
            print("PHONE:", phone)
            print("GENDER:", gender)
            print("DOB:", date_of_birth)
            print("COLLEGE:", college)
            print("BRANCH:", branch)
            print("GRADUATION:", graduation_year)
            print("=" * 60)

        else:

            flash(
                "Profile could not be saved. Please check users.json permissions.",
                "error"
            )

            print("=" * 60)
            print("PROFILE SAVE FAILED")
            print("=" * 60)

        return redirect(
            url_for("student_profile")
        )

    # ========================================================
    # GET PROFILE PAGE
    # ========================================================

    # Reload after save so the page shows latest values
    user_data = get_current_user_data()

    return render_first_existing(
        [
            "profile.html",
            "student_profile.html"
        ],

        user=user_data,

        profile=user_data,

        user_data=user_data,

        current_user=user_data,

        student=user_data,

        student_profile=user_data,

        skills=user_data,

        academic=user_data,

        activities=user_data,

        username=user_data.get(
            "name",
            get_current_username()
        ),

        display_name=user_data.get(
            "name",
            get_current_username()
        )
    )


# ============================================================
# PROFILE ALIAS
# ============================================================

@app.route("/profile")
@login_required
def profile():

    return redirect(
        url_for("student_profile")
    )


# ============================================================
# PHOTO UPLOAD
# ============================================================

@app.route(
    "/upload-photo",
    methods=["POST"]
)
@app.route(
    "/profile/upload-photo",
    methods=["POST"]
)
@login_required
def upload_photo():

    photo = (
        request.files.get("photo")
        or request.files.get("profile_photo")
        or request.files.get("candidate_photo")
        or request.files.get("image")
    )

    if photo is None or not photo.filename:

        flash(
            "Please select a photo first.",
            "error"
        )

        return redirect(
            url_for("student_profile")
        )

    original_name = secure_filename(
        photo.filename
    )

    if not original_name or "." not in original_name:

        flash(
            "Invalid image file.",
            "error"
        )

        return redirect(
            url_for("student_profile")
        )

    allowed_extensions = {
        "png",
        "jpg",
        "jpeg",
        "webp",
        "gif"
    }

    extension = original_name.rsplit(
        ".",
        1
    )[1].lower()

    if extension not in allowed_extensions:

        flash(
            "Only PNG, JPG, JPEG, WEBP and GIF images are allowed.",
            "error"
        )

        return redirect(
            url_for("student_profile")
        )

    username = secure_filename(
        get_current_username()
    ) or "student"

    filename = (
        f"{username}_profile_"
        f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}."
        f"{extension}"
    )

    filepath = os.path.join(
        UPLOAD_DIR,
        filename
    )

    try:

        photo.save(filepath)

        # Delete older photos
        for old_name in os.listdir(
            UPLOAD_DIR
        ):

            if old_name == filename:
                continue

            if old_name.startswith(
                username + "_profile"
            ):

                old_path = os.path.join(
                    UPLOAD_DIR,
                    old_name
                )

                try:

                    if os.path.isfile(old_path):

                        os.remove(old_path)

                except OSError:

                    pass

        if not save_current_user_data(
            {
                "profile_photo": filename
            }
        ):

            flash(
                "Photo uploaded, but user data could not be saved.",
                "error"
            )

            return redirect(
                url_for("student_profile")
            )

        flash(
            "Profile photo updated successfully!",
            "success"
        )

    except Exception as e:

        print(
            "PHOTO UPLOAD ERROR:",
            e
        )

        flash(
            f"Photo upload failed: {e}",
            "error"
        )

    return redirect(
        url_for("student_profile")
    )


# ============================================================
# UPLOADED FILE
# ============================================================

@app.route(
    "/uploads/<path:filename>"
)
@login_required
def uploaded_file(filename):

    from flask import send_from_directory

    return send_from_directory(
        UPLOAD_DIR,
        filename
    )


# ============================================================
# ACADEMIC DETAILS
# ============================================================

@app.route(
    "/academic-details",
    methods=["GET", "POST"]
)
@login_required
def academic_details():

    user_data = get_current_user_data()

    if request.method == "POST":

        data = {

            "cgpa": request.form.get(
                "cgpa",
                user_data.get(
                    "cgpa",
                    ""
                )
            ),

            "ssc_marks": request.form.get(
                "ssc_marks",
                request.form.get(
                    "SSC_Marks",
                    user_data.get(
                        "ssc_marks",
                        ""
                    )
                )
            ),

            "hsc_marks": request.form.get(
                "hsc_marks",
                request.form.get(
                    "HSC_Marks",
                    user_data.get(
                        "hsc_marks",
                        ""
                    )
                )
            ),

            "backlogs": request.form.get(
                "backlogs",
                user_data.get(
                    "backlogs",
                    "0"
                )
            ),

            "projects": request.form.get(
                "projects",
                user_data.get(
                    "projects",
                    "0"
                )
            ),

            "internships": request.form.get(
                "internships",
                user_data.get(
                    "internships",
                    "0"
                )
            ),

            "certifications": request.form.get(
                "certifications",
                user_data.get(
                    "certifications",
                    "0"
                )
            ),

            "workshops": request.form.get(
                "workshops",
                user_data.get(
                    "workshops",
                    "0"
                )
            )
        }

        if save_current_user_data(data):

            flash(
                "Academic details saved successfully!",
                "success"
            )

        else:

            flash(
                "Academic details could not be saved.",
                "error"
            )

        return redirect(
            url_for("academic_details")
        )

    return render_first_existing(
        [
            "academic.html",
            "academic_details.html"
        ],

        user=user_data,

        profile=user_data,

        academic=user_data,

        academic_data=user_data,

        skills=user_data
    )


# ============================================================
# ACADEMIC ALIAS
# ============================================================

@app.route("/academic")
@login_required
def academic():

    return redirect(
        url_for("academic_details")
    )


# ============================================================
# SKILLS & ACTIVITIES
# ============================================================

@app.route(
    "/skills-activities",
    methods=["GET", "POST"]
)
@login_required
def skills_activities():

    user_data = get_current_user_data()

    if request.method == "POST":

        data = {

            "aptitude": request.form.get(
                "aptitude",
                request.form.get(
                    "AptitudeTestScore",
                    user_data.get(
                        "aptitude",
                        "0"
                    )
                )
            ),

            "soft_skills": request.form.get(
                "soft_skills",
                request.form.get(
                    "SoftSkillsRating",
                    user_data.get(
                        "soft_skills",
                        "0"
                    )
                )
            ),

            "coding_skills": request.form.get(
                "coding_skills",
                user_data.get(
                    "coding_skills",
                    "0"
                )
            ),

            "communication": request.form.get(
                "communication",
                user_data.get(
                    "communication",
                    "0"
                )
            ),

            "extracurricular": request.form.get(
                "extracurricular",
                request.form.get(
                    "ExtracurricularActivities",
                    user_data.get(
                        "extracurricular",
                        "No"
                    )
                )
            ),

            "placement_training": request.form.get(
                "placement_training",
                request.form.get(
                    "PlacementTraining",
                    user_data.get(
                        "placement_training",
                        "No"
                    )
                )
            )
        }

        if save_current_user_data(data):

            flash(
                "Skills & activities updated successfully!",
                "success"
            )

        else:

            flash(
                "Skills & activities could not be saved.",
                "error"
            )

        return redirect(
            url_for("skills_activities")
        )

    return render_first_existing(
        [
            "skills.html",
            "skills_activities.html"
        ],

        user=user_data,

        profile=user_data,

        skills=user_data,

        academic=user_data,

        activities=user_data
    )


# ============================================================
# SKILLS ALIAS
# ============================================================

@app.route("/skills")
@login_required
def skills():

    return redirect(
        url_for("skills_activities")
    )


# ============================================================
# PLACEMENT PREDICTOR
# ============================================================

@app.route("/predictor")
@login_required
def predictor():

    user_data = get_current_user_data()

    return render_template(
        "predictor.html",

        user=user_data,

        profile=user_data,

        skills=user_data,

        academic=user_data
    )


# ============================================================
# YES / NO CONVERTER
# ============================================================

def yes_no_to_number(value):

    value = str(
        value
    ).strip().lower()

    if value in [
        "yes",
        "y",
        "true",
        "1"
    ]:

        return 1

    return 0


# ============================================================
# PLACEMENT PREDICTION
# ============================================================

@app.route(
    "/predict",
    methods=["POST"]
)
@login_required
def predict():

    try:

        if model is None:

            flash(
                "Placement model could not be loaded.",
                "error"
            )

            return redirect(
                url_for("predictor")
            )

        cgpa = float(
            request.form.get(
                "CGPA",
                request.form.get(
                    "cgpa",
                    0
                )
            )
        )

        internships = int(
            float(
                request.form.get(
                    "Internships",
                    request.form.get(
                        "internships",
                        0
                    )
                )
            )
        )

        projects = int(
            float(
                request.form.get(
                    "Projects",
                    request.form.get(
                        "projects",
                        0
                    )
                )
            )
        )

        workshops = int(
            float(
                request.form.get(
                    "Workshops",
                    request.form.get(
                        "workshops",
                        request.form.get(
                            "Certifications",
                            0
                        )
                    )
                )
            )
        )

        aptitude = float(
            request.form.get(
                "AptitudeTestScore",
                request.form.get(
                    "aptitude",
                    0
                )
            )
        )

        soft_skills = float(
            request.form.get(
                "SoftSkillsRating",
                request.form.get(
                    "soft_skills",
                    0
                )
            )
        )

        extracurricular_raw = request.form.get(
            "ExtracurricularActivities",
            request.form.get(
                "extracurricular",
                "No"
            )
        )

        placement_training_raw = request.form.get(
            "PlacementTraining",
            request.form.get(
                "placement_training",
                "No"
            )
        )

        ssc_marks = float(
            request.form.get(
                "SSC_Marks",
                request.form.get(
                    "ssc_marks",
                    0
                )
            )
        )

        hsc_marks = float(
            request.form.get(
                "HSC_Marks",
                request.form.get(
                    "hsc_marks",
                    0
                )
            )
        )

        extracurricular = yes_no_to_number(
            extracurricular_raw
        )

        placement_training = yes_no_to_number(
            placement_training_raw
        )

        data = np.array([[
            cgpa,
            internships,
            projects,
            workshops,
            aptitude,
            soft_skills,
            extracurricular,
            placement_training,
            ssc_marks,
            hsc_marks
        ]])

        print("=" * 60)
        print("MODEL INPUT:")
        print(data)
        print("=" * 60)

        prediction = model.predict(
            data
        )

        result_value = prediction[0]

        probability = None

        try:

            probabilities = model.predict_proba(
                data
            )

            probability = float(
                np.max(
                    probabilities[0]
                ) * 100
            )

        except Exception:

            probability = None

        if probability is None:

            probability = 75.0

        probability = round(
            probability,
            1
        )

        try:

            numeric_result = int(
                result_value
            )

        except Exception:

            numeric_result = 1 if str(
                result_value
            ).lower() in [
                "placed",
                "yes",
                "1",
                "true"
            ] else 0

        if numeric_result == 1:

            placement_status = "PLACED"

            recommendation = (
                "Excellent work! Keep improving "
                "your technical skills, communication "
                "and interview confidence."
            )

            motivation = (
                "Your preparation is creating "
                "opportunities. Keep learning, "
                "keep practicing and believe "
                "in your ability to succeed."
            )

        else:

            placement_status = "NOT PLACED"

            recommendation = (
                "Do not worry. Focus on improving "
                "aptitude, technical skills, communication, "
                "projects and interview preparation."
            )

            motivation = (
                "A prediction is not your destiny. "
                "Every skill you improve increases "
                "your future opportunities. Keep going!"
            )

        result_data = {

            "status": placement_status,

            "prediction": placement_status,

            "probability": probability,

            "cgpa": cgpa,

            "internships": internships,

            "projects": projects,

            "workshops": workshops,

            "aptitude": aptitude,

            "soft_skills": soft_skills,

            "ssc_marks": ssc_marks,

            "hsc_marks": hsc_marks,

            "recommendation": recommendation,

            "motivation": motivation,

            "date": datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            )
        }

        session["latest_result"] = result_data

        user_data = get_current_user_data()

        history = user_data.get(
            "history",
            []
        )

        if not isinstance(
            history,
            list
        ):

            history = []

        history.append(
            result_data
        )

        history = history[-50:]

        save_current_user_data({
            "history": history
        })

        return render_template(
            "result.html",

            user=user_data,

            profile=user_data,

            result=result_data,

            prediction=placement_status,

            status=placement_status,

            probability=probability,

            cgpa=cgpa,

            internships=internships,

            projects=projects,

            workshops=workshops,

            aptitude=aptitude,

            soft_skills=soft_skills,

            ssc_marks=ssc_marks,

            hsc_marks=hsc_marks,

            recommendation=recommendation,

            motivation=motivation
        )

    except Exception as e:

        print("=" * 60)
        print("PREDICTION ERROR:")
        print(e)
        print("=" * 60)

        flash(
            f"Prediction error: {e}",
            "error"
        )

        return redirect(
            url_for("predictor")
        )


# ============================================================
# RESULT
# ============================================================

@app.route("/result")
@login_required
def result():

    return redirect(
        url_for("predictor")
    )


@app.route("/results")
@login_required
def results():

    return redirect(
        url_for("predictor")
    )


# ============================================================
# PLACEMENT TIPS
# ============================================================

@app.route("/placement-tips")
@login_required
def placement_tips():

    user_data = get_current_user_data()

    return render_first_existing(
        [
            "placement_tips.html",
            "tips.html"
        ],

        user=user_data,

        profile=user_data,

        skills=user_data,

        academic=user_data
    )


@app.route("/tips")
@login_required
def tips():

    return redirect(
        url_for("placement_tips")
    )


# ============================================================
# HISTORY
# ============================================================

@app.route("/history")
@login_required
def history():

    user_data = get_current_user_data()

    history_data = user_data.get(
        "history",
        []
    )

    if not isinstance(
        history_data,
        list
    ):

        history_data = []

    history_data = list(
        reversed(
            history_data
        )
    )

    return render_template(
        "history.html",

        history=history_data,

        history_data=history_data,

        user=user_data,

        profile=user_data,

        skills=user_data,

        academic=user_data
    )


# ============================================================
# AI INTERVIEW
# ============================================================

@app.route("/interview")
@login_required
def interview():

    user_data = get_current_user_data()

    return render_template(
        "interview.html",

        user=user_data,

        profile=user_data,

        skills=user_data,

        academic=user_data
    )


# ============================================================
# INTERVIEW FEEDBACK
# ============================================================

@app.route(
    "/feedback",
    methods=["POST"]
)
@login_required
def feedback():

    answer = request.form.get(
        "answer",
        ""
    ).strip()

    if not answer:

        feedback_text = (
            "Please write an answer before submitting."
        )

        score = 0

    else:

        word_count = len(
            answer.split()
        )

        if word_count < 10:

            score = 45

            feedback_text = (
                "Your answer is a little short. "
                "Try explaining your point with "
                "an example and more details."
            )

        elif word_count < 30:

            score = 65

            feedback_text = (
                "Good start! Try adding a real "
                "example and explain your "
                "contribution clearly."
            )

        elif word_count < 60:

            score = 80

            feedback_text = (
                "Strong answer! Your response "
                "has useful detail. Improve it "
                "further by making it more "
                "structured and confident."
            )

        else:

            score = 90

            feedback_text = (
                "Excellent detailed response! "
                "Keep your final interview answer "
                "clear, focused and confident."
            )

    user_data = get_current_user_data()

    return render_template(
        "interview.html",

        user=user_data,

        profile=user_data,

        skills=user_data,

        academic=user_data,

        feedback=feedback_text,

        score=score,

        previous_answer=answer
    )


# ============================================================
# ABOUT
# ============================================================

@app.route("/about")
@login_required
def about():

    user_data = get_current_user_data()

    return render_template(
        "about.html",

        user=user_data,

        profile=user_data,

        skills=user_data,

        academic=user_data
    )


# ============================================================
# CONTACT
# ============================================================

@app.route("/contact")
@login_required
def contact():

    user_data = get_current_user_data()

    return render_template(
        "contact.html",

        user=user_data,

        profile=user_data,

        skills=user_data,

        academic=user_data
    )


# ============================================================
# DOWNLOAD PDF REPORT
# ============================================================

@app.route("/download_report")
@login_required
def download_report():

    result_data = session.get(
        "latest_result"
    )

    if not result_data:

        user_data = get_current_user_data()

        history = user_data.get(
            "history",
            []
        )

        if history:

            result_data = history[-1]

    if not result_data:

        flash(
            "Please complete a placement prediction first.",
            "error"
        )

        return redirect(
            url_for("predictor")
        )

    file_path = os.path.join(
        BASE_DIR,
        "placement_report.pdf"
    )

    document = SimpleDocTemplate(
        file_path,

        pagesize=A4,

        rightMargin=50,

        leftMargin=50,

        topMargin=50,

        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]

    heading_style = styles["Heading2"]

    normal_style = styles["BodyText"]

    story = []

    story.append(
        Paragraph(
            "AI CAMPUS PLACEMENT PRO",
            title_style
        )
    )

    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            "Student Placement Prediction Report",
            heading_style
        )
    )

    story.append(
        Spacer(1, 15)
    )

    user_data = get_current_user_data()

    story.append(
        Paragraph(
            f"Student: {user_data.get('name', get_current_username())}",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"Team: {TEAM_NAME}",
            normal_style
        )
    )

    story.append(
        Spacer(1, 15)
    )

    story.append(
        Paragraph(
            f"Prediction: "
            f"{result_data.get('status', 'N/A')}",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"Placement Probability: "
            f"{result_data.get('probability', 0)}%",
            normal_style
        )
    )

    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            "Academic & Professional Profile",
            heading_style
        )
    )

    story.append(
        Paragraph(
            f"CGPA: "
            f"{result_data.get('cgpa', 0)}",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"Internships: "
            f"{result_data.get('internships', 0)}",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"Projects: "
            f"{result_data.get('projects', 0)}",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"Workshops / Certifications: "
            f"{result_data.get('workshops', 0)}",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"Aptitude Score: "
            f"{result_data.get('aptitude', 0)}",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"Soft Skills Rating: "
            f"{result_data.get('soft_skills', 0)}",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"SSC Marks: "
            f"{result_data.get('ssc_marks', 0)}",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"HSC Marks: "
            f"{result_data.get('hsc_marks', 0)}",
            normal_style
        )
    )

    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            "Personalized Recommendation",
            heading_style
        )
    )

    story.append(
        Paragraph(
            result_data.get(
                "recommendation",
                ""
            ),
            normal_style
        )
    )

    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            "Motivational Message",
            heading_style
        )
    )

    story.append(
        Paragraph(
            result_data.get(
                "motivation",
                ""
            ),
            normal_style
        )
    )

    story.append(
        Spacer(1, 30)
    )

    story.append(
        Paragraph(
            "Best Wishes from SECRET CIRCLE 🔴",
            heading_style
        )
    )

    document.build(
        story
    )

    return send_file(
        file_path,

        as_attachment=True,

        download_name="AI_Campus_Placement_Report.pdf"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been securely logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# 404 ERROR
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    if "user" in session:

        return redirect(
            url_for("dashboard")
        )

    return redirect(
        url_for("login")
    )


# ============================================================
# 500 ERROR
# ============================================================

@app.errorhandler(500)
def internal_server_error(error):

    print("=" * 60)

    print(
        "INTERNAL SERVER ERROR:"
    )

    print(error)

    print("=" * 60)

    return (
        "<h2>AI Campus Placement Pro</h2>"
        "<p>An internal server error occurred.</p>"
        "<p>Please check the VS Code terminal.</p>"
    ), 500


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    print()

    print("=" * 60)

    print(
        "       AI CAMPUS PLACEMENT PRO"
    )

    print("=" * 60)

    print(
        f"       TEAM: {TEAM_NAME}"
    )

    print("=" * 60)

    print("Login      : /login")

    print("Register   : /register")

    print("Dashboard  : /dashboard")

    print("Profile    : /profile")

    print("Academic   : /academic")

    print("Skills     : /skills")

    print("Predictor  : /predictor")

    print("Results    : /results")

    print("History    : /history")

    print("Interview  : /interview")

    print("About      : /about")

    print("Contact    : /contact")

    print("Logout     : /logout")

    print("=" * 60)

    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )