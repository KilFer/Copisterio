"""
    Copisterio Daemon

"""
import os
import mimetypes
from ConfigParser import ConfigParser
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
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

class CopisterioDisk():
    """
        Disk management
    """
    def __init__(self, internal):
        """
            This is the class for disk usage management
        """
        self.i = internal

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
        return int(min_free_space) - disk_status[statvfs.F_BFREE] * 4096
        # Or something like this xDD TODO AND/OR FIXME

    def delete_files(self, files):
        """
            Delete an array of files
        """
        for lfile in files:
            os.unlink(lfile)

    def list_files(self, ldir):
        """
            Return files in a ldirectory, in a list of lists with all the files info
        """
        self.i.log('DEBUG', "Listing files in %s" %ldir)
        res = list()
        for root, ldirs, files in os.walk(ldir):
            [ res.append(root + lfile,
             mimetypes.guess_type( root + lfile)[0], lfile.__getitem__(0),
             _status(lfile).s.ctime, _status(lfile).st_size) for lfile in files]
        res.sort( lambda a, b: cmp(a[3], b[3]) )
        return res

    def _status(self, lfile):
        """
            Return data of a file to be used within _list_files
        """
        return os.stat_result(os.stat(lfile))

    def get_old_files(self, mainldir, ldir, freed=0, oldies=list()):
        """
            Get oldest files until we free neccesary space
        """

        to_free = self.to_free( self._get_disk_data(mainldir),
                self.i.cfg('minspace'))

        for lfile in self.list_files(self.i.cfg('main')):
            if freed < to_free:
                break
            freed += lfile[2]
            oldies.append(lfile)

        if oldies:
            self.i.log('INFO', "Current old files to delete: " + oldies)

        return oldies


class CopisterioDaemon():
    """
       Main class for the daemon
    """
    def __init__(self, cfile):
        """
            This is copisterio Daemon class
        """

        self.i = CopisterioInternal(cfile)
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
                self.i.cfg('main'), self.i.cfg('library')))

        for lfile in diskmanager.list_files(self.i.cfg('main')):

            if (os.path.exists( self.i.cfg('admdir') + os.sep +
                lfile[1] + os.sep + lfile[2] )):
                os.rename(self.i.cfg('tmpdir') + os.sep + lfile[0],
                       self.i.cfg('admdir') + os.sep + lfile[1] + \
                       os.sep + lfile[2])
                os.chown(os.getgid(), os.getuid(), self.i.cfg('admdir') +\
                        os.sep + lfile[0])
                os.chmod(744, self.i.cfg('admdir') + os.sep + lfile[0])

            else:
                self.i.log('WARN', "File %s/%s exists" %(lfile[1], lfile[2]))

if not os.path.exists( os.environ['HOME'] + os.sep + "." + __config_file__ ):
    __config_file__ = __base_cfile__
else:
    __config_file__ = os.environ['HOME'] + os.sep + "." + __config_file__

CopisterioDaemon(__config_file__)
