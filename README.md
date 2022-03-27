# Weightipy

Weightipy is a cut down version of [Quantipy3](https://github.com/Quantipy/quantipy3) for weighting people data using the RIM (iterative raking) algorithm.

#### Origins
- Quantipy was concieved of and instigated by Gary Nelson: http://www.datasmoothie.com

#### Contributors
- Alexander Buchhammer, Alasdair Eaglestone, James Griffiths, Kerstin Müller : https://yougov.co.uk
- Datasmoothie’s Birgir Hrafn Sigurðsson and [Geir Freysson](http://www.twitter.com/@geirfreysson): http://www.datasmoothie.com

## Installation

`pip install weightipy`

or

`python3 -m pip install weightipy`

Note that the package is called __weightipy__ on pip.

#### Create a virtual envirionment

If you want to create a virtual environment when using Weightipy:

conda
```python
conda create -n envwp python=3
```

with venv
```python
python -m venv [your_env_name]
 ```

## 5-minutes to Weightipy

**Get started**

#### Weighting
If your data hasn't been weighted yet, you can use Weightipy's RIM weighting algorithm.

Assuming we have the variables `gender` and `agecat` we can weight the dataset with these two variables:

```Python
import weightipy as wp

age_targets = {'agecat':{1:5.0, 2:30.0, 3:26.0, 4:19.0, 5:20.0}}
gender_targets = {'gender':{0:49, 1:51}}
scheme = wp.Rim('gender_and_age')
scheme.set_targets(targets=[age_targets, gender_targets])

df_weighted = wp.weight_dataframe(
    df=my_df,
    scheme=scheme,
    weight_column="weights"
)
efficiency = wp.weighting_efficiency(df_weighted["weights"])

```
Or by using the underlying functions that will give more access to reports etc:
```Python
...

my_df["identity"] = range(len(my_df))
engine = wp.WeightEngine(data=df)
engine.add_scheme(scheme=scheme, key="identity", verbose=False)
engine.run()
df_weighted = engine.dataframe()
col_weights = f"weights_{scheme.name}"

efficiency = wp.weighting_efficiency(df_weighted[col_weights])

print(engine.get_report())

Weight variable       weights_gender_and_age
Weight group                  _default_name_
Weight filter                           None
Total: unweighted                 582.000000
Total: weighted                   582.000000
Weighting efficiency               60.009826
Iterations required                14.000000
Mean weight factor                  1.000000
Minimum weight factor               0.465818
Maximum weight factor               6.187700
Weight factor ratio                13.283522
```

# Contributing

The test suite for Weightipy can be run with the command

`python3 -m pytest tests`

But when developing a specific aspect of Weightipy, it might be quicker to run (e.g. for the DataSet)

`python3 -m unittest tests.test_rim`

Tests for unsupported features are skipped, [see here for what tests are supported](SupportedFeaturesPython3.md).

We welcome volunteers and supporters. Please include a test case with any pull request, especially those that run calculations.
