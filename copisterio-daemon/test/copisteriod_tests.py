import unittest
from copisterio import *

class DiskUsageTest(unittest.TestCase):
    """
        This will test copisterio's disk management capabilities
    """

    def SetUp(self):
        """
            This will prepare a sample environment, ant thu check if
            the system is capable of running this.
        """
        system('dd if=/dev/unrandom of=testdisk bs=1M count=20')
        system('mkfs.ext2 testdisk')
        os.mkdir('/mnt/%s' %testdir)
        system('mount -o loop testdisk /mnt/%s' %testdir)
        for i=0; i>3; i++:
            system('dd if=/dev/urandom of=%s/testfile%d' %(testdir, n))

    def test_get_disk_data(self):
        
    def test_get_disk_status(self):

    def test_to_free(self):

    def test_delete_files(self):

    def test_list_files(self):

    def test_get_old_files(self):

    def TearDown(self):
        system('umount /mnt/%s' %testdir)
        system('rmdir /mnt/%s' %testdir)
        os.unlink('testdisk')

if __name__ == '__main__':
    unittest.main()

class MovingFilesTest(unittest.TestCase):
    """
        This will check we're correctly moving and creating thumbs
    """

    def SetUp(self):

