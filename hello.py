from flask import Flask,flash, session, redirect, url_for, escape, request
from flask.templating import render_template
import os
from os.path import join, dirname,realpath
import pandas as pd
import django
from django.http import JsonResponse
import mysql.connector
from flask import  json, jsonify
from flask_mysqldb import MySQL,MySQLdb
app = Flask(__name__)
app.secret_key = "Atharv Bhagya"

db= mysql.connector.connect(
    host="localhost",
    user="root",
    password="aaa",
    database="admins",
 
)
dbcur= db.cursor()




UPLOAD_FOLDER='static/files'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER


def abs_time_calc(a,b):
    if b=='FALL':
        return float(a)+0.5
    elif b=='SPRING':
        return float(a)


@app.route("/")
def index():
    return render_template('main_page.html')

@app.route('/filter')
def filter():
    return render_template('filter.html') 


@app.route('/table_menu')
def table_menu():
    return render_template('table_menu.html')


 ## department table
@app.route('/table_menu/department')
def department_table():
    dbcur.execute("select * from department")
    rows=dbcur.fetchall()
    return render_template('./show_tables/department_table.html',rows=rows)

## course table    
@app.route('/table_menu/course')
def course_table():
    dbcur.execute("select * from course")
    rows=dbcur.fetchall()
    return render_template('./show_tables/course_table.html',rows=rows)
 ## faculty table   
@app.route('/table_menu/faculty')
def faculty_table():
    dbcur.execute("select * from faculty")
    rows=dbcur.fetchall()
    return render_template('./show_tables/faculty_table.html',rows=rows)
 ## faculty with course table   
@app.route('/table_menu/faculty--with--course')
def faculty_with_course_table():
    dbcur.execute("select course_ID,faculty_ID,year,semester,No_students from faculty_with_course")
    rows=dbcur.fetchall()
    return render_template('./show_tables/faculty_with_course_table.html',rows=rows)
 ## timetable   
@app.route('/table_menu/timetable')
def timetable_table():
    dbcur.execute("select * from timetable")
    rows=dbcur.fetchall()
    return render_template('./show_tables/timetable_table.html',rows=rows)




@app.route('/getcou/<string:department>',methods=['GET'])

def getcou(department):
    dbcur.execute("select course_ID,course_title from course where department_name=(%s)",[department])
    course_rows=dbcur.fetchall()
    couArray=[]
    for row in course_rows:
        couObj={
            'course_id':row[0],
            'course_title': row[1]
        }
        couArray.append(couObj)
    return jsonify({'course_list': couArray})






@app.route("/filter/faculty", methods=['POST','GET'])
def filter_faculty():
    query='select department_name from department'
    dbcur.execute(query)
    row_dep=dbcur.fetchall()
    if request.method=='POST':
      entry1= request.form['department_name']
      entry2= request.form['course_ID']
      if entry1!='None' and entry2!='None':
       
          query2=("select department.department_name,faculty.faculty_ID,faculty.faculty_name,course.course_ID,course.course_title  \
              FROM department join course on department.department_name=course.department_name \
                  join faculty_with_course on faculty_with_course.course_ID=course.course_ID \
                      join faculty on faculty.faculty_ID= faculty_with_course.faculty_ID \
                          where department.department_name=(%s) and course.course_ID=(%s) ")
          dbcur.execute(query2,(entry1,entry2))
          rows1=dbcur.fetchall()
          return render_template('filter_faculty.html', row_dep=row_dep,rows1=rows1,table_ind=1)

      if entry1!='None' and entry2=='None':
          query3=("select department.department_name, faculty.faculty_ID, faculty.faculty_name \
              from department join faculty on department.department_name= faculty.department_name \
                  where department.department_name=(%s)")
          dbcur.execute(query3,(entry1,))
          rows1=dbcur.fetchall()
          return render_template('filter_faculty.html',row_dep=row_dep,rows1=rows1,table_ind=2)
      if entry1=='None' and entry2!='None':
          query4=("select course.department_name, faculty.faculty_ID, faculty.faculty_name,course.course_ID,course.course_title \
              from course join faculty_with_course on course.course_ID= faculty_with_course.course_ID  \
                  join faculty on faculty_with_course.faculty_ID=faculty.faculty_ID \
                  where course.course_ID=(%s)")
          dbcur.execute(query4,(entry2,))
          rows1=dbcur.fetchall()
          return render_template('filter_faculty.html',row_dep=row_dep,rows1=rows1,table_ind=3)
      if entry1=='None' and entry2=='None':
          msg='Please enter the input to get filter results !'
          flash(msg)
    return render_template('filter_faculty.html',row_dep=row_dep)










