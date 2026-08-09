from flask import Flask, render_template, request, send_file
import joblib
import numpy as np
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER


# --------------------------------------------------
# FLASK APPLICATION
# --------------------------------------------------

# Your HTML files are in the main GitHub folder,
# so template_folder="." tells Flask to look here.
app = Flask(__name__, template_folder=".")


# --------------------------------------------------
# LOAD MACHINE LEARNING MODEL
# --------------------------------------------------

model = joblib.load("placement_model.pkl")

# Store latest prediction for PDF
report_data = {}


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("home.html")


# --------------------------------------------------
# PREDICTOR
# --------------------------------------------------

@app.route("/predictor")
def predictor():
    return render_template("predictor.html")


# --------------------------------------------------
# ABOUT
# --------------------------------------------------

@app.route("/about")
def about():
    return render_template("about.html")


# --------------------------------------------------
# CONTACT
# --------------------------------------------------

@app.route("/contact")
def contact():
    return render_template("contact.html")


# --------------------------------------------------
# INTERVIEW PAGE
# --------------------------------------------------

@app.route("/interview")
def interview():
    return render_template("interview.html")


# --------------------------------------------------
# AI INTERVIEW FEEDBACK
# --------------------------------------------------

@app.route("/feedback", methods=["POST"])
def feedback():

    answer = request.form["answer"]

    if len(answer) < 50:

        feedback = """
Rating: 2 / 5

Your answer is too short.

Mention:
- Education
- Technical Skills
- Projects
- Career Goal
"""

    elif "python" in answer.lower() or "project" in answer.lower():

        feedback = """
Rating: 4 / 5

Excellent!

You mentioned your skills and projects.

Try speaking confidently and explain your achievements.
"""

    else:

        feedback = """
Rating: 3 / 5

Good Answer.

Include:
- Internships
- Technical Skills
- Strengths
- Career Objective
"""

    return render_template(
        "feedback.html",
        answer=answer,
        feedback=feedback
    )


# --------------------------------------------------
# PLACEMENT PREDICTION
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    global report_data

    # Get student information from form

    cgpa = float(request.form["CGPA"])
    internships = int(request.form["Internships"])
    projects = int(request.form["Projects"])
    workshops = int(request.form["Workshops"])
    aptitude = float(request.form["AptitudeTestScore"])
    softskills = float(request.form["SoftSkillsRating"])
    extracurricular = int(request.form["ExtracurricularActivities"])
    training = int(request.form["PlacementTraining"])
    ssc = float(request.form["SSC_Marks"])
    hsc = float(request.form["HSC_Marks"])

    # Arrange input in the same order
    # used while training the ML model

    data = np.array([[
        cgpa,
        internships,
        projects,
        workshops,
        aptitude,
        softskills,
        extracurricular,
        training,
        ssc,
        hsc
    ]])

    # Machine Learning Prediction

    prediction = model.predict(data)

    # Placement probability

    try:
        probability = round(
            max(model.predict_proba(data)[0]) * 100
        )
    except Exception:
        probability = 90

    # Prediction result

    if prediction[0] == 1:
        result = "Congratulations! You are Likely to be Placed"
    else:
        result = "You are Less Likely to be Placed"


    # --------------------------------------------------
    # CGPA RATING
    # --------------------------------------------------

    if cgpa >= 9:

        cgpa_rating = "Excellent"

    elif cgpa >= 8:

        cgpa_rating = "Very Good"

    elif cgpa >= 7:

        cgpa_rating = "Good"

    else:

        cgpa_rating = "Needs Improvement"


    # --------------------------------------------------
    # PROJECT RATING
    # --------------------------------------------------

    if projects >= 4:

        project_rating = "Excellent"

    elif projects >= 2:

        project_rating = "Good"

    else:

        project_rating = "Needs Improvement"


    # --------------------------------------------------
    # INTERNSHIP RATING
    # --------------------------------------------------

    if internships >= 2:

        internship_rating = "Excellent"

    elif internships == 1:

        internship_rating = "Good"

    else:

        internship_rating = "Needs Improvement"


    # --------------------------------------------------
    # AI RECOMMENDATIONS
    # --------------------------------------------------

    recommendations = []

    if cgpa < 8:

        recommendations.append(
            "Improve your CGPA."
        )

    if internships == 0:

        recommendations.append(
            "Complete at least one internship."
        )

    if projects < 3:

        recommendations.append(
            "Build more AI / Python projects."
        )

    if aptitude < 70:

        recommendations.append(
            "Practice aptitude questions daily."
        )

    if softskills < 7:

        recommendations.append(
            "Improve your communication skills."
        )

    if len(recommendations) == 0:

        recommendations.append(
            "Excellent profile. Apply to top companies."
        )


    # --------------------------------------------------
    # SAVE REPORT DATA
    # --------------------------------------------------

    report_data = {

        "prediction": result,

        "probability": probability,

        "cgpa": cgpa,

        "projects": projects,

        "internships": internships,

        "cgpa_rating": cgpa_rating,

        "project_rating": project_rating,

        "internship_rating": internship_rating,

        "recommendations": recommendations

    }


    # --------------------------------------------------
    # RESULT PAGE
    # --------------------------------------------------

    return render_template(

        "result.html",

        prediction=result,

        probability=probability,

        cgpa=cgpa,

        projects=projects,

        internships=internships,

        cgpa_rating=cgpa_rating,

        project_rating=project_rating,

        internship_rating=internship_rating,

        recommendations=recommendations

    )


