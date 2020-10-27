## Добавление поддержки нового типа документов в Dedoc

Предположим, необходимо добавить поддержку нового типа newtype.
Существует несколько способов обработки документов:
* **Converter** - можно написать конвертер из одного формата в другой;
* **Reader** - можно написать специальный обработчик конкретного формата;
* **AttachmentExtractor** - если документ данного типа содержит вложения, 
извлекатор вложений позволит их извлечь.

### Общая схема добавления Converter
1. Внутри `dedoc/converters/concrete_converters` создать файл `newtype_converter.py`, 
в котором реализовать класс `NewtypeConverter`. Данный класс должен быть наследником 
абстрактного класса `BaseConverter`, код которого можно посмотреть в `dedoc/converters/base_converter.py`.
В конструкторе класса необходимо вызвать конструктор базового класса.
    ```python
    from dedoc.converters.base_converter import BaseConverter
   
    class NewtypeConverter(BaseConverter):
       def __init__(self):
           super().__init__()
    ```
2. Реализовать методы `can_convert()` и `do_convert()` для конвертации других форматов в данный формат.

    ```python
    class NewtypeConverter(BaseConverter):
   
       def __init__(self):
           super().__init__()

       def can_convert(self, 
                       extension: str, 
                       mime: str) -> bool:
           pass  # код метода
       def do_convert(self, 
                      tmp_dir: str, 
                      filename: str, 
                      extension: str) -> str:
            pass  # код метода
    ```
    * **Метод `can_convert()`** проверяет, может ли новый конвертер обработать файл, 
    например, можно возвращать True если расширение файла соответствует тому расширению,
    из которого производится конвертация.
    * **Метод `do_convert()`** выполняет необходимое преобразование файла. 
    Можно не опасаться того, что в имени файла встретятся пробелы или другие нежелательные символы,
    так как файл был переименован менеджером.
    
3. Добавить конвертер в `dedoc/manager_config.py`.

   У `_config` в поле `converters` наряду с другими конвертерами необходимо добавить `NewtypeConverter()`.
   
### Общая схема добавления Reader
1. Добавить в `dedoc/readers` новый пакет `newtype_reader`, где `newtype` - тип, поддержку которого требуется добавить.
2. Внутри `dedoc/readers/newtype_reader` создать файл `newtype_reader.py`, 
в котором реализовать класс `NewtypeReader`. Данный класс должен быть наследником 
абстрактного класса `BaseReader`, код которого можно посмотреть в `dedoc/readers/base_readers.py`.
    ```python
    from dedoc.readers.base_reader import BaseReader
   
    class NewtypeReader(BaseReader):
        pass
    ```
3. Реализовать методы `can_read()` и `read()` в соответствии с тем, как обрабатывается нужный формат.

    ```python
    class NewtypeReader(BaseReader):
    
        def can_read(self, 
                     path: str, 
                     mime: str, 
                     extension: str, 
                     document_type: Optional[str]) -> bool:
            pass  # код метода
        def read(self,
                 path: str,
                 document_type: Optional[str] = None,
                 parameters: Optional[dict] = None) -> Tuple[UnstructuredDocument, bool]:
            pass  # код метода
    ```
    * **Метод `can_read()`** проверяет, можно ли обработать пришедший файл, 
    для этого может понадобиться путь до файла, информация о расширении файла, 
    mime и тип документа (передаётся пользователем в запросе, например можно обрабатывать
    только документы-научные статьи). Желательно сделать этот метод быстрым, 
    так как он будет вызываться часто, в том числе на документы других типов. 
    * **Метод `read()`** должен сформировать `UnstructuredDocument`.
    Метод так же должен сообщить может ли данный документ содержать вложения.
    
4. Добавить обработчик типа в `dedoc/manager_config.py`.

   У `_config` в поле `readers` наряду с другими обработчиками необходимо добавить `NewtypeReader()`.
   
### Общая схема добавления AttachmentExtractor
1. Внутри `dedoc/attachments_extractors/concrete_attach_extractors` создать файл `newtype_attachment_extractor.py`, 
в котором реализовать класс `NewtypeAttachmentsExtractor`. Данный класс должен быть наследником 
абстрактного класса `BaseConcreteAttachmentsExtractor`, код которого можно посмотреть в `dedoc/attachments_extractors/base_concrete_attach_extractor.py`.
    ```python
    from dedoc.attachments_extractors.base_concrete_attach_extractor import BaseConcreteAttachmentsExtractor
   
    class NewtypeAttachmentsExtractor(BaseConcreteAttachmentsExtractor):
        pass
    ```
2. Реализовать методы `can_extract()` и `get_attachments()` 
в соответствии с особенностями извлечения вложений для данного формата.

    ```python
    from typing import List, Union
   
    class NewtypeAttachmentsExtractor(BaseConcreteAttachmentsExtractor):
    
        def can_extract(self, 
                        mime: str, 
                        filename: str) -> bool:
            pass  # код метода
        def get_attachments(self, 
                            tmpdir: str, 
                            filename: str, 
                            parameters: dict) -> List[List[Union[str, bytes]]]:
            pass  # код метода
    ```
    * **Метод `can_extract()`** проверяет, можно ли извлечь вложения из пришедшего файла,
    то есть является ли тип файла типом, который может обрабатываться данным извлекатором.
    * **Метод `get_attachments()`** должен вернуть список вложений, которые получилось 
    извлечь из документа: для каждого вложения возвращается имя файла-вложения и его бинарное содержимое.
    