@app.route('/filter/course', methods=['POST','GET'])
def filter_course():
    dbcur.execute('select department_name from department')
    rows_dep=dbcur.fetchall()
    dbcur.execute('select distinct year from faculty_with_course')
    rows_year=dbcur.fetchall()
    if request.method=='POST':
         entry1=request.form['department_name']
         entry2=request.form['faculty_ID']
         entry_st_year=request.form['st_year']
         entry_st_sem=request.form['st_sem']
         entry_en_year=request.form['en_year']
         entry_en_sem=request.form['en_sem']
         if(not((entry_st_year=='None' and entry_st_sem=='None' and entry_en_year=='None' and entry_en_sem=='None') or(  entry_st_year!='None' and entry_st_sem!='None' and entry_en_year!='None' and entry_en_sem!='None'  and (abs_time_calc(entry_st_year,entry_st_sem)<= abs_time_calc(entry_en_year,entry_en_sem))) )):
             msg='Please re-enter the correct and complete time range for query results !'
             flash(msg)
          
             return render_template('filter_course.html',rows_dep=rows_dep,rows_year=rows_year)
         if((entry_st_year=='None' and entry_st_sem=='None' and entry_en_year=='None' and entry_en_sem=='None')):
             if entry1=='None' and entry2=='None':
                 query_one=("SELECT department.department_name,faculty.faculty_ID,faculty.faculty_name, faculty_with_course.course_ID,faculty_with_course.year,faculty_with_course.semester,faculty_with_course.No_students,timetable.start_time,timetable.end_time,timetable.weekday,timetable.room_no \
                  FROM department join faculty on faculty.department_name=department.department_name \
                  JOIN faculty_with_course on faculty.faculty_ID=faculty_with_course.faculty_ID  \
                  JOIN timetable on faculty_with_course.course_ID = timetable.course_ID and faculty_with_course.year=timetable.year and faculty_with_course.semester = timetable.semester  \
                  where faculty.department_name=faculty.department_name and faculty.faculty_ID=faculty.faculty_ID")
             #  query_abs_time=("update faculty_with_course set abs_time=(%f) where semester=(%s)")
                 dbcur.execute(query_one)
                 rows1=dbcur.fetchall()
                 return render_template('filter_course.html',rows1=rows1,rows_dep=rows_dep,rows_year=rows_year)
             if entry1=='None' and entry2!='None':
              query_two=("SELECT department.department_name,faculty.faculty_ID,faculty.faculty_name, faculty_with_course.course_ID,faculty_with_course.year,faculty_with_course.semester,faculty_with_course.No_students,timetable.start_time,timetable.end_time,timetable.weekday,timetable.room_no \
              FROM department join faculty on faculty.department_name=department.department_name \
              JOIN faculty_with_course on faculty.faculty_ID=faculty_with_course.faculty_ID  \
              JOIN timetable on faculty_with_course.course_ID = timetable.course_ID and faculty_with_course.year=timetable.year and faculty_with_course.semester = timetable.semester  \
              where faculty.department_name=faculty.department_name and faculty.faculty_ID=(%s)")
            
              dbcur.execute(query_two,(entry2,))
              rows1=dbcur.fetchall()
              return render_template('filter_course.html',rows1=rows1,rows_dep=rows_dep,rows_year=rows_year)
             if entry1!='None' and entry2=='None':
              query_three=("SELECT department.department_name,faculty.faculty_ID,faculty.faculty_name, faculty_with_course.course_ID,faculty_with_course.year,faculty_with_course.semester,faculty_with_course.No_students,timetable.start_time,timetable.end_time,timetable.weekday,timetable.room_no \
              FROM department join faculty on faculty.department_name=department.department_name \
              JOIN faculty_with_course on faculty.faculty_ID=faculty_with_course.faculty_ID  \
              JOIN timetable on faculty_with_course.course_ID = timetable.course_ID and faculty_with_course.year=timetable.year and faculty_with_course.semester = timetable.semester  \
              where faculty.department_name=(%s) and faculty.faculty_ID=faculty.faculty_ID")
            
              dbcur.execute(query_three,(entry1,))
              rows1=dbcur.fetchall()
              return render_template('filter_course.html',rows1=rows1,rows_dep=rows_dep,rows_year=rows_year)
             if entry1!='None' and entry2!='None':
              query_four=("SELECT department.department_name,faculty.faculty_ID,faculty.faculty_name, faculty_with_course.course_ID,faculty_with_course.year,faculty_with_course.semester,faculty_with_course.No_students,timetable.start_time,timetable.end_time,timetable.weekday,timetable.room_no \
              FROM department join faculty on faculty.department_name=department.department_name \
              JOIN faculty_with_course on faculty.faculty_ID=faculty_with_course.faculty_ID  \
              JOIN timetable on faculty_with_course.course_ID = timetable.course_ID and faculty_with_course.year=timetable.year and faculty_with_course.semester = timetable.semester  \
              where faculty.department_name=(%s) and faculty.faculty_ID=(%s)")
            
              dbcur.execute(query_four,(entry1,entry2))
              rows1=dbcur.fetchall()
              return render_template('filter_course.html',rows1=rows1,rows_dep=rows_dep,rows_year=rows_year)
        
         elif(( entry_st_year!='None' and entry_st_sem!='None' and entry_en_year!='None' and entry_en_sem!='None'  and (abs_time_calc(entry_st_year,entry_st_sem)<= abs_time_calc(entry_en_year,entry_en_sem)))):
            st_abs_time=abs_time_calc(entry_st_year,entry_st_sem)
            en_abs_time=abs_time_calc(entry_en_year,entry_en_sem)
            if entry1=='None' and entry2=='None':
                 query_five=("SELECT department.department_name,faculty.faculty_ID,faculty.faculty_name, faculty_with_course.course_ID,faculty_with_course.year,faculty_with_course.semester,faculty_with_course.No_students,timetable.start_time,timetable.end_time,timetable.weekday,timetable.room_no \
                  FROM department join faculty on faculty.department_name=department.department_name \
                  JOIN faculty_with_course on faculty.faculty_ID=faculty_with_course.faculty_ID  \
                  JOIN timetable on faculty_with_course.course_ID = timetable.course_ID and faculty_with_course.year=timetable.year and faculty_with_course.semester = timetable.semester  \
                  where faculty.department_name=faculty.department_name and faculty.faculty_ID=faculty.faculty_ID and faculty_with_course.abs_time<=(%s) and faculty_with_course.abs_time>=(%s)")
             #  query_abs_time=("update faculty_with_course set abs_time=(%f) where semester=(%s)")
                 dbcur.execute(query_five,(en_abs_time,st_abs_time))
                 rows1=dbcur.fetchall()
                 return render_template('filter_course.html',rows1=rows1,rows_dep=rows_dep,rows_year=rows_year)
            if entry1=='None' and entry2!='None':
              query_six=("SELECT department.department_name,faculty.faculty_ID,faculty.faculty_name, faculty_with_course.course_ID,faculty_with_course.year,faculty_with_course.semester,faculty_with_course.No_students,timetable.start_time,timetable.end_time,timetable.weekday,timetable.room_no \
              FROM department join faculty on faculty.department_name=department.department_name \
              JOIN faculty_with_course on faculty.faculty_ID=faculty_with_course.faculty_ID  \
              JOIN timetable on faculty_with_course.course_ID = timetable.course_ID and faculty_with_course.year=timetable.year and faculty_with_course.semester = timetable.semester  \
              where faculty.department_name=faculty.department_name and faculty.faculty_ID=(%s) and faculty_with_course.abs_time<=(%s) and faculty_with_course.abs_time>=(%s)")
            
              dbcur.execute(query_six,(entry2,en_abs_time,st_abs_time))
              rows1=dbcur.fetchall()
              return render_template('filter_course.html',rows1=rows1,rows_dep=rows_dep,rows_year=rows_year)
            if entry1!='None' and entry2=='None':
              query_seven=("SELECT department.department_name,faculty.faculty_ID,faculty.faculty_name, faculty_with_course.course_ID,faculty_with_course.year,faculty_with_course.semester,faculty_with_course.No_students,timetable.start_time,timetable.end_time,timetable.weekday,timetable.room_no \
              FROM department join faculty on faculty.department_name=department.department_name \
              JOIN faculty_with_course on faculty.faculty_ID=faculty_with_course.faculty_ID  \
              JOIN timetable on faculty_with_course.course_ID = timetable.course_ID and faculty_with_course.year=timetable.year and faculty_with_course.semester = timetable.semester  \
              where faculty.department_name=(%s) and faculty.faculty_ID=faculty.faculty_ID and faculty_with_course.abs_time<=(%s) and faculty_with_course.abs_time>=(%s)")
            
              dbcur.execute(query_seven,(entry1,en_abs_time,st_abs_time))
              rows1=dbcur.fetchall()
              return render_template('filter_course.html',rows1=rows1,rows_dep=rows_dep,rows_year=rows_year)
            if entry1!='None' and entry2!='None':
              query_eight=("SELECT department.department_name,faculty.faculty_ID,faculty.faculty_name, faculty_with_course.course_ID,faculty_with_course.year,faculty_with_course.semester,faculty_with_course.No_students,timetable.start_time,timetable.end_time,timetable.weekday,timetable.room_no \
              FROM department join faculty on faculty.department_name=department.department_name \
              JOIN faculty_with_course on faculty.faculty_ID=faculty_with_course.faculty_ID  \
              JOIN timetable on faculty_with_course.course_ID = timetable.course_ID and faculty_with_course.year=timetable.year and faculty_with_course.semester = timetable.semester  \
              where faculty.department_name=(%s) and faculty.faculty_ID=(%s) and faculty_with_course.abs_time<=(%s) and faculty_with_course.abs_time>=(%s)")
            
              dbcur.execute(query_eight,(entry1,entry2,en_abs_time,st_abs_time))
              rows1=dbcur.fetchall()
              return render_template('filter_course.html',rows1=rows1,rows_dep=rows_dep,rows_year=rows_year)     



   
    
    return render_template('filter_course.html',rows_dep=rows_dep,rows_year=rows_year)
    
      

