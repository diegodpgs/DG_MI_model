# DG_MI_model


This project induce dependency grammar in two ways: using Mutual Information and DMV algorithm. The code used for DMV can be found in this <a href="https://github.com/jxhe/struct-learning-with-flow/">repository</a>.




<h1>Indigenous Training</h1>

The training employs languages with a limited amount of data, and the original dataset lacks both a training and test set. Consequently, we conduct cross-validation using the available data. <br>


First, run the cv.py code to create cross validation data.

```
python3 cv.py --PATH_data ~/ProjectGit/DG_MI_model/data --PATH_dest ~/ProjectGit/DG_MI_model/data_cv
```

 <b>INPUT: </b> python3 run.py --PATH /home/diego/ProjectGit/DG_MI_model/data/ --max_d_r 2,3,4  --max_s 10,40 <br>
 <b> OUTPUT:</b> language;UDA;DDA;sentence lenght;dependency distance
