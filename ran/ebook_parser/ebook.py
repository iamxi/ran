
class EBookTableOfContentItem(object):
    def __init__(self, text: str, location: str) -> None:
        self.text = text
        self.location = location
        self.clildren: list[EBookTableOfContentItem] = []
    
    def add_children(self, children: list):
        self.clildren.extend(children)

class EBookTableOfContents(object):
    def __init__(self) -> None:
        self.items: list[EBookTableOfContentItem] = []
    
    def add_items(self, iteam: list[EBookTableOfContentItem]) -> None:
        self.items.extend(iteam)

class EBookMetaItem(object):
    def __init__(self, name: str, content: str) -> None:
        self.name = name
        self.content = content

class EBookMetaData(object):
    def __init__(self) -> None:
        self.data: list[EBookMetaItem] = []

class EBookAuthor(object):
    def __init__(self, first_name, middle_name, last_name) -> None:
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.full_name = self.first_name + ' ' + self.middle_name + ' ' + self.last_name
    
    def __init__(self, name) -> None:
        self.full_name = name

class AbstractEBook(object):
    def __init__(self, full_path: str) -> None:
        self._full_path: str = full_path
        self.meta_data = EBookMetaData()
        self.title: str = ''
        self.subtitle: str = ''
        self.identifier: str = ''
        self.author: list[EBookAuthor] = []

    def get_toc(self) -> EBookTableOfContents:
        pass

    def get_content(self, location) -> str:
        pass

if __name__ == "__main__":
    book = AbstractEBook('D://5%的改变.epub')