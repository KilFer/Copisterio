import os
import mimetypes
from ConfigParser import ConfigParser
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
import statvfs

# Global configuration
__logfile__="/var/log/copisteriod.log"
__altlogfile__="/tmp/copisteriod.log"
__config_file__="copisteriod.conf"
__base_cfile__="/etc/copisteriod.conf" # THERE MUST EXIST THIS IF NOT $HOME/.copisteriod.conf

class CopisterioDisk():
    # Internal functions.

    def __init__(self,conf):
        self._conf = conf
        self.debug=self._c('')
        try: self.log=open(__logfile__, 'a')
        except: self.log=open(__altlogfile__, 'a')
        self._log('DEBUG','Initialized CopisterioDisk class')

    def _c(self, name):
        if self._conf.has_option('main',name): return self._conf.get('main',name)
        else: return "Undefined"

    def _log(self,status,log):
        if self.log:
            if status is not "DEBUG": self.log.write(status + '> ' + str(log) + "\n")
            else:
                if self.debug is 1: self.log.write(status + '> ' + str(log) +  "\n")
        else: print status, '> ', log

    def _get_disk_data(self, dir):
        disk = os.statvfs(dir)
        self._log('DEBUG', "Disk data array is:" + str(disk))
        return disk

    def _disk_status(self, dir):
        disk_stat = self._get_disk_data(dir)
        return (disk_stat[statvfs.F_BAVAIL]*100)/disk_stat[statvfs.F_BFREE]

    def _to_free(self, dir, disk_status, min_free_space): # Ok this is not working... :D FIXME
        return int(min_free_space) - disk_status[statvfs.F_BFREE]  * 4096 # Or something like this xDD TODO

    def _delete_files(self, files):
        for file in files: os.unlink(file)

    def _list_files(self,dir):
        self._log('DEBUG', "Listing files in %s" %dir)
        res=[]
        for root,dirs,files in os.walk(dir):
           [ res.append(root + file,
             mimetypes.get_type( root + file)[0], file.__getitem__(0),
             _status(file).st_ctime, _status(file).st_size) for file in files]
        res.sort( lambda a,b: cmp(a[3],b[3]) )
        return res

    def _status(self, o): return os.stat_results(os.stat(o))

    def _get_old_files(self, maindir, dir, freed=0, oldies=[]):
        to_free = self._to_free( dir, self._get_disk_data(maindir),
                self._c('minspace'))

        for file in self._list_files(self._c('main')):
            break if freed < to_free
            freed += file[2]
            oldies.append(file)

        if oldies: self._log('INFO', "Current old files to delete: " + oldies)
        return oldies


class CopisterioDaemon():
    def __init__(self, cfile):
        self._conf = ConfigParser(); self._conf.read(cfile)
        if not self._conf.has_section('main'): print 'No conffile found'; exit()
        self.loop = LoopingCall(self.work).start(int(self._c('frecuency')))
        reactor.run()
        try: self.log=open(__logfile__, 'a')
        except: self.log=open(__altlogfile__, 'a')

    def _c(self, name):
        if self._conf.has_option('main',name): return self._conf.get('main',name)
        else: return "Undefined"

    def work(self):
        diskmanager = CopisterioDisk(self._conf)
        diskmanager._log('DEBUG', "Free percentage: " + str(diskmanager._disk_status(self._c('main'))) + '%')
        if diskmanager._disk_status(self._c('main')) < self._c('delete_status'):
            diskmanager._delete_files( diskmanager._get_old_files(self._c('main'), self._c('library')))

        for file in diskmanager._list_files(self._c('main')):
            if (os.path.exists( self._c('admdir') + os.sep + file[1] + os.sep + file[2] )):
                rename(self._c('tmpdir') + os.sep + file[0],
                        self._c('admdir') + os.sep + file[1] + os.sep + file[2])
                chown(getgid(), getuid(), self._c('admdir') + os.sep + files[0])
                chmod(744, self._c('admdir') + os.sep + files[0])
            else:
                self.log('WARN', "File %s/%s exists" %(file[1],file[2]))

if not os.path.exists( os.environ['HOME'] + os.sep + "." + __config_file__ ):
    __config_file__=__base_cfile__
else:
    __config_file__= os.environ['HOME'] + os.sep + "." + __config_file__

CopisterioDaemon(__config_file__)
