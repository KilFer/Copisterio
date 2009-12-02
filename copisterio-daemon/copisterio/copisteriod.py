"""
    Copisterio Daemon

"""
import os
import mimetypes
from ConfigParser import ConfigParser
from twisted.internet.task import LoopingCall
import twisted.internet.reactor as reactor
import statvfs

# Global configuration
__logfile__ = "/var/log/copisteriod.log"
__altlogfile__ = "/tmp/copisteriod.log"
__config_file__ = "copisteriod.conf"
__base_cfile__ = "/etc/copisteriod.conf"

class CopisterioInternal():
    """
          Internal functions used by copisterio daemn
    """

    def __init__(self, cfile):
        self.conf = ConfigParser()
        self.conf.read(cfile)
        self.db=self.init_db()

        if not self.conf.has_section('main'):
            print 'No conffile found'
            exit()

        try:
            self.log = open(__logfile__, 'a')
        except IOError:
            self.log = open(__altlogfile__, 'a')

        self.debug = self.cfg('debug')

        if self.debug is "Undefined":
            self.debug = 1

    def cfg(self, name):
        """
            Get configuration values
        """

        if self.conf.has_option('main', name):
            return self.conf.get('main', name)
        else:
            exit("Undefined option %s" %name)

    def log(self, status, log):
        """
            Logger
        """
        if not self.log:
            print status, '> ', log
            return

        if status is "DEBUG" and self.debug is 1 or status is not "DEBUG":
            self.log.write(status + '> ' + str(log) +  "\n")

    def init_db(self):
        conn = MySQLdb.connect (host = self.cfg("host"),
                           user = self.cfg('user'),
                           passwd = self.cfg('pass'),
                           db = self.cfg('db'))
        return conn.cursor()

class CopisterioDisk():
    """
        Disk management
    """
    def __init__(self, internal):
        """
            This is the class for disk usage management
        """
        self.i = internal
        self.db=self.i.db
        self.i.log('DEBUG', 'Initialized CopisterioDisk class')

    def _get_disk_data(self, ldir):
        """
            We return a statvfs object
        """
        disk = os.statvfs(ldir)
        self.i.log('DEBUG', "Disk data array is:" + str(disk))
        return disk

    def disk_status(self, ldir):
        """
            We got the available space in percentage
        """
        disk_stat = self._get_disk_data(ldir)
        return (disk_stat[statvfs.F_BAVAIL] * 100) / disk_stat[statvfs.F_BFREE]

    def to_free(self, disk_status, min_free_space):
        """
            We got the space neccesary to free to get the minum free space
            required (in bytes)
        """
        self.i.log('DEBUG', 'Calculating free space')
        return int(min_free_space) - disk_status[statvfs.F_BFREE] * 4096 # TODO Check this

    def delete_files(self, files):
        """
            Delete an array of files
        """
        for lfile in files:
            os.unlink(lfile)
            self.i.log('DEBUG', 'Unlinking file: %s' %lfile)


    def list_files(self, ldir):
        """
            Return files in a ldirectory, in a list of lists with all the files info
        """
        # FIXME woops, we should just get FILES not directories...
        # lfile --> root, mimetype, filename

        self.i.log('DEBUG', "Listing files in %s" %ldir)
        res = list()
        for root, ldirs, files in os.walk(ldir):
            [ res.append(root , lfile,
             mimetypes.guess_type( root + lfile)[0], lfile.__getitem__(0),
             _status(lfile)['st_ctime'], _status(lfile)['st_size'])\
             for lfile in files]
        res.sort( lambda a, b: cmp(a[3], b[3]) )
        return res

    def _status(self, lfile):
        """
            Return data of a file to be used within _list_files
        """
        return os.stat_result(os.stat(lfile))

    def get_old_files(self, mainldir, freed=0, oldies=list()):
        """
            Get oldest files until we free neccesary space
        """

        to_free = self.to_free( self._get_disk_data(mainldir),
                self.i.cfg('minspace'))

        for lfile in self.list_files(self.i.cfg('library')):
            if freed < to_free:
                break
            freed += lfile[2]
            oldies.append(lfile)

        if oldies:
            self.i.log('INFO', "Current old files to delete: " + oldies)

        return oldies

    def move_file(self, file):
        """
            This moves the file from admdir to final dir in media organised
            alphabetically and by type
        """
        # FIXME do this
        fileo=_status(file)
        os.rename(file, file[X])
        return full_path

    def check_processing(self, file, status):
        """
            This checks the file status, then moves it and adds it to db
            or deletes it
        """

        if status is 1:
            full_path=self.move_file(file)
            self.delete_file_from_db(file,'Processing')
            self.insert_file_in_db((file, full_path), "Approved" )

        elif status is 0:
            self.delete_file_from_db(file,'processing')
            self.delete_files([file,])

class CopisterioDaemon():
    """
       Main class for the daemon
    """

    def __init__(self, cfile):
        """
            This is copisterio Daemon class
        """

        self.i = CopisterioInternal(cfile)
        self.db=self.i.db
        self.loop = LoopingCall(self.work).start(int(self.i.cfg('frecuency')))

        reactor.run()

    def work(self):
        """
            This is the function doing the repeated work.
        """

        diskmanager = CopisterioDisk(self.i)

        self.i.log('DEBUG', "Free percentage: " +
                str(diskmanager.disk_status(self.i.cfg('main'))) + '%')

        if diskmanager.disk_status(self.i.cfg('main'))\
                < self.i.cfg('delete_status'):
            diskmanager.delete_files(diskmanager.get_old_files(
                self.i.cfg('main')))

        for lfile in diskmanager.list_files(self.i.cfg('main')):
            filepath=self.i.cfg('admdir') + os.sep + lfile[1]
            currentfilename=lfile[0] + os.sep + lfile[2]
            newfilename=filepath + os.sep + lfile[1] + os.sep + lfile[2]

            if (os.path.exists( newfilename):
                os.rename( currentfilename, newfilename)
                os.chown(os.getgid(), os.getuid(), newfilename)
                os.chmod(744, newfilename)
                thumbs=system('copisterio_mt %s %s' %(newfilename, filepath)
                self.diskmanager.insert_file_in_db((newfilename, thumbs),
                    "Processing")

            else:
                self.i.log('WARN', "File %s/%s exists" %(lfile[1], lfile[2]))

            self.db.execute("Select all from processing")
            for file in self.db.select_all: # FIXME

                diskmanager.check_processing(file)

if not os.path.exists( os.environ['HOME'] + os.sep + "." + __config_file__ ):
    __config_file__ = __base_cfile__
else:
    __config_file__ = os.environ['HOME'] + os.sep + "." + __config_file__

CopisterioDaemon(__config_file__)
