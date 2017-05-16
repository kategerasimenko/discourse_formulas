# discourse_formulas
Discourse formulas detector for Russian (web-app and offline versions are available).

## Requirements
- python 3.x
- pymorphy2
- numpy
- pandas
- scipy
- scikit-learn 0.18.1

## Versions
### an app version
available at [web-corpora.net](http://web-corpora.net/wsgi3/discourse-formulas/).<br>
run `app.py`. <br>
in a web-application, it is possible to upload one text file and get a list of formulas in the table format: <br>
`filename  | left context  | formula` <br>
and a list of unique formulas with counts on the right.

### an offline version
run `run_this.py`. <br>
you will have to say whether the speakers should be deleted from the text (if it is a play). <br>
textfiles (can be as man as needed) should be put into the `texts` folder. <br>
result is a list of formulas compiled from all texts and each text with formula annotation - `{{formula!}}`. <br>
results are put into the `processed` folder which is created automatically.