@app.route('/get_fac/<string:department>', methods=['GET'])
def get_fac(department):
   
    dbcur.execute("SELECT faculty_ID,faculty_name FROM faculty WHERE department_name = (%s)", [department])
    faculty_rows= dbcur.fetchall()
    faculty_array=[]
    for row in faculty_rows:
        faculty_object={
            'faculty_ID': row[0],
            'faculty_name': row[1]
        }
        faculty_array.append(faculty_object)
    return jsonify({'faculty_json' : faculty_array})


@app.route('/edit/<string:name>/department', methods=['GET','POST'])
def edit_department(name):
    if request.method=='POST':
        try:
         entry = request.form['department_name']
         
         query = "INSERT INTO department(department_name) VALUES (%s)"
         dbcur.execute(query,(entry,))
         db.commit()
         msg=  " A new department named (%s) added !" %entry
         flash(msg) 
        except:
            msg='This entry violates the primary key constraint. Refer to the ER diagram !'
            flash(msg)
        # dbcur.execute('Select * from department')
        # rows= dbcur.fetchall()
        # return redirect({{url_for('edit_department',name=name)}})
    dbcur.execute('Select * from department')
    rows= dbcur.fetchall()
    return render_template('department.html', name=name ,rows=rows)  


@app.route('/edit/<string:name>/department/delete/<string:name1>')
def delete_department(name,name1):
    query='delete from department where department_name=(%s)'
    val= name1
    dbcur.execute(query,(val,))
    db.commit()
    dbcur.execute('select * from department')
    rows= dbcur.fetchall()
    return render_template('department.html',name=name,rows=rows)





