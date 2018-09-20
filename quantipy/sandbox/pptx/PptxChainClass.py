# encoding: utf-8
import re
import warnings
import numpy as np
import pandas as pd
from quantipy.sandbox.sandbox import Chain
import topy.core.ygpy.tools as t
t.use_encoding('utf-8')

BASE_COL = '@'
BASE_ROW = ['is_counts', 'is_c_base']
PCT_TYPES = ['is_c_pct', 'is_r_pct']
NOT_PCT_TYPES = ['is_stat']
CONTINUATION_STR = "(continued {})"
MAX_PIE_ELMS = 4


def float2String(input, ndigits=0):
    """
    Round and converts the input, if int/float or list of, to a string.
    :param
        input: int/float or list of int/float
        ndigits: number of decimals to round to
    :return:
        output: string or list of strings depeneding on the input
    """
    output = input
    if not isinstance(input, list):
        output = [output]
    output = map(lambda x: round(x, ndigits), output)
    output = map(int, output)
    output = map(str, output)
    if not isinstance(input, list):
        output = output[0]
    return output

def uniquify(l):
    """
    Return the given list without duplicates, retaining order.

    See Dave Kirby's order preserving uniqueifying list function
    http://www.peterbe.com/plog/uniqifiers-benchmark
    """

    seen = set()
    seen_add = seen.add
    uniques = [x for x in l if x not in seen and not seen_add(x)]

    return uniques


def strip_levels(df, rows=None, columns=None):
    """
    Function that strips a MultiIndex DataFrame for specified row and column index
    Can be used with all DP-systems
    :param
    rows: Int, default None
        Row index to remove
    columns: Int, default None
        Column index to remove
    :return:
    df_strip: A pandas.Dataframe
        The input dataframe stripped for specified levels
    """
    df_strip = df.copy()
    if rows is not None:
        if df_strip.index.nlevels > 1:
            df_strip.index = df_strip.index.droplevel(rows)
    if columns is not None:
        if df_strip.columns.nlevels > 1:
            df_strip.columns = df_strip.columns.droplevel(columns)
    return df_strip


def as_numeric(df):
    """
    Runs through all values in input DataFrame and replaces
    ',' to '.'
    '%' to ''
    '-' to '0'
    '*' to '0'
    Can be used with all DP-systems
    :param
    df: Pandas.Dataframe
        A dataframe of any structure, also multiindex
    :return:
    df: A pandas.Dataframe
        dataframe with values as float
    """

    if not df.values.dtype in ['float64', 'int64']:
        data = [[float(str(value).replace(',','.').replace('%','').replace('-','0').replace('*','0')) for value in values] for values in df.values]
        df = pd.DataFrame(data, index=df.index, columns=df.columns)
    return df.copy()


def is_grid_slice(chain):
    """
    Returns True if chain is a grid slice
    :param
        chain: the chain instance
    :return: True id grid slice
    """
    pattern = '\[\{.*?\}\].'
    found = re.findall(pattern, chain.name)
    if len(found) > 0 and chain._array_style == -1:
        return True


def get_indexes_from_list(lst, find, exact=True):
    """
    Helper function that search for element in a list and
    returns a list of indexes for element match
    E.g. get_indexes_from_list([1,2,3,1,5,1], 1) returns [0,3,5]
    :param
        lst: a list
        find: the element to find. Can be a list
        exact: If False the index are returned if find in value
    :return: a list of ints
    """
    if exact == True:
        return [index for index, value in enumerate(lst) if value == find]
    else:
        if isinstance(find,list):
            return [index for index, value in enumerate(lst) if set(find).intersection(set(value))]
        else:
            return [index for index, value in enumerate(lst) if find in value]


def auto_charttype(df, array_style, max_pie_elms=MAX_PIE_ELMS):
    """
    Auto suggest chart type based on dataframe analysis
    TODO Move this to Class PptxDataFrame()
    :param
        df: a Pandas Dataframe, not multiindex
        array_style: array_style as returned from Chain Class
    :return: charttype ('bar_clustered', 'bar_stacked', 'bar_stacked_100', 'pie')
    """
    if array_style == -1: # Not array summary
        chart_type = 'bar_clustered'
        if len(df.index.get_level_values(-1)) <= max_pie_elms:
            if len(df.columns.get_level_values(-1)) == 1:
                chart_type = 'pie'
    else: # Array Sum
        chart_type = 'bar_stacked_100'
        # TODO _auto_charttype - return 'bar_stacked' if rows not sum to 100

    return chart_type


def fill_gaps(l):
    """
    Return l replacing empty strings with the value from the previous position.
    """
    lnew = []
    for i in l:
        if i == '':
            lnew.append(lnew[-1])
        else:
            lnew.append(i)
    return lnew


