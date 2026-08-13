# STUDENT PRODUCTIVITY TRACKER - VERSION 2
# A simple menu-driven program using lists, dictionaries and file handling.

import os
from datetime import datetime

TASK_FILE = "tasks.txt"
LOG_FILE = "productivity_log.txt"

# We use "|" as a separator instead of "," because task names or subjects
# might themselves contain a comma (e.g. "Math, Physics").
SEP = "|"


# ---------------------------------------------------------
# TASK MANAGER FUNCTIONS
# ---------------------------------------------------------

def load_tasks():
    tasks = []
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r") as file:
            for line in file:
                line = line.strip()
                if line == "":
                    continue
                parts = line.split(SEP)
                if len(parts) == 3:
                    task = {"subject": parts[0], "title": parts[1], "status": parts[2]}
                    tasks.append(task)
        # file is automatically closed here, even if an error happened above
    return tasks


def save_tasks(tasks):
    with open(TASK_FILE, "w") as file:
        for task in tasks:
            file.write(task["subject"] + SEP + task["title"] + SEP + task["status"] + "\n")


def add_task(tasks):
    subject = input("Enter subject: ")
    title = input("Enter task: ")
    task = {"subject": subject, "title": title, "status": "Pending"}
    tasks.append(task)
    save_tasks(tasks)
    print("Task added successfully!\n")


def show_tasks(tasks):
    if len(tasks) == 0:
        print("No tasks found.\n")
        return
    print("\nID\tSubject\t\tTask\t\tStatus")
    print("-" * 45)
    for i in range(len(tasks)):
        t = tasks[i]
        print(str(i + 1) + "\t" + t["subject"] + "\t\t" + t["title"] + "\t\t" + t["status"])
    print()


# Get a valid task ID from the user, or None if input is invalid
def get_valid_task_id(tasks):
    text = input("Enter task ID: ")
    if not text.isdigit():
        print("Invalid input! Please enter a number.\n")
        return None
    num = int(text)
    if num < 1 or num > len(tasks):
        print("Invalid task ID.\n")
        return None
    return num


def complete_task(tasks):
    show_tasks(tasks)
    if len(tasks) == 0:
        return
    num = get_valid_task_id(tasks)
    if num is None:
        return
    tasks[num - 1]["status"] = "Done"
    save_tasks(tasks)
    print("Task marked as done!\n")


def delete_task(tasks):
    show_tasks(tasks)
    if len(tasks) == 0:
        return
    num = get_valid_task_id(tasks)
    if num is None:
        return
    removed = tasks.pop(num - 1)
    save_tasks(tasks)
    print("Deleted:", removed["title"], "\n")


def show_summary(tasks):
    done = 0
    pending = 0
    for t in tasks:
        if t["status"] == "Done":
            done = done + 1
        else:
            pending = pending + 1
    print("\nTotal tasks:", len(tasks))
    print("Completed:", done)
    print("Pending:", pending, "\n")


# ---------------------------------------------------------
# HELPER FUNCTION FOR SAFE NUMBER INPUT
# ---------------------------------------------------------

# Keeps asking until the user enters a valid non-negative number.
# allow_decimal lets us accept values like 6.5 hours.
def get_valid_number(prompt, allow_decimal=True):
    while True:
        text = input(prompt)
        try:
            if allow_decimal:
                value = float(text)
            else:
                value = int(text)
            if value < 0:
                print("Please enter a number that is 0 or more.")
                continue
            return value
        except ValueError:
            print("Invalid input! Please enter a valid number.")


# ---------------------------------------------------------
# PRODUCTIVITY TRACKER FUNCTIONS
# ---------------------------------------------------------