@app.route("/edit/<string:name>/faculty", methods=['GET', 'POST'])
def edit_faculty(name):
    if request.method=='POST':
        dep_name=request.form['department_name']
        query="select department_name from department where department_name=(%s)"
        dbcur.execute(query,(dep_name,))
        # db.commit()
        is_pre=dbcur.fetchall()
        if len(is_pre)>0:
           try:
            entry1=request.form['faculty_ID']
            entry2=request.form['faculty_name']
            entry3=request.form['department_name']
            query1="insert into faculty(Faculty_ID,Faculty_name,department_name) values(%s,%s,%s)"
            dbcur.execute(query1,(entry1,entry2,entry3))
            db.commit()
            msg= "A new Faculty named is added !"
            flash(msg)
           except:
               msg='Primary key constraint violated ! Refer to the ER diagram !'
               flash(msg)

        else:
            msg="This department doesn't exist ! Please enter correct entry !"
            flash(msg)
    dbcur.execute("select * from faculty")
    rows= dbcur.fetchall()
    return render_template("faculty.html", name=name, rows=rows)

@app.route('/edit/<string:name>/faculty/delete/<string:name1>')
def delete_faculty(name,name1):
    query='delete from faculty where faculty_ID=(%s)'
    val= name1
    dbcur.execute(query,(val,))
    db.commit()
    dbcur.execute('select * from faculty')
    rows= dbcur.fetchall()
    return render_template('faculty.html',name=name,rows=rows)


