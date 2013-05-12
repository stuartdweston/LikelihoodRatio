#===========================================================================
#
# n_m.py
#
# Python script to query SWIRE_ES1 mysql database to determine the
# n(m) for the likelihood ratio.
#
#===========================================================================
#
# S. Weston
# AUT University
# March 2013
#===========================================================================

def n_m():

    print "\nStarting n(m) calculations and db updates\n"

    execfile('constants.py')

# Connect to the local database with the atlas uid

    db=_mysql.connect(host="localhost",user="atlas",passwd="atlas")

# Lets run a querry

    db.query("select IRAC_3_6_micron_FLUX_MUJY FROM swire_es1.es1_swire \
         where IRAC_3_6_micron_FLUX_MUJY != -9.9 \
         and ra_spitzer > 8.0 and ra_spitzer < 9.5 \
         and dec_spitzer < -43.0 and dec_spitzer > -44.5;")

# store_result() returns the entire result set to the client immediately.
# The other is to use use_result(), which keeps the result set in the server 
#and sends it row-by-row when you fetch.

#r=db.store_result()
# ...or...
    r=db.use_result()

# fetch results, returning char we need float !

    rows=r.fetch_row(maxrows=0)

# Close connection to the database

    db.close()

#print rows

# rows is a tuple, convert it to a list

    lst_rows=list(rows)

#mag=[]
#numpy.histogram(rows,bins=50)

# fetch_row paramaters, maxrows and how

#The other oddity is: Assuming these are numeric columns, why are they returned 
#as strings? Because MySQL returns all data as strings and expects you to 
#convert it yourself. This would be a real pain in the ass, but in fact, _mysql 
#can do this for you. (And MySQLdb does do this for you.) To have automatic 
#type conversion done, you need to create a type converter dictionary, and pass 
#this to connect() as the conv keyword parameter.

    f_rows=[]
    for row in lst_rows:

#   a = IRAC_3_6_micron_FLUX_MUJY
        a=map(float,row)
        b=math.log10(a[0])
#    print "Flux %4.8f Log10_Flux %4.8f " % (a[0], b)
        f_rows.append(b)

    (hist,bins)=numpy.histogram(f_rows,bins=60,range=[-1.0,5.0])
    width = 0.7*(bins[1]-bins[0])
    center = (bins[:-1]+bins[1:])/2
#plt.yscale('log')
#plt.xscale('log')
    plt.bar(center, hist, align = 'center',width = width,linewidth=0)
    plt.title('es1 N(m)')
    plt.ylabel('n(f)')
    plt.xlabel('log10(f)')
    plot_fname='atlas-elaise_nf_vs_log10f.ps'
    fname=output_dir + plot_fname
    plt.savefig(fname)
    plt.show()
    
# We have the binned data as a histogram, now insert it into table n_m_lookup

    db=_mysql.connect(host="localhost",user="atlas",passwd="atlas")
    db.query("set autocommit=0;")

# first is the lookup table empty, if yes then use insert if no then use update
    db.query("select count(*) from swire_es1.n_m_lookup;")
    r=db.store_result()
    rows=r.fetch_row(maxrows=1)
    for row in rows:
	    r_count=int(row[0])
	    
# If the row count from above is zero then insert into the db table, if row count is > 0 then update
    print "    Update database with n(m) values"
 	
    i=1
    for item in xrange(len(hist)):
        n_m=hist[item]
#        print " n_m md/area arcsec^2 : %14.9f %14.9f" % (hist[item], n_m) 
        log10_f=bins[item]
#       Update the database with the n(m) values	
        if r_count == 0:	
           db.query("insert into swire_es1.n_m_lookup(i,n_m,log10_f,md) values ('%d','%f','%f','%f');" % (i,n_m,log10_f,hist[item]))
        else:
           db.query("update swire_es1.n_m_lookup set n_m=%f, log10_f=%f, md=%f where i=%d;" % (n_m, log10_f, hist[item],i))
        db.commit()
        i=i+1

    db.commit()

# Close connection to the database
    db.close()

    print "\nEnd of n(m)"