# Calculate a simple productivity score out of 100 based on daily activity.
# We use min() to CAP each activity, so extra hours beyond a healthy limit
# don't keep adding more score. A day only has 24 hours, so unrealistic
# entries (like 15 hours of study) should not be rewarded endlessly.
def calculate_score(study, coding, sleep, assignments):
    # Cap each activity at a sensible daily maximum before scoring
    capped_study = min(study, 6)          # beyond 6 hrs study, no extra points
    capped_coding = min(coding, 4)        # beyond 4 hrs coding, no extra points
    capped_assignments = min(assignments, 5)  # beyond 5 assignments, no extra points

    score = (capped_study * 5) + (capped_coding * 5) + (capped_assignments * 10)

    # Bonus for healthy sleep, penalty for too little sleep
    if sleep >= 7:
        score = score + 10
    elif sleep < 5:
        score = score - 10

    # Score should stay between 0 and 100
    if score > 100:
        score = 100
    if score < 0:
        score = 0

    return int(score)


# Keeps asking until the user enters a real, correctly formatted date.
# datetime.strptime() raises a ValueError if the text doesn't match the
# format, so we use that to reject things like "hello" or "15/08/26".
def get_valid_date():
    while True:
        text = input("Enter date (YYYY-MM-DD, e.g. 2024-01-15): ")
        try:
            datetime.strptime(text, "%Y-%m-%d")
            return text
        except ValueError:
            print("Invalid date! Please use the YYYY-MM-DD format.")


def log_productivity():
    print("\n--- Log Today's Productivity ---")
    day = get_valid_date()
    study = get_valid_number("Study hours: ")
    coding = get_valid_number("Coding hours: ")
    sleep = get_valid_number("Sleep hours: ")
    assignments = get_valid_number("Assignments completed: ", allow_decimal=False)

    # A day only has 24 hours, so warn if the entries don't make sense
    if study + coding + sleep > 24:
        print("Warning: study + coding + sleep hours add up to more than 24!")
        print("Your entry will still be saved, but please double check it.\n")

    score = calculate_score(study, coding, sleep, assignments)

    line = day + SEP + str(study) + SEP + str(coding) + SEP + str(sleep) + SEP + str(assignments) + SEP + str(score)
    with open(LOG_FILE, "a") as file:
        file.write(line + "\n")

    print("Logged successfully! Your productivity score for the day:", score, "/ 100\n")


def load_logs():
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as file:
            for line in file:
                line = line.strip()
                if line == "":
                    continue
                parts = line.split(SEP)
                if len(parts) == 6:
                    entry = {
                        "date": parts[0],
                        "study": float(parts[1]),
                        "coding": float(parts[2]),
                        "sleep": float(parts[3]),
                        "assignments": int(float(parts[4])),
                        "score": int(parts[5]),
                    }
                    logs.append(entry)
        # file is automatically closed here, even if an error happened above
    return logs


def show_productivity_report():
    logs = load_logs()
    if len(logs) == 0:
        print("No productivity data logged yet.\n")
        return

    print("\nDate\t\tStudy\tCoding\tSleep\tAssignments\tScore")
    print("-" * 65)
    total_score = 0
    for entry in logs:
        print(entry["date"] + "\t" + str(entry["study"]) + "\t" + str(entry["coding"]) + "\t" +
              str(entry["sleep"]) + "\t" + str(entry["assignments"]) + "\t\t" + str(entry["score"]))
        total_score = total_score + entry["score"]

    average_score = total_score / len(logs)
    print("-" * 65)
    print("Average productivity score:", round(average_score, 2), "/ 100\n")


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

def main():
    tasks = load_tasks()

    while True:
        print("===== STUDENT PRODUCTIVITY TRACKER =====")
        print("1. Add Task")
        print("2. Show All Tasks")
        print("3. Mark Task as Done")
        print("4. Delete Task")
        print("5. Show Task Summary")
        print("6. Log Today's Productivity (Study/Coding/Sleep/Assignments)")
        print("7. Show Productivity Report")
        print("8. Exit")

        choice = input("Enter your choice (1-8): ")

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            show_tasks(tasks)
        elif choice == "3":
            complete_task(tasks)
        elif choice == "4":
            delete_task(tasks)
        elif choice == "5":
            show_summary(tasks)
        elif choice == "6":
            log_productivity()
        elif choice == "7":
            show_productivity_report()
        elif choice == "8":
            print("Goodbye! Keep studying well.")
            break
        else:
            print("Invalid choice. Try again.\n")


# Call the main function to run the program
main()