@app.route("/edit/<string:name>/course", methods=['POST','GET'])
def edit_course(name):
    if request.method=='POST':
         dep_name=request.form['department_name']
         query="select department_name from department where department_name=(%s)"
         dbcur.execute(query,(dep_name,))
        # db.commit()
         is_pre=dbcur.fetchall()
         if len(is_pre)>0:
           try:
            entry1=request.form['course_ID']
            entry2=request.form['course_title']
            entry3=request.form['department_name']
            query1="insert into course(course_ID,course_title,department_name) values(%s,%s,%s)"
            dbcur.execute(query1,(entry1,entry2,entry3))
            db.commit()
            msg= "A new Course named is added !"
            flash(msg)
           except:
               msg='Primary key constraint violated ! Refer to the ER diagram !'
               flash(msg)

         else:
            msg="This department doesn't exist ! Please enter correct entry !"
            flash(msg)
    dbcur.execute("select * from course")
    rows= dbcur.fetchall()
    return render_template('course.html',name=name,rows=rows)

@app.route('/edit/<string:name>/course/delete/<string:name1>')
def delete_course(name,name1):
    query='delete from course where course_ID=(%s)'
    val= name1
    dbcur.execute(query,(val,))
    db.commit()
    dbcur.execute('select * from course')
    rows= dbcur.fetchall()
    return render_template('course.html',name=name,rows=rows)








