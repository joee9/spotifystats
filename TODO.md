## structs.py

- change pickle serialization to JSON to allow for functions like "load_db" and "dump" to be run from other files
- take care of case when daily summary leads to yearly summary and the current monthly db is passed to the yearly function to avoid recalculating values unncecessarily
- add kwparam such that database.dump() can be dumped to user chosen yyyymm