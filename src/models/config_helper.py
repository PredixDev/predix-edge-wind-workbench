import os.path
from shutil import copyfile

#Handle config files for apps and site management
#Inside container:
# The app config files are stored in /opt/microservice
# The site config files are store in ./site_config
# Site config is expected to be volumned from host

def file_for_site_management(filename):
    #the function will be disabled
    return filename
    app_dir = "/opt/microservice"
    site_dir = "site_config"
    app_config_file = os.path.join(app_dir, filename)
    site_file =  os.path.join(site_dir, filename)

    # If site config file is volumned from host, will use the site config file
    if os.path.isfile(site_file):
        return site_file
    # If site config folder does not exist (No volumne in)
    # Will try to create the folder
    if not os.path.exists(site_dir):
        try:
            os.makedirs(site_dir)
        except:
            print "INFO: could not make site directory", site_dir
            print "INFO: use default app config file", app_config_file
            return app_config_file

    # No matter the site deployment personnel choose to volumn or not
    # site_dir should exist now
    # Alway copy the default app config file to site_dir
    # For first time docker volumn, this will provide an opportunity for site
    # deployment personnel to modify the config files

    if os.path.isfile(app_config_file):
        try:
            copyfile(app_config_file, site_file)
            return site_file
        except:
            print "INFO: could not copy {0} to {1}".format(app_config_file, site_file)
            print "INFO: use default app config file", app_config_file
            return app_config_file
    else:
        print "INFO: could not locate default app config file ", app_config_file
        return None

if __name__ == '__main__':

    print file_for_site_management("config/plot.config")
