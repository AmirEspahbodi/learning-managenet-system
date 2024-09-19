# Education Management System

This project is a comprehensive **Education Management System** designed to manage courses, quizzes, exams, and user roles. It is built using **Django** and **Django REST Framework** for the backend.

## Features

### 1. Course Management System
- Manage courses offered each semester.
- Each course can have multiple class groups per semester.
- Assign instructors to courses.
- Students can register for courses and pay tuition fees or apply for scholarships with instructor approval.

### 2. Quiz & Exam System
- Supports various types of questions, including:
  - Text-based answers.
  - File-based answers.
  - Multiple choice questions.
- Instructors can review answers, assign grades, and provide recommendations or feedback to students.

### 3. User Roles
The system has four types of users, each with different access levels:
- **Admins**: Manage the entire system.
- **Instructors**: Handle course management and grade students.
- **Students**: Enroll in courses, take quizzes, and receive grades.
- **Supervisors**: Oversee course operations.

### 4. Token Management System
- Sets a maximum number of tokens each user can have (configurable).
- Logs user login activities.
- Sends notifications to the user’s email on new logins based on predefined settings.

## Running the Project

To run the project, use **Docker Compose**. Make sure Docker is installed on your machine.

Run the following command:

```bash
docker compose up -d
```


### **under refactoring**  
### **checkout old branch**  

[<img src="https://run.pstmn.io/button.svg" alt="Run In Postman" style="width: 128px; height: 32px;">](https://app.getpostman.com/run-collection/29876617-6d44ef61-1af6-4e24-820a-8f308d22ffc7?action=collection%2Ffork&source=rip_markdown&collection-url=entityId%3D29876617-6d44ef61-1af6-4e24-820a-8f308d22ffc7%26entityType%3Dcollection%26workspaceId%3Dae45c6b3-57fc-4195-9eef-fad06e1609ec)