@app.route('/edit/<string:name>/faculty--with--course', methods=['POST','GET'])
def edit_fwc(name):
    if request.method=='POST':
        fid= request.form['faculty_ID']
        cid= request.form['course_ID']
        query1="select course_ID from course where course_ID=(%s)"
        query2="select faculty_ID from faculty where faculty_ID=(%s)"
        dbcur.execute(query1,(cid,))
        course_pre= dbcur.fetchall()
        
        dbcur.execute(query2,(fid,))
        faculty_pre=dbcur.fetchall()
       
        if len(course_pre)>0 and len(faculty_pre)>0:
            query11='select department_name from course where course_ID=(%s)'
       
            dbcur.execute(query11,(course_pre[0][0],))
            dep_course= dbcur.fetchone()
            query21='select department_name from faculty where faculty_ID=(%s)'
            
            dbcur.execute(query21,(faculty_pre[0][0],))
            dep_fac= dbcur.fetchone()
            if dep_course[0]==dep_fac[0]:
             try:
               entry1= request.form['faculty_ID']
               entry2= request.form['course_ID']
               entry3= int(request.form['year'])
               entry4= request.form['semester']
               entry5= int(request.form['No_students'])
               query="insert into faculty_with_course(faculty_ID, course_ID, year, semester,No_students,abs_time) values(%s,%s,%s,%s,%s,%s)"
               
               if entry4=='FALL':
                 entry6=float(entry3)+0.5
                 dbcur.execute(query,(entry1,entry2,entry3,entry4,entry5,entry6))
                 db.commit()
               elif entry4=='SPRING':
                 entry6=float(entry3)
                 dbcur.execute(query,(entry1,entry2,entry3,entry4,entry5,entry6))
                 db.commit()

               msg= " A new course has been assigned to a faculty !"
               flash(msg)
             except Exception as e:
               print(e)
               msg='Primary Key constraint violated ! PLS look into the ER diagram and make a consistent entry!'
               flash(msg)
        else:
            msg='Course and/or Faculty does not exists OR may be course and faculty does not belong to same department. Pls look into table and Try again ! '
            flash(msg)
    dbcur.execute('select faculty_ID,course_ID,year,semester,No_students from faculty_with_course')
    rows=dbcur.fetchall()
    return render_template('fwc.html', name=name, rows=rows)

@app.route('/edit/<string:name>/faculty--with--course/delete/<string:name1>/<string:name2>/<float:name3>/<string:name4>')
def delete_fwc(name,name1,name2,name3,name4):
    query='delete from faculty_with_course where course_ID=(%s) and faculty_ID=(%s) and  year=(%s) and  semester=(%s)'
    val1= name1
    val2= name2
    val3= name3
    val4= name4

    dbcur.execute(query,(val1,val2,val3,val4))
    db.commit()
    dbcur.execute('select faculty_ID,course_ID,year,semester,No_students from faculty_with_course')
    rows= dbcur.fetchall()
    return render_template('fwc.html',name=name,rows=rows)






@app.route('/edit/<string:name>/timetable', methods=['POST','GET'])
def edit_timetable(name):
    if request.method=='POST':
        cid= request.form['course_ID']
        query='select * from course where course_ID=(%s)'
        dbcur.execute(query,(cid,))
        is_pre_in_course=dbcur.fetchall()
        query_='select * from faculty_with_course where course_ID=(%s)'
        dbcur.execute(query_,(cid,))
        is_pre_in_fwc=dbcur.fetchall()

        if len(is_pre_in_course)>0 and len(is_pre_in_fwc)>0:
            try:
             entry1= request.form['course_ID']
             entry2= request.form['start_time']
             entry3= request.form['end_time']
             entry4= request.form['weekday']
             entry5= request.form['room_no']
             entry6= request.form['year']
             entry7= request.form['semester']

             query1='insert into timetable(course_ID,start_time ,end_time, weekday, room_no,  year, semester) values(%s,%s,%s,%s,%s,%f,%s)'
             dbcur.execute(query1,(entry1,entry2,entry3,entry4,entry5,entry6,entry7))
             db.commit()
             query2='select course_title from course where course_ID=(%s)'
             dbcur.execute(query2,(cid,))
             course_name=dbcur.fetchone()
             msg='TimeTable for a course has been added !'
             flash(msg)
            except:
                msg='The entry you made violates the primary key constraint. Refer to the ER diagram !'
                flash(msg)
        else:
            msg='This course does not exists. pls check the courses table !'
            flash(msg)    
    dbcur.execute('select * from timetable')
    rows=dbcur.fetchall()
    return render_template('timetable.html',name=name,rows=rows)

