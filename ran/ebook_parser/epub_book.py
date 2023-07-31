import os, math, zipfile
from ebook_parser.ebook import *
from xml.etree import ElementTree as ET

class EpubBook(AbstractEBook):
    _CONTENT_FILE_NAME = 'content.opf'
    _MIMETYPE_FILE_NAME = 'mimetype'
    _CONTAINER_FILE_PATH = 'META-INF/container.xml'
    _EPUB_VERSION_2 = 2
    _EPUB_VERSION_3 = 3

    def __init__(self, full_path) -> None:
        super().__init__(full_path)

        self._book_zip_file: zipfile.ZipFile = None
        self._oebps_folder_list: list[str] = []
        self._epub_version: int = 3 #epub标准默认3
        self._open(full_path)
        self._parse_meta()
    
    def get_toc(self) -> EBookTableOfContents:
        content_path = self._oebps_folder_list[0] + EpubBook._CONTENT_FILE_NAME

        file_list = self._book_zip_file.namelist()
        if content_path not in file_list:
            print("epub文件不完整")
        
        et_root = ET.fromstring(self._book_zip_file.read(content_path))
        namespaces = {'dc': 'http://purl.org/dc/elements/1.1/', 'opf': 'http://www.idpf.org/2007/opf'}

        if EpubBook._EPUB_VERSION_2 == self._epub_version:
            et_toc = et_root.findall("opf:manifest/opf:item[@id='ncx']", namespaces)
            toc_file = et_toc[0].attrib['href']
            toc_path = self._oebps_folder_list[0] + toc_file
            return self._parse_toc_2(toc_path)
        else:
            et_toc = et_root.findall("opf:manifest/opf:item[@properties='nav']", namespaces)
            toc_file = et_toc[0].attrib['href']
            toc_path = self._oebps_folder_list[0] + toc_file
            return self._parse_toc_3(toc_path)
    
    def get_content(self, location) -> str:
        return self._book_zip_file.read(location).decode('utf-8')

    def _open(self, full_path) -> None:
        if not os.path.exists(full_path):
            print('电子书文件不存在')
        
        self._book_zip_file = zipfile.ZipFile(full_path, 'r')

        if not self._check_epub_spec():
            print('文件非epub格式')

        self._oebps_folder_list = self._find_oebps_folder_list()
    
    def _parse_meta(self):
        content_path = self._oebps_folder_list[0] + EpubBook._CONTENT_FILE_NAME

        file_list = self._book_zip_file.namelist()
        if content_path not in file_list:
            print("epub文件不完整")
        
        et_root = ET.fromstring(self._book_zip_file.read(content_path))
        self._epub_version = math.floor(float(et_root.attrib['version']))
        namespaces = {'dc': 'http://purl.org/dc/elements/1.1/', 'opf': 'http://www.idpf.org/2007/opf'}
        et_metadata = et_root.find('opf:metadata', namespaces)

        et_title = et_metadata.find('dc:title', namespaces)
        if et_title is not None:
            self.title = et_title.text
        
        self._find_author(et_metadata)
    
    def _check_epub_spec(self) -> bool:
        file_list = self._book_zip_file.namelist()

        if EpubBook._MIMETYPE_FILE_NAME not in file_list:
            return False

        mimetype = self._book_zip_file.read(EpubBook._MIMETYPE_FILE_NAME).decode('utf-8')
        if mimetype != 'application/epub+zip':
            return False

        if EpubBook._CONTAINER_FILE_PATH not in file_list:
            return False
        
        return True
    
    def _find_oebps_folder_list(self) -> list[str]:
        root = ET.fromstring(self._book_zip_file.read(EpubBook._CONTAINER_FILE_PATH))
        namespaces = {'container': 'urn:oasis:names:tc:opendocument:xmlns:container'}
        rootfiles = root.findall('container:rootfiles', namespaces)
        if not rootfiles:
            print('解析“META-INF/container.xml”文件失败')
        rootfile = rootfiles[0].findall('container:rootfile', namespaces)
        if not rootfile:
            print('解析“META-INF/container.xml”文件失败')
        return list(map(lambda x: self._cut_oebps_folder(x.get('full-path')), rootfile))
    
    def _cut_oebps_folder(self, path) -> str:
        folder_index = path.rfind('/')
        return path if folder_index == -1 else path[:folder_index + 1]
    
    def _find_author(self, et_metadata) -> None:
        namespaces = {'dc': 'http://purl.org/dc/elements/1.1/', 'opf': 'http://www.idpf.org/2007/opf'}
        et_creators = et_metadata.findall('dc:creator', namespaces)
        for et in et_creators:
            self.author.append(EBookAuthor(et.text))
    
    def _parse_toc_2(self, toc_file_path) -> EBookTableOfContents:
        toc = EBookTableOfContents()

        root = ET.fromstring(self._book_zip_file.read(toc_file_path))
        namespaces = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
        et_nav_map = root.find('ncx:navMap', namespaces)
        if et_nav_map is not None:
            toc.add_items(self._parse_toc_2_nav_map(et_nav_map))

        return toc
    
    def _parse_toc_2_nav_map(self, et_parent) -> list[EBookTableOfContentItem]:
        re = []
        namespaces = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
        et_nav_point_list = et_parent.findall('ncx:navPoint', namespaces)
        for et_nav_point in et_nav_point_list:
            toc_item = self._parse_toc_2_nav_point(et_nav_point)
            re.append(toc_item)
            toc_item.add_children(self._parse_toc_2_nav_map(et_nav_point))
        return re
    
    def _parse_toc_2_nav_point(self, et_nav_point) -> EBookTableOfContentItem:
        namespaces = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
        text = et_nav_point.findall('ncx:navLabel/ncx:text', namespaces)[0].text
        src = et_nav_point.findall('ncx:content', namespaces)[0].get('src')
        location = self._oebps_folder_list[0] + src
        return EBookTableOfContentItem(text, location)

    def _parse_toc_3(self, toc_file_path):
        pass

if __name__ == "__main__":
    book = EpubBook('D://5%的改变.epub')
    toc = book.get_toc()
    for c in toc.toc:
        print(c.location)
        if len(c.clildren) > 0:
            for cc in c.clildren:
                print(cc.location)