3. Добавить извлекатор вложений в `dedoc/manager_config.py`.

   В список `concrete_attachments_extractors` наряду с другими извлекаторами необходимо добавить `NewtypeAttachmentsExtractor()`.
   
### Пример добавления обработчиков pdf/djvu

Предположим, что мы хотим добавить возможность обработки документов в формате pdf/djvu с текстовым слоем.
Мы не хотим разбираться с двумя форматами, тем более djvu хорошо конвертируется в pdf. 
Предлагается следующая последовательность действий:
1. Написание конвертера из djvu в pdf DjvuConverter.
2. Написание PdfReader.
3. Написание PdfAttachmentsExtractor.
4. Добавление реализованных обработчиков в конфиг менеджера.

Опишем каждый шаг более подробно.

#### Написание конвертера из djvu в pdf DjvuConverter

Внутри `dedoc/converters/concrete_converters` создаем файл `djvu_converter.py`,
в котором нам предстоит реализовать класс `DjvuConverter`

```python
from dedoc.converters.base_converter import BaseConverter
   
class DjvuConverter(BaseConverter):
    def __init__(self):
       super().__init__()
```

Реализовываем необходимые методы: 
* `can_convert()`: будем возвращать True если расширение файла `.djvu`.
Для более аккуратной работы с расширениями рекомендуется ознакомиться с файлом `dedoc/extensions.py`.
* `do_convert()`: будем использовать утилиту `ddjvu` (для ОС linux) и вызывать её через `os.system`.
Метод `_await_for_conversion()` гарантирует то, что сконвертированный файл сохранен.

```python
import os
from dedoc.converters.base_converter import BaseConverter

class DjvuConverter(BaseConverter):

   def __init__(self):
       super().__init__()

   def can_convert(self, 
                   extension: str, 
                   mime: str) -> bool:
       return extension == '.djvu'

   def do_convert(self, 
                  tmp_dir: str, 
                  filename: str, 
                  extension: str) -> str:
        os.system(f"ddjvu -format=pdf {tmp_dir}/{filename}{extension} {tmp_dir}/{filename}.pdf")
        self._await_for_conversion(filename + '.pdf', tmp_dir)
        return filename + '.pdf'
```

#### Написание PdfReader

Добавляем в `dedoc/readers` новый пакет `pdf_reader`.
Внутри `dedoc/readers/pdf_reader` создаем файл `pdf_reader.py`, 
в котором нам предстоит реализовать класс `PdfReader`

```python
from dedoc.readers.base_reader import BaseReader

class PdfReader(BaseReader):
    pass
```

Реализовываем необходимые методы: 
* `can_read()`: 
* `read()`: будем возвращать True, так как pdf-документ может содержать вложения.
                
```python
from dedoc.extensions import recognized_extensions, recognized_mimes
from dedoc.data_structures.paragraph_metadata import ParagraphMetadata
from dedoc.data_structures.table import Table
from dedoc.data_structures.table_metadata import TableMetadata
from dedoc.data_structures.unstructured_document import UnstructuredDocument
from dedoc.readers.base_reader import BaseReader
from dedoc.data_structures.line_with_meta import LineWithMeta
from dedoc.data_structures.annotation import Annotation
from dedoc.readers.utils.hierarch_level_extractor import HierarchyLevelExtractor
from typing import Tuple, Optional

class PdfReader(BaseReader):
    
    def can_read(self, 
                 path: str, 
                 mime: str, 
                 extension: str, 
                 document_type: Optional[str]) -> bool:
        return ((extension in recognized_extensions.pdf_like_format 
                 or mime in recognized_mimes.pdf_like_format) and not document_type)

    def read(self,
             path: str,
             document_type: Optional[str] = None,
             parameters: Optional[dict] = None) -> Tuple[UnstructuredDocument, bool]:
        pass
```
#### Написание PdfAttachmentsExtractor

Внутри `dedoc/attachments_extractors/concrete_attach_extractors` 
создаем файл `pdf_attachment_extractor.py`, 
в котором нам предстоит реализовать класс `PdfAttachmentsExtractor`.

```python
from dedoc.attachments_extractors.base_concrete_attach_extractor import BaseConcreteAttachmentsExtractor

class PdfAttachmentsExtractor(BaseConcreteAttachmentsExtractor):
    pass
```

Реализовываем необходимые методы: 
* `can_extract()`: 
* `get_attachments()`:

```python
from typing import List, Union
from dedoc.attachments_extractors.base_concrete_attach_extractor import BaseConcreteAttachmentsExtractor

class NewtypeAttachmentsExtractor(BaseConcreteAttachmentsExtractor):

    def can_extract(self, 
                    mime: str, 
                    filename: str) -> bool:
        pass  # код метода

    def get_attachments(self, 
                        tmpdir: str, 
                        filename: str, 
                        parameters: dict) -> List[List[Union[str, bytes]]]:
        pass  # код метода
```

#### Добавление реализованных обработчиков в конфиг менеджера

#### Упражнение