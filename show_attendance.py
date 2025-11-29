import pandas as pd
from glob import glob
import os
import tkinter
import csv
import tkinter as tk
from tkinter import *

def subjectchoose(text_to_speech):
    
    def calculate_attendance():
        Subject = tx.get().strip() # Use strip() to remove accidental spaces
        
        if not Subject:
            t = 'Please enter the subject name.'
            text_to_speech(t)
            return
    
        # Use os.path.join for reliable path construction
        search_path = os.path.join("Attendance", Subject, f"{Subject}*.csv")
        
        # 1. Search for all subject attendance files
        filenames = glob(search_path)
        
        # --- FIX for IndexError: list index out of range ---
        if not filenames:
            t = f"Error: No daily attendance sheets found for subject '{Subject}'."
            text_to_speech(t)
            return
            
        # 2. Read and merge all CSV files
        try:
            df = [pd.read_csv(f) for f in filenames]
            
            # This is safe because 'filenames' is guaranteed to not be empty
            newdf = df[0] 
            
            for i in range(1, len(df)):
                # Use merge on a common key (assuming 'Enrollment' or 'Id' exists)
                # If no key is specified, it merges on all common columns
                newdf = newdf.merge(df[i], how="outer")
        except Exception as e:
            t = f"Error reading or merging files. Ensure your CSVs have a consistent format. Details: {e}"
            text_to_speech(t)
            return

        # 3. Calculate Attendance Percentage
        newdf.fillna(0, inplace=True)
        # Calculate percentage using mean of columns 2 onwards
        # The slice [i, 2:-1] excludes the first two identifying columns and the last, soon-to-be-calculated column.
        for i in range(len(newdf)):
            attendance_mean = newdf.iloc[i, 2:].mean() # Adjusted slice to ensure it grabs all attendance columns
            
            # Use .loc for setting value to avoid SettingWithCopyWarning
            newdf.loc[i, "Attendance"] = str(int(round(attendance_mean * 100))) + '%'
            
        
        # 4. Save the merged attendance sheet
        output_file_path = os.path.join("Attendance", Subject, "attendance.csv")
        newdf.to_csv(output_file_path, index=False)

        # 5. Display the attendance in a Tkinter window
        root = tkinter.Tk()
        root.title("Attendance of "+Subject)
        root.configure(background="black")
        
        with open(output_file_path) as file:
            reader = csv.reader(file)
            r = 0
            for col in reader:
                c = 0
                for row in col:
                    label = tkinter.Label(
                        root,
                        width=10,
                        height=1,
                        fg="yellow",
                        font=("times", 15, " bold "),
                        bg="black",
                        text=row,
                        relief=tkinter.RIDGE,
                    )
                    label.grid(row=r, column=c)
                    c += 1
                r += 1
        root.mainloop()

    # --- Attf function for "Check Sheets" button ---
    def Attf():
        sub = tx.get().strip() # Use strip()
        
        if not sub:
            t = "Please enter the subject name!!!"
            text_to_speech(t)
            return
        
        # --- FIX for FileNotFoundError: Check folder existence and use os.path.join ---
        folder_path = os.path.join("Attendance", sub)
        
        if os.path.isdir(folder_path):
            try:
                # Open the directory/folder
                os.startfile(folder_path)
            except Exception as e:
                # Catch potential errors if the OS fails to open the folder
                t = f"Error opening folder: {e}. Check OS permissions."
                text_to_speech(t)
        else:
            t = f"Error: Subject folder '{sub}' not found inside 'Attendance' directory. Did you register any students for this subject?"
            text_to_speech(t)


    # --- Tkinter GUI Setup (Remains the same) ---
    subject = Tk()
    subject.title("Subject...")
    subject.geometry("580x320")
    subject.resizable(0, 0)
    subject.configure(background="black")
    
    titl = tk.Label(subject, bg="black", relief=RIDGE, bd=10, font=("arial", 30))
    titl.pack(fill=X)
    
    titl = tk.Label(
        subject,
        text="Which Subject of Attendance?",
        bg="black",
        fg="green",
        font=("arial", 25),
    )
    titl.place(x=100, y=12)

    attf = tk.Button(
        subject,
        text="Check Sheets",
        command=Attf,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=10,
        relief=RIDGE,
    )
    attf.place(x=360, y=170)

    sub_label = tk.Label( # Changed variable name from 'sub' to 'sub_label' to avoid conflict
        subject,
        text="Enter Subject",
        width=10,
        height=2,
        bg="black",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("times new roman", 15),
    )
    sub_label.place(x=50, y=100)

    tx = tk.Entry(
        subject,
        width=15,
        bd=5,
        bg="black",
        fg="yellow",
        relief=RIDGE,
        font=("times", 30, "bold"),
    )
    tx.place(x=190, y=100)

    fill_a = tk.Button(
        subject,
        text="View Attendance",
        command=calculate_attendance,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=12,
        relief=RIDGE,
    )
    fill_a.place(x=195, y=170)
    subject.mainloop()