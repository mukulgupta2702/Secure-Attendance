
# Secure-Attendance
Engage 2022 Face Recognition Project:\
This is a browser based webite of Attendance system using Face Recognition. User can simply create an account and then add members of his organisation using a single picture.

## Demo

https://drive.google.com/drive/folders/1ugAVsy52aAj3f0CXNI87wSpCy0XjV5w2?usp=sharing


## Features

- Multiple Users (admins) can be created
- Alerts are generated if unknown person is trying to mark the attendance 
- Time Gap between two consecutive attendance of members can be customised for each admin
- Face recognition decision takes place on the mode of 5 consecutive frame decision
- Email Verification
- Password reset via email 
- passwords stored in database are hashed 
- Details of each member and admin can be updated 

## Run Locally

Clone the project

```bash
  git clone https://github.com/mukulgupta2702/Secure-Attendance.git
```

Install dependencies

```bash
  pip install -r .\requirements.txt  
```

Start the server

```bash
  python .\app.py
```


## Screenshots

![Home Page](screenshots\home.png)
![Login Page](screenshots\login_page.png)
![Registration Page](screenshots\registration_page.png)
![Attendance Page](screenshots\Attendance_page.png)
![Alerts Page]([screenshots\Alerts.png](https://github.com/mukulgupta2702/Secure-Attendance/blob/main/screenshots/Alerts.png))
![Account Page](screenshots\user_account.png)
![Update Account Page](screenshots\update_account.png)

