from unittest import TestCase

from chat.domain.valueobject.pdfdataloader import PdfDataloader


class TestPdfDataloader(TestCase):
    def test_This_PDF_has_18_pages(self):
        dataloader = PdfDataloader('./doj_cloud_act_white_paper_2019_04_10.pdf', ['\n\n \n'])
        self.assertEqual(18, len(dataloader.data))
        print(dataloader.data)
