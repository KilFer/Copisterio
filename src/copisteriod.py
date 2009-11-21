import os
import mimetypes
from ConfigParser import ConfigParser
from twisted.internet.task import LoopingCall
import statvfs

# Global configuration
__logfile__="/var/log/copisteriod.log"
__altlogfile__="/tmp/copisteriod.log"
__config_file__="foo"

# TODO ADD KARMA

class CopisterioDisk():
    # Internal functions.

    def __init__(self,conf):
        self._conf = conf
        try: self.log=open(__logfile__, 'a')
        except: self.log=open(__altlogfile__, 'a')

    def _c(self, name): return self._conf.get('main',name)

    def _log(self,status,log):
        try:
            self.log
            self.log.write(status, '> ', log)
        except:
            print status, '> ', log

    def _get_disk_data(self, dir):
        disk = os.statvfs(dir)
        self._log('INFO', disk )
        return disk

    def _disk_status(self, dir):
        disk_stat = self._get_disk_data(dir)
        self._log('INFO', disk_stat[statvfs.F_BAVAIL])
        self._log('INFO', disk_stat[statvfs.F_BFREE])
        return (disk_stat[statvfs.F_BAVAIL]*100)/disk_stat[statvfs.F_BFREE]

    def _to_free(self, dir, disk_status, min_free_space):
        return min_free_space - disk_status[statvfs.B_FREE]*4096 # Or something like this xDD TODO

    def _delete_files(self, files):
        for file in files: os.unlink(file)

    def _list_files(self,dir):
        res=[]
        for root,dirs,files in os.walk(dir):
           [ res.append(root + file,
             mimetypes.get_type( root + file)[0], file.__getitem__(0),
             _status(file).st_ctime, _status(file).st_size) for file in files]
        res.sort( lambda a,b: cmp(a[3],b[3]) )
        return res

    def _status(self, o): return os.stat_results(os.stat(o))

    def _get_old_files(self,maindir,dir):
        freed = 0
        oldies=[]

        to_free = self._to_free( dir, self._disk_status(self._c('main')),
                self._c('minspace'))

        while(to_free < freed):
            files=self._list_files(self._c('main'))
            for file in oldies: freed += ofile[2]
        return oldies


class CopisterioDaemon():
    def __init__(self, cfile):
        self._conf = ConfigParser(); self._conf.read(cfile)
        self.loop = LoopingCall(self.work).start(self._c('frecuency'))
        try: self.log=open(__logfile__, 'a')
        except: self.log=open(__altlogfile__, 'a')

    def _c(self, name): return self._conf.get('main',name)

    def work(self):
        diskmanager = CopisterioDisk(self._conf) # Yeah, yeah, I know it would be better to just make the object access to the parent's _c function, but I'm lazy now, and don't remember how's done :D
        diskmanager._log('INFO', "Free percentage: " + str(diskmanager._disk_status(self._c('main'))) + '%')
        if diskmanager._disk_status(self._c('main')) < self._c('delete_status'):
            diskmanager._delete_files( diskmanager._get_old_files(self._c('main'), self._c('library')))

        for file in self._list_files():
            rename(self._c('tmpdir') + os.sep + file[0],
                    self._c('admdir') + os.sep + file[1] + os.sep + file[2])
            chown(getgid(), getuid(), self._c('admdir') + os.sep + files[0])
            chmod(744, self._c('admdir') + os.sep + files[0])
        #Check file does not exist

CopisterioDaemon(__config_file__)