def fill_index_labels(df):
    """
    Fills in blank labels in the second level of df's multi-level index.
    """
    _0, _1 = zip(*df.index.values.tolist())
    _1new = fill_gaps(_1)
    dfnew = df.copy()
    dfnew.index = pd.MultiIndex.from_tuples(zip(_0, _1new), names=df.index.names)
    return dfnew


def fill_column_values(df, icol=0):
    """
    Fills empty values in the targeted column with the value above it.
    """
    v = df.iloc[:,icol].fillna('').values.tolist()
    vnew = fill_gaps(v)
    dfnew = df.copy()
    dfnew.iloc[:,icol] = vnew
    return dfnew


class PptxDataFrame(object):
    """
    Class for handling the dataframe to be charted
    """

    def __init__(self, dataframe, cell_items, array_style, chart_type):
        self.array_style = array_style
        self.cell_items = cell_items
        self.df = dataframe # type: pd.DataFrame
        self.__frames = []
        self.chart_type = chart_type

    def __call__(self):
        return self.df

    def to_table(self, decimals=2, pct_decimals=2):

        df = self.df
        if df.empty:
            return self
        if self.array_style == -1:
            df = df.T

        rows_not_nan = pd.notnull(df).any(axis='columns')

        df = df.fillna('')

        # Percent type cells
        indexes = get_indexes_from_list(self.cell_items, PCT_TYPES, exact=False)
        df.iloc[:, indexes] *= 100
        df.iloc[:, indexes] = df.iloc[:, indexes].round(decimals=pct_decimals)
        if pct_decimals == 0:
            columns = df.columns[indexes].tolist()
            columns_to_int=dict(zip(columns, ['int'] * len(columns)))
            df[rows_not_nan] = df[rows_not_nan].astype(columns_to_int)

        # Not percent type cells
        indexes = get_indexes_from_list(self.cell_items, NOT_PCT_TYPES, exact=False)
        df.iloc[:, indexes] = df.iloc[:, indexes].round(decimals=decimals)
        if decimals == 0:
            columns = df.columns[indexes].tolist()
            columns_to_int=dict(zip(columns, ['int'] * len(columns)))
            df[rows_not_nan] = df[rows_not_nan].astype(columns_to_int)

        if self.array_style == -1:
            df = df.T

        self.df = df

        return self

    def select_categories(self,categories):

        if self.array_style == -1:
            df_copy=self.df.iloc[categories]
        else:
            df_copy = self.df.iloc[:,categories]

        pptx_df_copy = PptxDataFrame(df_copy,self.cell_items,self.array_style,self.chart_type)
        pptx_df_copy.chart_type = auto_charttype(df_copy, self.array_style)
        pptx_df_copy.cell_items = [self.cell_items[i] for i in categories]

        return pptx_df_copy

    def get_propstest(self):
        """
        Return a copy of the PptxDataFrame only containing sig testing type categories

        Returns
        -------
        A PptxDataFrame instance

        """
        row_list = get_indexes_from_list(self.cell_items, 'is_propstest', exact=False)
        #dont_want = get_indexes_from_list(self.cell_items, ['is_net', 'net', 'is_c_pct_sum'], exact=False)
        #not_net = get_indexes_from_list(self.cell_items, ['normal', 'expanded'], exact=False)

        #for x in dont_want:
        #    if x in row_list and x not in not_net:
        #        row_list.remove(x)

        return self.select_categories(row_list)

    def get_stats(self):
        """
        Return a copy of the PptxDataFrame only containing stat type categories

        Returns
        -------
        A PptxDataFrame instance

        """
        row_list = get_indexes_from_list(self.cell_items, 'is_stat', exact=False)
        #dont_want = get_indexes_from_list(self.cell_items, ['is_net', 'net', 'is_c_pct_sum'], exact=False)
        #not_net = get_indexes_from_list(self.cell_items, ['normal', 'expanded'], exact=False)

        #for x in dont_want:
        #    if x in row_list and x not in not_net:
        #        row_list.remove(x)

        return self.select_categories(row_list)

    def get_cpct(self):
        """
        Return a copy of the PptxDataFrame only containing column percentage categories

        Returns
        -------
        A PptxDataFrame instance

        """

        row_list = get_indexes_from_list(self.cell_items, 'is_c_pct', exact=False)
        dont_want = get_indexes_from_list(self.cell_items, ['is_net', 'net', 'is_c_pct_sum'], exact=False)
        not_net = get_indexes_from_list(self.cell_items, ['normal', 'expanded'], exact=False)

        for x in dont_want:
            if x in row_list and x not in not_net:
                row_list.remove(x)

        return self.select_categories(row_list)

    def get_nets(self):
        """
        Return a copy of the PptxDataFrame only containing net type categories

        Returns
        -------
        A PptxDataFrame instance

        """

        row_list = get_indexes_from_list(self.cell_items, ['is_net', 'net'], exact=False)
        dont_want = get_indexes_from_list(self.cell_items,
                                          ['is_propstest', 'calc', 'normal', 'is_c_pct_sum', 'is_counts', 'expanded'],
                                          exact=False)

        for x in dont_want:
            if x in row_list:
                row_list.remove(x)

        return self.select_categories(row_list)

    def get_means(self):
        """
        Return a copy of the PptxDataFrame only containing mean type categories

        Returns
        -------
        A PptxDataFrame instance

        """

        row_list = get_indexes_from_list(self.cell_items, ['is_mean'], exact=False)
        dont_want = get_indexes_from_list(self.cell_items, ['is_meanstest'], exact=False)

        for x in dont_want:
            if x in row_list:
                row_list.remove(x)

        return self.select_categories(row_list)

    def get(self, cell_items_request):
        """
        Method to get specific elements from chains dataframe

        Parameters
        ----------
        cell_items_request : str
            A string of comma separated cell types to return. Available types are 'c_pct, net, mean'

        Returns
        -------
        A PptxDataFrame instance

        """
        method_map = {'c_pct': self.get_cpct,
                      'pct': self.get_cpct,
                      'net': self.get_nets,
                      'nets': self.get_nets,
                      'mean': self.get_means,
                      'means': self.get_means,
                      'test': self.get_propstest,
                      'tests': self.get_propstest,
                      'stats': self.get_stats,
                      'stat': self.get_stats}
        # TODO Add methods for 'stddev', 'min', 'max', 'median', 't_means'
        available_cell_items = set(method_map.keys())
        if isinstance(cell_items_request, basestring):
            cell_items_request = re.sub(' +', '', cell_items_request)
            cell_items_request = cell_items_request.split(',')
        value_test = set(cell_items_request).difference(available_cell_items)
        if value_test:
            raise ValueError("Cell type: {} is not an available cell type. \n Available cell types are {}".format(cell_items_request, available_cell_items))

        list_of_dataframes = []
        cell_items = []

        for cell_item in cell_items_request:
            pptx_frame = method_map[cell_item]()
            #if pptx_frame.df.empty:
            #    continue
            list_of_dataframes.append(pptx_frame.df)
            cell_items += pptx_frame.cell_items

        new_df=pd.concat(list_of_dataframes, axis=0 if self.array_style==-1 else 1)

        new_pptx_df = PptxDataFrame(new_df, cell_items, self.array_style, self.chart_type)
        new_pptx_df.chart_type = auto_charttype(new_df, self.array_style)

        return new_pptx_df

    def get_kerstin(self, cell_types, sort=False):
        """
        Method to get specific elements from chains dataframe
        :param
            cel_types: A comma separated list of cell types to return. Available types are 'c_pct,net'
            sort: Sort the elements ascending or decending. Str 'asc', 'dsc' or False
        :return: df_copy, a Pandas dataframe. Element types will be returned in the order they are requested
        """
        # method_map = {'c_pct': self.get_cpct,
        #               'net': self.get_nets}
        # TODO Add methods for 'mean', 'stddev', 'min', 'max', 'median', 't_props', 't_means'
        available_celltypes = ['c_pct', 'net'] # set(method_map.keys())
        if isinstance(cell_types, basestring):
            cell_types = re.sub(' +', '', cell_types)
            cell_types = cell_types.split(',')
        value_test = set(cell_types).difference(available_celltypes)
        if value_test:
            msg = "Cell type: {} is not an available cell type.\n"
            msg += "Available cell types are {}"
            raise ValueError(msg.format(cell_types, available_celltypes))

        req_ct = []
        exclude = ['normal', 'calc', 'is_propstest', 'is_c_pct_sum', 'is_counts']
        if 'c_pct' in cell_types:
            req_ct.append('is_c_pct')
        if 'net' in cell_types:
            req_ct.extend(['is_net', 'net'])
        else:
            exclude.extend(['is_net', 'net'])

        row_list = get_indexes_from_list(self.cell_contents, req_ct, exact=False)
        dont_want = get_indexes_from_list(self.cell_contents, exclude, exact=False)
        row_list = [x for x in row_list if not x in dont_want]

        if self.array_style == -1:
            df_copy = self.iloc[row_list]
        else:
            df_copy = self.iloc[:, row_list]

        new_df = self.make_copy(data=df_copy.values, index=df_copy.index, columns=df_copy.columns)
        new_df.chart_type = auto_charttype(new_df, new_df.array_style)
        cell_contents = new_df.cell_contents
        new_df.cell_contents = [cell_contents[i] for i in row_list]

        # for cell_type in cell_types:
        #     frame = method_map[cell_type]()
        #     frames.append(frame)
        #     cell_contents += frame.cell_contents
        # new_df=pd.concat(frames, axis=0 if self.array_style==-1 else 1)

        pptx_df = self.make_copy(data=new_df.values, index=new_df.index, columns=new_df.columns)
        pptx_df.chart_type = auto_charttype(pptx_df, pptx_df.array_style)
        pptx_df.cell_contents = cell_contents

        return pptx_df