@app.route('/edit/<string:name>/timetable/delete/<string:name1>/<string:name2>/<string:name3>/<string:name4>')
def delete_timetable(name,name1,name2,name3,name4):
    query='delete from timetable where course_ID=(%s) and year=(%f) and  weekday=(%s) and  semester=(%s)'
    val1= name1
    val2= name2
    val3= name3
    val4= name4

    dbcur.execute(query,(val1,val2,val3,val4))
    db.commit()
    dbcur.execute('select * from timetable')
    rows= dbcur.fetchall()
    return render_template('timetable.html',name=name,rows=rows)







@app.route("/edit/<string:name>", methods=['POST','GET'])
def edit(name):
  if request.method=='POST':   
    uploaded_file=request.files['file']
    if uploaded_file.filename!='':
        file_path=os.path.join(UPLOAD_FOLDER,uploaded_file.filename)
        uploaded_file.save(file_path)
        col_names=['department_name','faculty_ID','faculty_name','course_ID','course_title','year','semester','weekday','start_time','end_time','room_no','No_students']
        csvData= pd.read_csv(file_path,names=col_names,header=None)
        prop=True
        for i,row in csvData.iterrows():
            st=row['start_time']
            et=row['end_time']
            query='select * from timetable where not(start_time>=(%s) or end_time<=(%s)) and year=(%s) and semester=(%s) and weekday=(%s) and room_no=(%s)'
            dbcur.execute(query,(et,st,row['year'],row['semester'],row['weekday'],row['room_no']))
            coincide= dbcur.fetchall()
            if len(coincide)>0:
                prop=False
                msg='Your CSV file contains session that already exists in Table. Pls check the tables and edit your CSV file at %d th row before uploading again !' %(i+1)
                flash(msg)
                break
        if prop:
            for i,row in csvData.iterrows():
                try:
                 query1='insert into department(department_name) values(%s)'
                 dbcur.execute(query1,(row['department_name'],))
                 db.commit()
                except:
                    print('This Department already present !')
                try:
                 query2='insert into faculty(faculty_ID,faculty_name,department_name) values(%s,%s,%s)'
                 dbcur.execute(query2,(row['faculty_ID'],row['faculty_name'],row['department_name']))
                 db.commit()
                except:
                    print('Faculty ID "(%s)" already present') %row['faculty_ID']
                try:    
                 query3='insert into course(course_ID,course_title,department_name) values(%s,%s,%s)'
                 dbcur.execute(query3,(row['course_ID'],row['course_title'],row['department_name']))
                 db.commit()
                except:
                    print('course ID "(%s)" already present !') %row['course_ID']
                try:    
                 query4='insert into faculty_with_course(course_ID,faculty_ID,year,semester,No_students) values(%s,%s,%s,%s,%s)'
                 dbcur.execute(query4,(row['course_ID'],row['faculty_ID'],row['year'],row['semester'],row['No_students']))
                 db.commit()
                except:
                    print('(%s) has already been assigned a course for this semester !') %row['faculty_ID']
                try:    
                 query5='insert into timetable(course_ID,start_time,end_time,year,weekday,room_no,semester) values(%s,%s,%s,%s,%s,%s,%s)'
                 dbcur.execute(query5,(row['course_ID'],row['start_time'],row['end_time'],row['year'],row['weekday'],row['room_no'],row['semester']))
                 db.commit()
                except:
                    print('This particular room "(%s)" has been booked for a course already !') %row['room_no']
            msg='The CSV file has been successfully added to all tables !'
            flash(msg)             
                    
  return render_template('logout.html',name_user=name)
    
   
@app.route("/logout")
def logout():
    session.pop('username',None)
    return redirect(url_for('login'))

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session['username'] = request.form['username']
        name1 = session['username']
        dbcur.execute("SELECT * FROM credentials WHERE username= %s AND password=%s",(name1 , request.form['password']))
        data= dbcur.fetchall()
        if(len(data)>0):
            
         return redirect(url_for('edit', name=name1))
        else:
            flash("ERROR ! Your credentials don't match. Try again !")
            return render_template('login.html')
    return render_template('login.html')




if __name__ == '__main__':
    app.run(debug=True)






 