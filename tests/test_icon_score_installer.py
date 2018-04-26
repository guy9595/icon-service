import unittest
from icon.iconservice.iconscore.icon_score_installer import *
from icon.iconservice.base.address import Address


class TestICONSCOREINSTALLER(unittest.TestCase):
    def setUp(self):
        self.installer = IconScoreInstaller('./')
        self.address = Address('cx', bytes.fromhex("1234123412341234123412341234123412341234"))
        self.archive_path = "./test.zip"
        self.archive_path2 = "./test_bad.zip"
        self.score_root_path = os.path.join(self.installer.icon_score_root_path, str(self.address))

        self.installer2 = IconScoreInstaller('/')
        self.address2 = Address.from_string("cx1234123412341234123412341234123412341234")

    def test_write_zipfile_with_bytes(self):
        write_file_first_time_result = self.installer.\
            write_zipfile_with_bytes(self.score_root_path, self.installer.read_zipfile_as_byte(self.archive_path))
        self.assertTrue(os.path.isfile(self.score_root_path))

        self.assertRaises(ScoreInstallWriteZipfileException, self.installer.write_zipfile_with_bytes
                          , self.score_root_path, self.installer.read_zipfile_as_byte(self.archive_path))

        self.installer.remove_exists_archive(self.score_root_path)

        self.assertRaises(ScoreInstallWriteZipfileException, self.installer.write_zipfile_with_bytes,
                          './', self.installer.read_zipfile_as_byte(self.archive_path))

    def test_remove_exists_archive(self):
        self.installer.write_zipfile_with_bytes(self.score_root_path
                                                , self.installer.read_zipfile_as_byte(self.archive_path))
        self.installer.remove_exists_archive(self.score_root_path)
        self.assertFalse(os.path.isfile(self.score_root_path))

    def test_install(self):
        block_height1, transaction_index1 = 1234, 12
        score_id = str(block_height1) + "_" + str(transaction_index1)
        self.installer.install(self.address, self.installer.read_zipfile_as_byte(self.archive_path)
                               , block_height1, transaction_index1)
        install_path = os.path.join(self.score_root_path, score_id)
        self.assertEqual(True, os.path.exists(install_path))

        ret1 = self.installer.install(self.address, self.installer.read_zipfile_as_byte(self.archive_path)
                               , block_height1, transaction_index1)
        self.assertEqual(CONST_SCORE_EXISTS_ERROR_CODE, ret1)

        self.installer.remove_exists_archive(os.path.join('./', str(self.address)))

        ret2 = self.installer.install(self.address, self.installer.read_zipfile_as_byte(self.archive_path2)
                                      , block_height1, transaction_index1)
        self.assertEqual(CONST_EXTRACT_FILES_ERROR_CODE, ret2)

        ret3 = self.installer2.install(self.address2, self.installer.read_zipfile_as_byte(self.archive_path)
                                       , block_height1, transaction_index1)

        self.assertEqual(ret3, CONST_PERMISSION_ERROR_CODE)


if __name__ == "__main__":
    unittest.main()