class PptxChain(object):
    """
    This class is a wrapper around Chain class to prepare for PPTX charting
    """

    def __init__(self, chain, is_varname_in_qtext=True, crossbreak=None, base_type='weighted', decimals=2, verbose=True):
        """
        :param
            chain: An instance of Chain class
            is_varname_in_qtext: Is var name included in the painted chain dataframe? (False, True, 'full', 'ignore')
            crossbreak:
        """
        self._chart_type = None
        self._sig_test = None # type: list # is updated by ._select_crossbreak()
        self.crossbreak_qtext = None # type: str # is updated by ._select_crossbreak()
        self.verbose = verbose
        self._decimals = decimals
        self._chain = chain
        self.name = chain.name
        self.xkey_levels = chain.dataframe.index.nlevels
        self.ykey_levels = chain.dataframe.columns.nlevels
        self.index_map = self._index_map()
        self.is_mask_item = chain._is_mask_item
        self.x_key_name = chain._x_keys[0]
        self.source = chain.source
        self._var_name_in_qtext = is_varname_in_qtext
        self.array_style = chain.array_style
        self.is_grid_summary = True if chain.array_style in [0,1] else False
        self.crossbreak = self._check_crossbreaks(crossbreak) if crossbreak else [BASE_COL]
        self.x_key_short_name = self._get_short_question_name()
        self.chain_df = self._select_crossbreak()
        self.xbase_indexes = self._base_indexes()
        self.xbase_labels = ["Base"] if self.xbase_indexes is None else [x[0] for x in self.xbase_indexes]
        self.xbase_count = ""
        self.xbase_label = ""
        self.xbase_index = 0
        self.ybases = None
        self.select_base(base_type=base_type)
        self.base_description = "" if chain.base_descriptions is None else chain.base_descriptions
        if self.base_description[0:6].lower() == "base: ": self.base_description = self.base_description[6:]
        self._base_text = None
        self.question_text = self.get_question_text(include_varname=False)
        self.chart_df = self.prepare_dataframe()
        self.continuation_str = CONTINUATION_STR
        self.vals_in_labels = False

    def __str__(self):
        str_format = ('Table name: {}'
                      '\nX key name: {}'
                      '\nShort x key name: {}'
                      '\nGrid summary: {}'
                      '\nQuestion text: {}'
                      '\nBase description: {}'
                      '\nBase label: {}'
                      '\nBase size: {}'
                      '\nRequested crossbreak: {}'
                      '\n')
        return str_format.format(getattr(self, 'name', 'None'),
                                 getattr(self, 'x_key_name', 'None'),
                                 getattr(self, 'x_key_short_name', 'None'),
                                 getattr(self, 'is_grid_summary', 'None'),
                                 getattr(self, 'question_text', 'None'),
                                 getattr(self, 'base_description', 'None'),
                                 getattr(self, 'xbase_labels', 'None'),
                                 getattr(self, 'ybases', 'None'),
                                 getattr(self, 'crossbreak', 'None'))

    def __repr__(self):
        return self.__str__()

    @property
    def sig_test(self):

        # Get the sig testing
        sig_df = self.prepare_dataframe()
        sig_df = sig_df.get_propstest()
        self._sig_test = sig_df.df.values.tolist()
        return self._sig_test

    @property
    def chart_type(self):
        if self._chart_type is None:
            self._chart_type = self.chart_df.chart_type
        return self._chart_type

    @chart_type.setter
    def chart_type(self, chart_type):
        self._chart_type = chart_type

    def select_base(self,base_type='weighted'):
        """
        Sets self.xbase_label and self.xbase_count
        :param base_type: str
        :return: None set self
        """
        if not self.xbase_indexes:
            msg = "No 'Base' element found"
            warnings.warn(msg)
            return None

        if base_type: base_type = base_type.lower()
        if not base_type in ['unweighted','weighted']:
            raise TypeError('base_type misspelled, choose weighted or unweighted')

        cell_contents = [x[2] for x in self.xbase_indexes]
        if base_type == 'weighted':
            index = [x for x, items in enumerate(cell_contents) if 'is_weighted' in items]
        else:
            index = [x for x, items in enumerate(cell_contents) if not 'is_weighted' in items]

        if not index: index=[0]

        # print "self.xbase_indexes: ", self.xbase_indexes
        total_base = self.xbase_indexes[index[0]][3]
        total_base = np.around(total_base, decimals=self._decimals)
        self.xbase_count = float2String(total_base)
        self.xbase_label = self.xbase_labels[index[0]]
        self.xbase_index = self.xbase_indexes[index[0]][1]
        self.ybases = self._get_y_bases()

    def _base_indexes(self):
        """
        Returns a list of label, index, cell_content and value of bases found in x keys.
        :return: list
        """

        cell_contents = self._chain.describe()
        if self.array_style == 0:
            row = min([k for k, va in cell_contents.items()
                              if any(pct in v for v in va for pct in PCT_TYPES)])
            cell_contents = cell_contents[row]

        # Find base rows
        bases = get_indexes_from_list(cell_contents, BASE_ROW, exact=False)
        skip = get_indexes_from_list(cell_contents, ['is_c_base_gross'], exact=False)
        base_indexes = [idx for idx in bases if not idx in skip] or bases

        # Show error if no base elements found
        if not base_indexes:
            #msg = "No 'Base' element found, base size will be set to None"
            #warnings.warn(msg)
            return None

        cell_contents = [cell_contents[x] for x in base_indexes]

        if self.array_style == -1 or self.array_style == 1:

            xlabels = self._chain.dataframe.index.get_level_values(-1)[base_indexes].tolist()
            base_counts = self._chain.dataframe.iloc[base_indexes, 0]

        else:

            xlabels = self._chain.dataframe.columns.get_level_values(-1)[base_indexes].tolist()
            base_counts = self._chain.dataframe.iloc[0, base_indexes]

        return zip(xlabels, base_indexes, cell_contents, base_counts)

    def _index_map(self):
        """
        Map not painted index with painted index into a list of tuples (notpainted, painted)
        :return:
        """
        if self._chain.painted:  # UnPaint if painted
            self._chain.toggle_labels()
        if self._chain.array_style == -1:
            unpainted_index = self._chain.dataframe.index.get_level_values(-1).tolist()
        else:
            unpainted_index = self._chain.dataframe.columns.get_level_values(-1).tolist()
        if not self._chain.painted:  # Paint if not painted
            self._chain.toggle_labels()
        if self._chain.array_style == -1:
            painted_index = self._chain.dataframe.index.get_level_values(-1).tolist()
        else:
            painted_index = self._chain.dataframe.columns.get_level_values(-1).tolist()

        return zip(unpainted_index, painted_index)

    def _select_crossbreak(self):
        """
        Takes self._chain.dataframe and returns only the columns stated in self.crossbreak
        :return:
        """

        cell_items = self._chain.cell_items.split('_')

        if not self.is_grid_summary:
            # Keep only requested columns
            if self._chain.painted: # UnPaint if painted
                self._chain.toggle_labels()

            all_columns = self._chain.dataframe.columns.get_level_values(0).tolist() # retrieve a list of the not painted column values for outer level
            if self._chain.axes[1].index(BASE_COL) == 0:
                all_columns[0] = BASE_COL # Need '@' as the outer column label

            column_selection = []
            for cb in self.crossbreak:
                column_selection = column_selection + (get_indexes_from_list(all_columns, cb))

            if not self._chain.painted: # Paint if not painted
                self._chain.toggle_labels()

            all_columns = self._chain.dataframe.columns.get_level_values(0).tolist() # retrieve a list of painted column values for outer level

            col_qtexts = [all_columns[x] for x in column_selection] # determine painted column values for requested crossbreak
            self.crossbreak_qtext = uniquify(col_qtexts) # Save q text for crossbreak in class atribute

            # Slice the dataframes columns based on requested crossbreaks
            df = self._chain.dataframe.iloc[:, column_selection]

            if len(cell_items) > 1:
                df = fill_index_labels(df)

        else:
            if len(cell_items) > 1:
                cell_contents = self._chain.describe()
                rows = [k for k, va in cell_contents.items()
                        if any(pct in v for v in va for pct in PCT_TYPES)]
                df_filled = fill_index_labels(fill_column_values(self._chain.dataframe))
                df = df_filled.iloc[rows, :]
                #for index in base_indexes:
                #    base_values = self.chain.dataframe.iloc[rows_bad, index].values
                #    base_column = self.chain.dataframe.columns[index]
                #    df.loc[:,[base_column]] = base_values
            else:
                df = self._chain.dataframe

        df_rounded = np.around(df, decimals=self._decimals, out=None)
        return df_rounded

    @property
    def ybase_values(self):
        if not hasattr(self, "_ybase_values"):
            self._ybase_values=[x[1] for x in self.ybases]
        return self._ybase_values

    @property
    def ybase_value_labels(self):
        if not hasattr(self, "_ybase_value_labels"):
            self._ybase_value_labels=[x[0] for x in self.ybases]
        return self._ybase_value_labels

    @property
    def ybase_test_labels(self):
        if not hasattr(self, "_ybase_test_labels"):
            if self.is_grid_summary:
                self._ybase_test_labels = None
                return None
            self._ybase_test_labels=[x[2] for x in self.ybases]
        return self._ybase_test_labels

    def add_test_letter_to_column_labels(self, sep=" ", prefix=None, circumfix='()'):

        # Checking input
        if circumfix is None:
            circumfix = list(('',) * 2)
        else:
            if not isinstance(circumfix, str) or len(circumfix) <> 2:
                raise TypeError("Parameter circumfix needs a string with length 2")
            circumfix = list(circumfix)

        str_parameters = ['sep', 'prefix']
        for i in str_parameters:
            if not isinstance(eval(i), (str, type(None))):
                raise TypeError("Parameter {} must be a string".format(i))

        if self.is_grid_summary:
            pass

        else:

            column_labels = self.chain_df.columns.get_level_values('Values')

            # Edit labels
            new_labels_list = {}
            for x, y in zip(column_labels, self.ybase_test_labels):
                new_labels_list.update({x: x + (sep or '') + circumfix[0] + (prefix or '') + y + circumfix[1]})

            self.chain_df = self.chain_df.rename(columns=new_labels_list)

    def place_vals_in_labels(self, base_position=0, orientation='side', values=None, sep=" ", prefix="n=", circumfix="()", setup='if_differs'):
        """
        Takes values from a given column or row and inserts it to the df's row or column labels.
        Can be used to insert base values in side labels for a grid summary
        :param
        base_position: Int, Default 0
            Which row/column to pick the base element from
        orientation: Str: 'side' or 'column', Default 'side'
            Add base to row or column labels.
        values: list
            the list of values to insert
        sep: str
            the string to use to separate the value from the label
        prefix: str
            A string to insert as a prefix to the label
        circumfix: str
            A character couple to surround the value
        setup: str
            A string telling when to insert value ('always', 'if_differs', 'never')
        """
        if setup=='never': return

        # Checking input
        if circumfix is None:
            circumfix = list(('',) * 2)
        else:
            if not isinstance(circumfix, str) or len(circumfix) <> 2:
                raise TypeError("Parameter circumfix needs a string with length 2")
            circumfix = list(circumfix)

        str_parameters = ['sep', 'prefix', 'orientation', 'setup']
        for i in str_parameters:
            if not isinstance(eval(i), (str, type(None))):
                raise TypeError("Parameter {} must be a string".format(i))

        valid_orientation = ['side', 'column']
        if orientation not in valid_orientation:
            raise ValueError("Parameter orientation must be either of {}".format(valid_orientation))

        valid_setup  = ['always', 'if_differs', 'never']
        if setup not in valid_setup:
            raise ValueError("Parameter setup must be either of {}".format(valid_setup))

        if self.is_grid_summary:
            if (len(uniquify(self.ybase_values))>1 and setup=='if_differs') or setup=='always':

                # grab row labels
                index_labels = self.chain_df.index.get_level_values(-1)

                # Edit labels
                new_labels_list = {}
                for x, y in zip(index_labels, values):
                    new_labels_list.update({x: x + (sep or '') + circumfix[0]+ (prefix or '') + str(y) + circumfix[1]})

                self.chain_df = self.chain_df.rename(index=new_labels_list)
                self.vals_in_labels = True

        else:

            # grab row labels
            index_labels = self.chain_df.columns.get_level_values('Values')

            # Edit labels
            new_labels_list = {}
            for x, y in zip(index_labels, values):
                new_labels_list.update({x: x + (sep or '') + circumfix[0] + (prefix or '') + str(y) + circumfix[1]})

            # Saving column index for level 'Question' in case it accidentially gets renamed
            index_level_values = self.chain_df.columns.get_level_values('Question')

            self.chain_df = self.chain_df.rename(columns=new_labels_list)

            # Returning column index for level 'Question' in case it got renamed
            self.chain_df.columns.set_levels(index_level_values, level='Question', inplace=True)

            self.vals_in_labels = True

    @property
    def base_text(self):
        return self._base_text

    @base_text.setter
    def base_text(self, base_text):
        self._base_text = base_text

    def set_base_text(self, base_value_circumfix="()", base_label_suf=":", base_description_suf=" - ", base_value_label_sep=", ", base_label=None):
        """
        Returns the full base text made up of base_label, base_description and ybases, with some delimiters
        :param
            base_value_circumfix: chars to surround the base value
            base_label_suf: char to put after base_label
            base_description_suf: When more than one column, use this char after base_description
            base_value_label_sep: char to separate column label, if more than one
            base_label: str adhoc to use for base label
        :return:
        """
        # Checking input
        if base_value_circumfix is None:
            base_value_circumfix = list(('',) * 2)
        else:
            if not isinstance(base_value_circumfix, str) or len(base_value_circumfix) <> 2:
                raise TypeError("Parameter base_value_circumfix needs a string with length 2")
            base_value_circumfix = list(base_value_circumfix)

        str_parameters = ['base_label_suf', 'base_description_suf', 'base_value_label_sep', 'base_label']
        for i in str_parameters:
            if not isinstance(eval(i), (str, type(None))):
                raise TypeError("Parameter {} must be a string".format(i))

        # Base_label
        if base_label is None:
            base_label = self.xbase_label

        if self.base_description:
            base_label = u"{}{}".format(base_label,base_label_suf or '')
        else:
            base_label = u"{}".format(base_label)

        # Base_values
        if self.xbase_indexes:
            base_values = self.ybase_values[:]
            for index, base in enumerate(base_values):
                base_values[index] = u"{}{}{}".format(base_value_circumfix[0], base, base_value_circumfix[1])
        else:
            base_values=[""]

        # Base_description
        base_description = ""
        if self.base_description:
            if len(self.ybases) > 1 and not self.vals_in_labels and self.array_style==-1:
                base_description = u"{}{}".format(self.base_description, base_description_suf or '')
            else:
                base_description = u"{} ".format(self.base_description)

        # ybase_value_labels
        base_value_labels = self.ybase_value_labels[:]

        # Include ybase_value_labels in base values if more than one base value
        base_value_text = ""
        if base_value_label_sep is None: base_value_label_sep = ''
        if len(base_values) > 1:
            if not self.vals_in_labels:
                if self.xbase_indexes:
                    for index, label in enumerate(zip(base_value_labels, base_values)):
                        base_value_text=u"{}{}{} {}".format(base_value_text, base_value_label_sep, label[0], label[1])
                    base_value_text = base_value_text[len(base_value_label_sep):]
                else:
                    for index, label in enumerate(base_value_labels):
                        base_value_text=u"{}{}{}".format(base_value_text, base_value_label_sep, label)
                    base_value_text = base_value_text[len(base_value_label_sep):]
            else:
                if not self.is_grid_summary:
                    base_value_text = u"({})".format(self.xbase_count)

        # Final base text
        if not self.is_grid_summary:
            if len(self.ybases) == 1:
                if base_description:
                    base_text = u"{} {}{}".format(base_label,base_description,base_values[0])
                else:
                    base_text = u"{} {}".format(base_label, base_values[0])
            else:
                if base_description:
                    base_text = u"{} {}{}".format(base_label,base_description,base_value_text)
                else:
                    base_text = u"{} {}".format(base_label,base_value_text)
        else: # Grid summary
            if len(uniquify(self.ybase_values)) == 1:
                if base_description:
                    base_text = u"{} {}{}".format(base_label,base_description,base_values[0])
                else:
                    base_text = u"{} {}".format(base_label, base_values[0])
            else:
                if base_description:
                    base_text = u"{} {}".format(base_label, base_description)
                else:
                    base_text = ""

        self._base_text = base_text

    def _check_crossbreaks(self, crossbreaks):
        """
        Checks for existence of the requested crossbreaks
        :param crossbreaks:
        :return:
        """
        if not isinstance(crossbreaks, list):
            crossbreaks = [crossbreaks]

        if not self.is_grid_summary:
            for cb in crossbreaks[:]:
                if cb not in self._chain.axes[1]:
                    crossbreaks.remove(cb)
                    if self.verbose:
                        msg = 'Requested crossbreak: \'{}\' is not found for chain \'{}\' and will be ignored'.format(cb, chain.name)
                        warnings.warn(msg)
            if crossbreaks == []: crossbreaks = None
        else:
            pass # just ignore checking if Grid Summary
            #crossbreaks = None

        return uniquify(crossbreaks) if crossbreaks is not None else [BASE_COL]

    def _get_short_question_name(self):
        """
        Retrieves question name
        :param
            chain: the chain instance
        :return: question_name (as string)
        """
        if not self.is_grid_summary: # Not grid summary
            if self.is_mask_item: # Is grid slice
                pattern = '(?<=\[\{).*(?=\}\])'
                result_list = re.findall(pattern, self.x_key_name)
                if result_list:
                    return result_list[0] # TODO Hmm what if grid has more than one level
                else:
                    return self.x_key_name

            else: # Not grid slice
                return self.x_key_name

        else: # Is grid summary
            find_period = self.x_key_name.find('.')
            if find_period > -1:
                return self.x_key_name[:find_period]
            else:
                return self.x_key_name

    def get_question_text(self, include_varname=False):
        """
        Retrieves the question text from the dataframe.
        Assumes that self.chain_df has one of the following setups  regarding question name self._var_name_in_qtext:
            False:  No question name included in question text
            True:   Question text included in question text, mask items has short question name included.
            'Full': Question text included in question text, mask items has full question name included.

        :param
            include_varname: Include question name in question text (bool)
        :return: question_txt (as string)
        """

        # Get variable name
        var_name = self.x_key_name
        if self.is_mask_item:
            if self._var_name_in_qtext == True:
                var_name = self.x_key_short_name

        # Get question text, stripped for variable name
        question_text = self.chain_df.index[0][0]
        if self._var_name_in_qtext:
            question_text = question_text[len(var_name) + 2:]

        # Include the full question text for mask items if missing
        if self.is_mask_item:
            question_text = self._mask_question_text(question_text)

        # Add variable name to question text if requested
        if include_varname:
            question_text = u'{}. {}'.format(self.x_key_short_name, question_text)

        # Remove consecutive line breaks and spaces
        question_text = re.sub('\n+', '\n', question_text)
        question_text = re.sub('\r+', '\r', question_text)
        question_text = re.sub(' +', ' ', question_text)

        return question_text.strip()

    def _mask_question_text(self, question_text):
        """
        Adds to a mask items question text the array question text
        if not allready there
        :param
            question_text: the question text from the mask item
        :return:
            question_text appended the array question text
        """
        if self.source == "native":
            meta=self._chain._meta
            cols = meta['columns']
            masks = meta['masks']
            if self.is_mask_item:
                parent = cols[self.x_key_name]['parent'].keys()[0].split('@')[-1]
                m_text = masks[parent]['text']
                text = m_text.get('x edit', m_text).get(meta['lib']['default text'])
                if not text.strip() in question_text:
                    question_text = u'{} - {}'.format(text, question_text)

        return question_text

    def _is_base_row(self, row):
        """
        Return True if Row is a Base row
        :param
            row: The row to check (list)
        :return:
            True or False
        """
        for item in BASE_ROW:
            if item not in row:
                return False
        return True

    def _get_y_bases(self):
        """
        Retrieves the base label and base size from the dataframe
        :param chain: the chain instance
        :return: ybases - list of tuples [(base label, base size)]
        """

        base_index = self.xbase_index

        if not self.is_grid_summary:

            # Construct a list of tuples with (base label, base size, test letter)
            base_values = self.chain_df.iloc[base_index, :].values.tolist()
            base_values = np.around(base_values, decimals=self._decimals).tolist()
            base_values = float2String(base_values)
            base_labels = list(self.chain_df.columns.get_level_values('Values'))
            if self._chain.sig_levels:
                base_test   = list(self.chain_df.columns.get_level_values('Test-IDs'))
                bases = zip(base_labels, base_values, base_test)
            else:
                bases = zip(base_labels, base_values)

        else: # Array summary
            # Find base columns

            # Construct a list of tuples with (base label, base size)
            base_values = self.chain_df.T.iloc[base_index,:].values.tolist()
            base_values = np.around(base_values, decimals=self._decimals).tolist()
            base_values = float2String(base_values)
            base_labels = list(self.chain_df.index.get_level_values(-1))
            bases = zip(base_labels, base_values)

        #print ybases
        return bases

    def prepare_dataframe(self):
        """
        Prepares the dataframe for charting, that is takes self.chain_df and
        removes all outer levels and prepares the dataframe for PptxPainter.
        :return: copy of chain.dataframe containing only rows and cols that are to be charted
        """

        # Strip outer level
        df = strip_levels(self.chain_df, rows=0, columns=0)
        df = strip_levels(df, columns=1)

        # Strip HTML TODO Is 'Strip HTML' at all nessecary?

        # Check that the dataframe is numeric
        all_numeric = all(df.applymap(lambda x: isinstance(x, (int, float)))) == True
        if not all_numeric:
            df = as_numeric(df)

        # For rows that are type '%' divide by 100
        indexes = []
        cell_contents = self._chain.describe()
        if self.is_grid_summary:
            colpct_row = min([k for k, va in cell_contents.items()
                              if any(pct in v for v in va for pct in PCT_TYPES)])
            cell_contents = cell_contents[colpct_row]

        for i, row in enumerate(cell_contents):
            for type in row:
                for pct_type in PCT_TYPES:
                    if type == pct_type:
                        indexes.append(i)
        if not self.is_grid_summary:
            df.iloc[indexes] /= 100
        else:
            df.iloc[:, indexes] /= 100

        # Make a PptxDataFrame instance
        chart_df = PptxDataFrame(df,cell_contents,self.array_style,None)
        # Choose a basic Chart type that will fit dataframe TODO Move this to init of Class PptxDataFrame
        chart_df.chart_type = auto_charttype(df, self.array_style)

        return chart_df

