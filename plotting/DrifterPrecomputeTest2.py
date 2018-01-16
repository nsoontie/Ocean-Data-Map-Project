from netCDF4 import Dataset, netcdftime, chartostring
import datetime
import numpy as np
import glob, os
from oceannavigator.util import get_variable_name, get_variable_unit, \
    get_dataset_url, get_variable_scale_factor
from oceannavigator import app
import time
import datetime
from scipy.interpolate import interp1d

#inits

class DrifterModleComputer():
    def __init__(self, drifter, drifter_compute_modle):
        self.drifter
        self.drifter_modle = drifter_compute_modle # the file for the track of the modle
        self.drift_src_url = app.config['DRIFTER_URL']
        self.mrege_dest_url = app.config['DRIFTER_MODLE_MERGE_URL']


    def get_model_fileName(model, date):
        #TODO get current date
        if(model = "giops"):
            file_name = model + "_" + date + ".nc"
            file_name = 'giops_201704.nc'
            return file_name

    def get_last_date_checked():
        #reutn the date of the last update

    def wright_to_file(name, ):
    #get drifer list from done folder
    drifters = glob.glob('/data/drifter/done/*.nc')
    if len(drifters) < 1:
        print("ERROR: there are no drifter files in /data/drifter/done/  exiting script")
        exit()

    for drifter in drifters:
        output_file =  # new file modle_data_drifter_drifternumber.nc
        #get drifters times
            #interpulate the date list from drifter dates to dataset dates (maybe, maybe just interpulat to days)
        #get drifter postions
            #interpulate postions to dataset grid

    def load_data(self, ds):
        #open drifter
        ds_url = app.config['DRIFTER_URL']
        data_names = []
        data_units = []
        
        # open drifter file
        self.name = ds.buoyid

        self.imei = str(chartostring(ds['imei'][0]))
        self.wmo = str(chartostring(ds['wmo'][0]))

        t = netcdftime.utime(ds['data_date'].units)

        d = []
        for v in self.buoyvariables:
            d.append(ds[v][:])
            if "long_name" in ds[v].ncattrs():
                data_names.append(ds[v].long_name)
            else:
                data_names.append(v)

            if "units" in ds[v].ncattrs():
                data_units.append(ds[v].units)
            else:
                data_units.append(None)

        self.data = d

        self.times = t.num2date(ds['data_date'][:])
        self.points = np.array([
            ds['latitude'][:],
            ds['longitude'][:],
        ]).transpose()

        data_names = data_names[:len(self.buoyvariables)]
        data_units = data_units[:len(self.buoyvariables)]

        for i, t in enumerate(self.times):
            if t.tzinfo is None:
                self.times[i] = t.replace(tzinfo=pytz.UTC)

        self.data_names = data_names
        self.data_units = data_units

        if len(self.times) < 2
            print(error: "list of times in drifter is to short")
            continue
        self.starttime = self.times[0]
        self.endtime = self.times[-1]
        #to be removed
        if self.starttime is not None:
            d = dateutil.parser.parse(self.starttime)
            self.start = np.where(self.times >= d)[0].min()
        else:
            self.start = 0
        if self.endtime is not None:
            d = dateutil.parser.parse(self.endtime)
            self.end = np.where(self.times <= d)[0].max() + 1
        else:
            self.end = len(self.times) - 1

        if self.start < 0:
            self.start += len(self.times)
        self.start = np.clip(self.start, 0, len(self.times) - 1)
        if self.end < 0:
            self.end += len(self.times)
        self.end = np.clip(self.end, 0, len(self.times) - 1)
        


    '''
    * methoud: compute_modle
    * PRAMTERTERS: 
    * * frame_start: starting point in section for datapoint needed to be computed (should be the data at the start of the drifter file for new files, and the date after the last date with data in a drifter that alllreay has been made) 
    * * frame_end: should be the last date in the drifter file
    * return: returns 2 dimentional array [vars][values] which inturplated modle values for the points in the drifter file . 
    '''
    def compute_modle(modle_dataset, frame_start, frame_end):
        #open model file 
        with open_dataset(get_dataset_url(modle_dataset)) as dataset: # open aggreate modle dataset
            depth = int(self.depth)

            try:
                model_start = np.where(
                    dataset.timestamps <= self.times[self.start]
                )[0][-1]
            except IndexError:
                model_start = 0

            model_start -= 1
            model_start = np.clip(model_start, 0, len(dataset.timestamps) - 1)

            try:
                model_end = np.where(
                    dataset.timestamps >= self.times[self.end]
                )[0][0]
            except IndexError:
                model_end = len(dataset.timestamps) - 1

            model_end += 1
            model_end = np.clip(
                model_end,
                model_start,
                len(dataset.timestamps) - 1
            )

            model_times = map(
                lambda t: time.mktime(t.timetuple()),
                dataset.timestamps[model_start:model_end + 1]
            )
            output_times = map(
                lambda t: time.mktime(t.timetuple()),
                self.times[self.start:self.end + 1]
            )
            d = []
            #read in values
            for v in self.variables:
                #np.array([lat, lon]), distances, times, result
                pts, dist, mt, md = dataset.get_path(
                    self.points[self.start:self.end + 1],
                    depth,
                    range(model_start, model_end + 1),
                    v,
                    times=output_times
                )

                f = interp1d(
                    model_times,
                    md,
                    assume_sorted=True,
                    bounds_error=False,
                )

                d.append(np(f(mt)))

            model_data = np.ma.array(d)

            variable_names = []
            variable_units = []
            scale_factors = []

            for v in self.variables:
                variable_units.append(get_variable_unit(self.dataset_name,
                                                        dataset.variables[v]))
                variable_names.append(get_variable_name(self.dataset_name,
                                                        dataset.variables[v]))
                scale_factors.append(
                    get_variable_scale_factor(self.dataset_name,
                                                dataset.variables[v])
                )

            for idx, sf in enumerate(scale_factors):
                model_data[idx, :] = np.multiply(model_data[idx, :], sf)

            for idx, u in enumerate(variable_units):
                variable_units[idx], model_data[idx, :] = \
                    self.kelvin_to_celsius(u, model_data[idx, :])

            self.model_data = model_data
            self.model_times = map(datetime.datetime.utcfromtimestamp, mt)
            self.variable_names = variable_names
            self.variable_units = variable_units  
        
    def append_data(self, data, output_file):   

    #append to output_File
    #TODO add config
    exclude =['time_counter', 'nav_lon', 'nav_lat']
    removal_list = ['time_counter', 'x', 'y']
    exclude_attbutes = ['axis', 'online_operation']
    mode_data_list = ['giops_day'] 
    ds_url = '/home/jdawson/' # app.config['DRIFTER_URL']
    drifters = ['300234063262890.nc'] # TODO pass in crrect drifter
    Merged_file = 'Merge_test1_300234063262890.nc'


    for drifter in drifters:
        #TODO add the load data part of drifters .py here but mod it so that it wrights to file instead of ploting.
        model_name = 'giops_day' 
        if not os.path.isfile(self.mrege_dest_url % 'Merged_file_' % drifter) #TODO get propper file path

            #copy Drifter file
            try:
                shutil.copy2(self.drift_src_url % drifter, self.mrege_dest_url % 'Merged_file_' % drifter) #TODO check thi syntax
            except:
                print "drifter file copy/creat failed"
                continue
            #TODO open drifter file for wrighting
            with Dataset(Merged_file % drifter, 'w') as Merge_output:
                for md in mode_data_list:
                    with open_dataset(get_dataset_url(md)) as mode_dataset: 
                        mode_dataset   
                        #create dimentions
                        for d in mode_dataset.dimensions.keys():
                            if d not in Merge_output.dimensions.keys() and d not in exclude:
                                print d 
                                Merge_output.createDimension(d, len(mode_dataset.variables[d].dimensions) if not mode_dataset.dimensions[d].isunlimited() else None)
                        
                        #create the new varibles
                        for var_name in mode_dataset.variables.keys():
                            print "var name: " + var_name
                            if var_name in exclude or var_name in Merge_output.variables.keys():
                                print "skiping to next var"
                                continue
                            var_dimen = list(mode_dataset.variables[var_name].dimensions)
                            for dimen in removal_list:
                                if dimen in var_dimen:
                                    print "removeing: " + dimen
                                    var_dimen.remove(dimen) #remove unded dimention from the vairable
                            converted_dime = tuple(var_dimen)
                            new_var = Merge_output.createVariable(var_name, mode_dataset.variables[var_name].datatype, dimensions=temp)

                            #add attbutes to varibale
                            for attbute in mode_dataset.variables[var_name].ncattrs():
                                if attbute in exclude_attbutes:
                                    continue
                                try: 
                                    print "attbute values: " + mode_dataset.variables['vosaline'].getncattr(attbute)
                                    Merge_output.variables['vosaline'].setncattr(attbute, mode_dataset.variables['vosaline'].getncattr(attbute))
                                except:
                                    print "__ cound not print"

                    #TODO get start and end
                    times = netcdftime.utime(drifter.variables['data_date'].units)
                    times_gregoire = t.num2date(drifter_dataset.variables['data_date'][:])
                    startData = 
                    endDate = 
                    compute_modle(model_name, startData, endDate)            
                    
                    #TODO assigen data
                    for var in self.model_data #not sure if this is doing what I think it will
                        print var
                        Merge_output.vairable[var] = self.model_data[self.variables.index(var)]

        else:
            with Dataset(drifter % Merged_file, 'a') as Merge_output:
                compute_modle(modle_dataset, frame_start, frame_end)
                append_data(self.model_data, Merge_output)
                #TODO open conbined file
                #TODO append data
