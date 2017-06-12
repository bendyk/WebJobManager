#!/usr/bin/python

import sqlite3 as lite
import sys
import os

gnu_template = """
set terminal pngcairo enhanced font "arial,10" fontscale 1.0 size 600, 600
set output 'time_hist.png'
set title "Times"
set key left top
set xtics
set ytics
set mytics 10
set grid xtics
set grid ytics
set grid mytics
set xrange[0:27]
set yrange[0:250]
set xtics nomirror rotate by -45
set style data histogram
set style histogram rowstacked
set style fill solid border -1 
set boxwidth 0.8
plot 'plot.dat' using 2:xtic(1) lc rgb "#ffffff" title "Time to submission", '' u 3 lc rgb "#ff9933" title "Time in queue", '' u 4 lc rgb "#00ff00" title "Execution time", '' u 5 lc rgb "#ff0000" title "Time to post ", '' u 6 lc rgb "#ffff00" title "Post time"
"""


def main():
    filepath = ""
    jobs     = []

    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        print("Path to database file (montage-0.stampede.db) of the montage run missing")
        exit(-1)

    db_conn   = lite.connect(filepath)
    db_cursor = db_conn.cursor()

    db_cursor.execute('SELECT timestamp FROM workflowstate WHERE state == "WORKFLOW_STARTED"')
    start_wf = int(db_cursor.fetchone()[0])

    db_cursor.execute('SELECT exec_job_id, job_instance_id, cluster_start, cluster_duration FROM job, job_instance WHERE job_instance.job_submit_seq < 25 AND job.job_id = job_instance.job_id ORDER BY job_submit_seq')
    
    data_jobs = db_cursor.fetchall()
    for job in data_jobs:
        jobs += [{"name":job[0], "id":job[1], "exec_s": job[2], "exec_d":job[3]}]
    
    for job in jobs:
        db_cursor.execute('SELECT timestamp FROM jobstate WHERE job_instance_id == %d ORDER BY jobstate_submit_seq' % job["id"])
        data = db_cursor.fetchall()
        job["submit"] = data[0][0] - start_wf
        
        if(job["exec_s"] == None):
            job["exec_s"] = data[1][0] - data[0][0]
            job["exec_d"] = data[2][0] - data[1][0]
        else:
            job["exec_s"] -= data[0][0]
        
        if len(data) > 4:
            job["post_s"] = data[4][0] - data[0][0] - job["exec_s"] - job["exec_d"]
            job["post_d"] = data[5][0] - data[4][0]
        else:
            job["post_s"] = 0
            job["post_d"] = 0        

         

    with open("plot.dat", "w") as f:
        for job in jobs:
            submit = job["submit"]
            exec_s = job["exec_s"]
            exec_t = job["exec_d"]
            post_s = job["post_s"]
            post_t = job["post_d"]
            f.write("%s\t%d\t%d\t%d\t%d\t%d\n" % (job["name"].replace("_", "-"), submit, exec_s, exec_t, post_s, post_t))


    with open("plot.gnu", "w") as f:
        f.write(gnu_template)

    os.system("gnuplot plot.gnu")
    os.remove("plot.gnu")

if __name__ == '__main__':
    main()