# --------------------------------------------------
# DOWNLOAD PDF REPORT
# --------------------------------------------------

@app.route("/download")
def download():

    global report_data

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    title = styles["Title"]

    title.alignment = TA_CENTER

    story = []


    # Title

    story.append(
        Paragraph(
            "AI CAMPUS PLACEMENT REPORT",
            title
        )
    )

    story.append(
        Spacer(1, 20)
    )


    # Prediction

    story.append(
        Paragraph(
            "<b>Prediction Result</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            report_data["prediction"],
            styles["BodyText"]
        )
    )

    story.append(
        Spacer(1, 12)
    )


    # Probability

    story.append(
        Paragraph(
            "<b>Placement Probability</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            str(report_data["probability"]) + "%",
            styles["BodyText"]
        )
    )

    story.append(
        Spacer(1, 12)
    )


    # Student Details

    story.append(
        Paragraph(
            "<b>Student Details</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            f"CGPA: {report_data['cgpa']}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"Projects: {report_data['projects']}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"Internships: {report_data['internships']}",
            styles["BodyText"]
        )
    )

    story.append(
        Spacer(1, 12)
    )


    # Skill Ratings

    story.append(
        Paragraph(
            "<b>Skill Ratings</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            "CGPA Rating: " + report_data["cgpa_rating"],
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            "Project Rating: " + report_data["project_rating"],
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            "Internship Rating: " + report_data["internship_rating"],
            styles["BodyText"]
        )
    )

    story.append(
        Spacer(1, 12)
    )


    # Recommendations

    story.append(
        Paragraph(
            "<b>AI Recommendations</b>",
            styles["Heading2"]
        )
    )

    for item in report_data["recommendations"]:

        story.append(
            Paragraph(
                "- " + item,
                styles["BodyText"]
            )
        )


    story.append(
        Spacer(1, 20)
    )


    # Footer

    story.append(
        Paragraph(
            "Generated by AI Campus Placement Pro",
            styles["Italic"]
        )
    )


    # Build PDF

    doc.build(story)

    buffer.seek(0)


    return send_file(

        buffer,

        as_attachment=True,

        download_name="AI_Placement_Report.pdf",

        mimetype="application/pdf"

    )


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    app.run(debug=True)
