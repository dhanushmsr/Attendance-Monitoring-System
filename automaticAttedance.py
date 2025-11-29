import tkinter as tk
from tkinter import *
import os, cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.ttk as tkk
import tkinter.font as font

def text_to_speech(text):
    print(f"[Speech Output]: {text}")

# ------------------------ FIX #1 : ABSOLUTE PATHS ----------------------------
BASE_DIR = os.getcwd()

haarcasecade_path = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")
trainimagelabel_path = os.path.join(BASE_DIR, "TrainingImageLabel", "Trainner.yml")
trainimage_path = os.path.join(BASE_DIR, "TrainingImage")
studentdetail_path = os.path.join(BASE_DIR, "StudentDetails", "studentdetails.csv")
attendance_path = os.path.join(BASE_DIR, "Attendance")

# ------------------------ FIX #2 : VALIDATE OPENCV VERSION ------------------
if not hasattr(cv2, "face"):
    raise Exception(
        "\nERROR: You installed the WRONG OpenCV!\n"
        "Install this version:\n"
        "pip install opencv-contrib-python==4.7.0.72\n"
    )

# ============================================================================

def subjectChoose(text_to_speech):

    def FillAttendance():
        Subject = tx.get().strip()
        if not Subject:
            text_to_speech("Please enter the subject name!")
            return

        # ------------------------ FIX #3 : CHECK MODEL FILE ------------------
        if not os.path.exists(trainimagelabel_path):
            Notifica.config(text="Training model not found!", bg="red", fg="white")
            text_to_speech("Training model missing. Train again.")
            return

        # ------------------------ FIX #4 : CHECK CSV FILE --------------------
        if not os.path.exists(studentdetail_path):
            Notifica.config(text="StudentDetails CSV missing!", bg="red", fg="white")
            text_to_speech("Student details missing.")
            return

        # ------------------------ FIX #5 : CHECK HAAR FILE -------------------
        if not os.path.exists(haarcasecade_path):
            Notifica.config(text="Haarcascade XML missing!", bg="red", fg="white")
            text_to_speech("Face detection file missing.")
            return

        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read(trainimagelabel_path)

            face_cascade = cv2.CascadeClassifier(haarcasecade_path)

            df = pd.read_csv(studentdetail_path)

            # --------------------- FIX #6 : CAMERA CHECK ----------------------
            cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                text_to_speech("Camera could not be opened! Check permissions.")
                return

            font_style = cv2.FONT_HERSHEY_SIMPLEX
            attendance = pd.DataFrame(columns=["Enrollment", "Name"])

            timeout = time.time() + 20  # 20 seconds

            while True:
                ret, frame = cam.read()
                if not ret:
                    text_to_speech("Camera frame error!")
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.2, 5)

                for (x, y, w, h) in faces:
                    try:
                        Id, conf = recognizer.predict(gray[y:y+h, x:x+w])
                    except:
                        continue

                    if conf < 70:
                        row = df.loc[df["Enrollment"] == Id]

                        if row.empty:
                            cv2.putText(frame, "UnknownID in CSV", (x, y-10), font_style, 1, (0, 0, 255), 2)
                        else:
                            name = row["Name"].values[0]
                            attendance.loc[len(attendance)] = [Id, name]

                            cv2.putText(frame, f"{Id}-{name}", (x, y-10), font_style, 1, (255, 255, 0), 2)
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    else:
                        cv2.putText(frame, "Unknown", (x, y-10), font_style, 1, (0, 0, 255), 2)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

                attendance.drop_duplicates("Enrollment", inplace=True)

                cv2.imshow("Filling Attendance...", frame)

                if cv2.waitKey(30) & 0xFF == 27:
                    break

                if time.time() > timeout:
                    break

            cam.release()
            cv2.destroyAllWindows()

            # ------------------------- FIX #7 : EMPTY ATTENDANCE CHECK ---------
            if attendance.empty:
                text_to_speech("No known face detected.")
                return

            ts = time.time()
            date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H-%M-%S")

            attendance[date] = 1

            folder = os.path.join(attendance_path, Subject)
            os.makedirs(folder, exist_ok=True)

            file_path = os.path.join(folder, f"{Subject}_{date}_{timeStamp}.csv")
            attendance.to_csv(file_path, index=False)

            Notifica.config(text="Attendance Saved Successfully!", bg="green", fg="white")

            # -------------------------- DISPLAY ATTENDANCE ---------------------
            root = tk.Toplevel(subject)
            root.title("Attendance Records")
            root.configure(bg="black")

            with open(file_path, "r") as f:
                reader = csv.reader(f)
                for r, row in enumerate(reader):
                    for c, col in enumerate(row):
                        lbl = tk.Label(root, text=col, font=("times", 15, "bold"),
                                       fg="yellow", bg="black", width=15, relief=RIDGE)
                        lbl.grid(row=r, column=c)

            root.mainloop()

        except Exception as e:
            text_to_speech(f"ERROR: {e}")
            print("FULL ERROR:", e)
            cv2.destroyAllWindows()

    # ========================================================================
    # GUI WINDOW
    subject = Tk()
    subject.title("Subject Selection")
    subject.geometry("580x320")
    subject.resizable(0, 0)
    subject.configure(background="black")

    Notifica = tk.Label(subject, text="", bg="black", fg="yellow",
                        font=("times", 15, "bold"))
    Notifica.place(x=20, y=250)

    def Attf():
        sub = tx.get().strip()
        if not sub:
            text_to_speech("Enter subject name!")
            return

        folder = os.path.join(attendance_path, sub)
        if os.path.isdir(folder):
            os.startfile(folder)
        else:
            text_to_speech("No attendance folder found for this subject.")

    tk.Label(subject, text="Enter Subject", fg="yellow", bg="black",
             font=("times", 15), relief=RIDGE).place(x=50, y=100)

    tx = tk.Entry(subject, width=15, fg="yellow", bg="black",
                  font=("times", 28, "bold"))
    tx.place(x=190, y=100)

    tk.Button(subject, text="Fill Attendance", command=FillAttendance,
              fg="yellow", bg="black", font=("times", 15), relief=RIDGE).place(x=195, y=170)

    tk.Button(subject, text="Check Sheets", command=Attf,
              fg="yellow", bg="black", font=("times", 15), relief=RIDGE).place(x=360, y=170)

    subject.mainloop()
