# Review remarks

## General remarks
- the majority of remarks are in code
- unfortunately the project is not executable yet (ran app.py after installing requirements)
  - after checking that I have to run `create_database.py` first it ran. Please add a user guide to teh README.md! 
- the `.idea` should not be part of the project
- no pattern yet... easiest to implement in `create_database.py`
  - my suggestion is to use the strategy pattern to handle the databases
  - The Strategy Interface would look like something like this:
```python
import pandas as pd
from abc import ABC, abstractmethod


class DbHandler(ABC):
  
    def __init__(
        self,
        name: str,  # like "routines.db"
        create_query: str,
        insert_query: str,
    ):
        ... # you can also keep name and queries as constants 
  
    @abstractmethod
    def create(self):
        ...
  
    def update(self):  # contains code from `DataLoader.update_data()`
        ...
  
    def query(self) -> pd.DataFrame:  # contains code from `DataLoader.get_data()`
        ...
```
  - then you can separate modules like this:
    - db_handlder.py
    - rider_db_handler.py containing `RiderDbHandler(DbHandler)`
    - rider_routine.py containing `RiderRoutineDbHandler(DbHandler)`
    - routine.py containing `RoutineDbHandler(DbHandler)`
    - load_data.py would be not necessary anymore, as code is part of `DbHandler` 
- docx & draw.io are not typically part of a repository. This should be described in the README.md
  - for images, which you want to show in your README.md, put them in a dedicated "images" folder to keep the root folder of the project clean
- many obvious comments and magic values
  - please check (old) slides to ensure you stay in code and projecture structure style


## Grading criteria remarks
- Readme is missing. I gave some comments above, what should be in the README.md
  - please ensure that an installation and usage guide is in there as well (see installation guide here: https://github.com/Practical-Python-Development/minesweeper)
- please run mypy and ruff to check if your code adheres to coding style
- please add a few more tests of the core functionality. One including the pattern usage.
- I highlighted where I want to see docstrings. basically in every method, function or class
- comments should exist as little as possible (check coding style)
  - therefore, please remove all my comments before we will grate the project
- Currently, there is no pattern in use. Please use my suggestion for example. the Singleton Pattern could be also an option for the DataLoader. 