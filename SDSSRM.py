# These are the needed packages for SDSSRM.
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import pandas as pd
from astroquery.sdss import SDSS

def datafetcher():
    # This function fetches a sample SDSS data for ra, dec, run from PhotoObj within certain magnitudes.
    # The resulting data table is then saved for future reference as a .csv file.
    
    query1 = """
            select
                ra, dec, run
            from PhotoObj
            where psfMag_g BETWEEN 16.96 and 16.99
            """
    query2 = """
            select
                ra, dec, run
            from PhotoObj
            where psfMag_g BETWEEN 17 and 17.041
            """
    query3 = """
            select
                ra, dec, run
            from PhotoObj
            where psfMag_g BETWEEN 17.041 and 17.08
            """
    query4 = """
            select
                ra, dec, run
            from PhotoObj
            where psfMag_g BETWEEN 17.08 and 18.02
            """
    res1 = SDSS.query_sql(query1, timeout=3600).to_pandas()
    res2 = SDSS.query_sql(query2, timeout=3600).to_pandas()
    res3 = SDSS.query_sql(query3, timeout=3600).to_pandas()
    res4 = SDSS.query_sql(query4, timeout=3600).to_pandas()
    concat_res = pd.concat([res1, res2, res3, res4], ignore_index=True)
    concat_res.to_csv('SDSSdatasample.csv')
    return concat_res

def mapcutter(ra_l, ra_u, dec_l, dec_u, datatable):
    # This function is the bread and butter of the module. 
    # It takes the passed parameters and outputs a snapshot of a heatmap of the runs done within a specific region.
    
    #The passed table is cut by the bounds passed and rounded in order to get 1x1 degree pixels.
    cuttable = datatable.query(f'({ra_l} <= ra) & ({ra_u} >= ra)').query(f'({dec_l} <= dec) & ({dec_u} >= dec)')
    cuttable['ra'] = np.floor(cuttable['ra'])
    cuttable['dec'] = np.floor(cuttable['dec'])
    
    img = runcounter(cuttable) # calls function to make the grid necessary for graphing
    
    #creates ticks present for every 15 degrees
    ra_ticks = np.arange(ra_l, ra_u+15, 15)
    dec_ticks = np.arange(dec_l, dec_u+15, 15)
    
    # Below is the graphing process.
    plt.style.use('ggplot')
    plt.rc('axes', grid=False)   # turn off the background grid for images
    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(12,6)
    fig.tight_layout()           # Make better use of space on plot
    
    ax.set_xlabel('RA')
    ax.set_ylabel('DEC')
    ax.set_title('SDSS Runs Map')
    
    ax.set_xticks(ra_ticks)
    ax.set_yticks(dec_ticks)
    
    plot = ax.imshow(img[dec_l+90:dec_u+90, ra_l:ra_u], 
                     norm=LogNorm(vmin = 1, vmax = 100), 
                     origin='lower', 
                     cmap=plt.cm.viridis, 
                     extent=[ra_l,ra_u,dec_l,dec_u])
    fig.colorbar(plot)
    
    plt.savefig("runsmap.png", bbox_inches='tight') #saves the plot as a png file
    
    return plot

def runcounter(table):
    # This function takes in a table and creates a grid containing the amount of runs 
    # in each RA and DEC, used for plotting with plt.imshow.
    
    imgdata = table.groupby(['ra', 'dec'])['run'].nunique()
    img = np.zeros([180,360])
    img[imgdata.index.to_frame()['dec'].values.astype(int)+90, imgdata.index.to_frame()['ra'].values.astype(int)] = imgdata.values
    
    return img

def runs_map(ra_l, ra_u, dec_l, dec_u):
    # This function is the main function called within SDSSRM.
    # It outputs a slice of the map with the given parameters through using several other functions.
    # The parameters passed are the lower RA bound, upper RA bound, lower DEC bound, and upper DEC bound, in integers.
    
    try: #If a previous data file was made, the function will read it.
        datatable = pd.read_csv('./SDSSdatasample.csv')
    except IOError:
        print("Data file not accessible - creating new data file. This will take a while.")
        datatable = datafetcher()
    plot = mapcutter(ra_l, ra_u, dec_l, dec_u, datatable)
    
    return plot

def full_map():
    # outputs the full runs map.
    # The bounds are hard-coded to output the whole observed region.
    
    try:
        datatable = pd.read_csv('./SDSSdatasample.csv')
    except IOError:
        print("Data file not accessible - creating new data file. This will take a while.")
        datatable = datafetcher()
    plot = mapcutter(0, 360, -90, 90, datatable)
    return plot

